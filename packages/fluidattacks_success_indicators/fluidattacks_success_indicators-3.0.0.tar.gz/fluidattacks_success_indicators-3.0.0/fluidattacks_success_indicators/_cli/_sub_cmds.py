import inspect

import click
from fa_purity import (
    Cmd,
    Maybe,
    ResultE,
    cast_exception,
)
from fa_purity._core.utils import raise_exception
from fluidattacks_connection_manager import ConnectionConf, Databases, Roles, Warehouses
from fluidattacks_etl_utils import smash
from fluidattacks_etl_utils.bug import Bug
from fluidattacks_etl_utils.typing import (
    NoReturn,
    Tuple,
)
from snowflake_client import SnowflakeCredentials

from fluidattacks_success_indicators._core import CompoundJob, SingleJob
from fluidattacks_success_indicators._db_client import (
    JobName,
)
from fluidattacks_success_indicators._factory import ClientFactory


def _decode_conf(
    raw_warehouse: str | None,
    raw_role: str | None,
    raw_user: str | None,
    raw_account: str | None,
    raw_private_key: str | None,
) -> ResultE[Tuple[ConnectionConf, SnowflakeCredentials]]:
    warehouse = (
        Maybe.from_optional(raw_warehouse)
        .to_result()
        .alt(lambda _: ValueError("missing warehouse"))
        .alt(cast_exception)
        .bind(Warehouses.from_raw)
    )
    role = (
        Maybe.from_optional(raw_role)
        .to_result()
        .alt(lambda _: ValueError("missing role"))
        .alt(cast_exception)
        .bind(Roles.from_raw)
    )
    conf = smash.smash_result_2(
        warehouse,
        role,
    ).map(
        lambda t: ConnectionConf(*t, Databases.OBSERVES),
    )
    user = (
        Maybe.from_optional(raw_user)
        .to_result()
        .alt(lambda _: ValueError("missing user"))
        .alt(cast_exception)
    )
    key = (
        Maybe.from_optional(raw_private_key)
        .to_result()
        .alt(lambda _: ValueError("missing private key"))
        .alt(cast_exception)
    )
    account = (
        Maybe.from_optional(raw_account)
        .to_result()
        .alt(lambda _: ValueError("missing account"))
        .alt(cast_exception)
    )
    creds = smash.smash_result_3(user, key, account).map(lambda t: SnowflakeCredentials(*t))
    return smash.smash_result_2(conf, creds)


@click.command()
@click.option("--job", type=str, required=True)
@click.option("--warehouse", type=str, required=False, envvar="SNOWFLAKE_WAREHOUSE")
@click.option("--role", type=str, required=False, envvar="SNOWFLAKE_ROLE")
@click.option("--user", type=str, required=False, envvar="SNOWFLAKE_USER")
@click.option("--account", type=str, required=False, envvar="SNOWFLAKE_ACCOUNT")
@click.option("--private-key", type=str, required=False, envvar="SNOWFLAKE_PRIVATE_KEY")
def single_job(  # noqa: PLR0913
    job: str,
    warehouse: str | None,
    role: str | None,
    user: str | None,
    account: str | None,
    private_key: str | None,
) -> NoReturn:
    decoded_job = SingleJob.decode(job).alt(raise_exception).to_union()
    if private_key is None:
        cmd: Cmd[None] = ClientFactory.observes_client().update_single_job(decoded_job)
        cmd.compute()
    else:
        conf, creds = Bug.assume_success(
            "_decode_conf",
            inspect.currentframe(),
            (str(warehouse), str(role), str(user), str(account)),
            _decode_conf(warehouse, role, user, account, private_key),
        )
        cmd_2: Cmd[None] = ClientFactory.custom_client(conf, creds).update_single_job(decoded_job)
        cmd_2.compute()


@click.command()
@click.option("--job", type=str, required=True)
@click.option("--child", type=str, required=True)
def compound_job(job: str, child: str) -> None:
    decoded_job = CompoundJob.decode(job).alt(raise_exception).to_union()
    cmd: Cmd[None] = ClientFactory.observes_client().update_compound_job(
        decoded_job,
        JobName(child),
    )
    cmd.compute()
