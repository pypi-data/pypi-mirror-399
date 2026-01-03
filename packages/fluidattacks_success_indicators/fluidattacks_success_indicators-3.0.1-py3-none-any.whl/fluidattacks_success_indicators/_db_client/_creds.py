from dataclasses import dataclass

from fa_purity import ResultE
from fa_purity.json import JsonObj, JsonPrimitiveUnfolder, JsonUnfolder, Unfolder
from fluidattacks_etl_utils.secrets import SnowflakeCredentials


@dataclass(frozen=True)
class SnowflakeSecretsConf:
    account_field: str
    private_key_field: str
    user_name: str


def observes_conf() -> SnowflakeSecretsConf:
    return SnowflakeSecretsConf(
        account_field="SNOWFLAKE_ACCOUNT",
        private_key_field="SNOWFLAKE_ETL_PRIVATE_KEY",
        user_name="ETL_USER",
    )


def decode_snowflake_creds(
    conf: SnowflakeSecretsConf,
    raw: JsonObj,
) -> ResultE[SnowflakeCredentials]:
    _account = JsonUnfolder.require(raw, conf.account_field, Unfolder.to_primitive).bind(
        JsonPrimitiveUnfolder.to_str,
    )
    _key = JsonUnfolder.require(raw, conf.private_key_field, Unfolder.to_primitive).bind(
        JsonPrimitiveUnfolder.to_str,
    )
    return _account.bind(
        lambda account: _key.map(
            lambda key: SnowflakeCredentials(
                user=conf.user_name,
                private_key=key,
                account=account,
            ),
        ),
    )
