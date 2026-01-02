import inspect

from fa_purity import (
    Cmd,
    Result,
)
from fluidattacks_connection_manager import (
    ConnectionConf,
    ConnectionManagerFactory,
    Databases,
    DbClients,
    Roles,
    Warehouses,
)
from fluidattacks_etl_utils.bug import (
    Bug,
)
from fluidattacks_etl_utils.typing import (
    Callable,
    TypeVar,
)
from snowflake_client import SnowflakeCredentials

_T = TypeVar("_T")
_F = TypeVar("_F")


def with_observes_connection(
    process: Callable[[DbClients], Cmd[Result[_T, _F]]],
) -> Cmd[_T]:
    conf = ConnectionConf(
        Warehouses.GENERIC_COMPUTE,
        Roles.ETL_UPLOADER,
        Databases.OBSERVES,
    )
    return (
        ConnectionManagerFactory.observes_manager()
        .map(lambda r: Bug.assume_success("create_manager", inspect.currentframe(), (), r))
        .bind(lambda manager: manager.execute_with_snowflake(process, conf))
        .map(
            lambda r: Bug.assume_success(
                "with_common_connection_process",
                inspect.currentframe(),
                (),
                r,
            ),
        )
    )


def with_custom_connection(
    process: Callable[[DbClients], Cmd[Result[_T, _F]]],
    conf: ConnectionConf,
    creds: SnowflakeCredentials,
) -> Cmd[_T]:
    manager = ConnectionManagerFactory.custom_manager(creds)
    return manager.execute_with_snowflake(process, conf).map(
        lambda r: Bug.assume_success(
            "with_common_connection_process",
            inspect.currentframe(),
            (),
            r,
        ),
    )
