from fa_purity import Cmd, Result
from fluidattacks_connection_manager import ConnectionConf
from fluidattacks_etl_utils.typing import TypeVar
from snowflake_client import (
    ConnectionFactory,
    SnowflakeConnection,
    SnowflakeCredentials,
    SnowflakeDatabase,
    SnowflakeWarehouse,
)

_F = TypeVar("_F")


def new_snowflake_connection(
    creds: SnowflakeCredentials,
    conf: ConnectionConf,
) -> Cmd[Result[SnowflakeConnection, _F]]:
    return ConnectionFactory.snowflake_connection(
        SnowflakeDatabase(conf.database.value),
        SnowflakeWarehouse(conf.warehouse.value),
        SnowflakeCredentials(
            user=creds.user,
            private_key=creds.private_key,
            account=creds.account,
        ),
    ).map(lambda c: Result.success(c))
