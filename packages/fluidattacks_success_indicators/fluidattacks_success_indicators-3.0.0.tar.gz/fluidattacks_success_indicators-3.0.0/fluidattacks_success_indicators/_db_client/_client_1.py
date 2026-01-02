import inspect
from dataclasses import (
    dataclass,
)
from datetime import (
    datetime,
)

from fa_purity import (
    Cmd,
    FrozenDict,
    FrozenList,
    FrozenTools,
    Result,
    ResultE,
    ResultFactory,
    cast_exception,
)
from fa_purity.json import (
    JsonPrimitiveUnfolder,
    Primitive,
)
from fluidattacks_etl_utils.bug import (
    Bug,
)
from fluidattacks_etl_utils.typing import (
    Dict,
    TypeVar,
)
from redshift_client.sql_client import (
    DbPrimitiveFactory,
    QueryValues,
    RowData,
)
from snowflake_client import (
    SnowflakeCursor,
    SnowflakeQuery,
)

from ._core import (
    Client,
    JobLastSuccess,
    JobName,
)

_T = TypeVar("_T")


def _require_index(items: FrozenList[_T], index: int) -> ResultE[_T]:
    factory: ResultFactory[_T, Exception] = ResultFactory()
    try:
        return factory.success(items[index])
    except IndexError as err:
        return factory.failure(err)


def _decode_job_success(raw: RowData) -> ResultE[JobLastSuccess]:
    _job = _require_index(raw.data, 0).bind(
        lambda p: p.map(
            lambda j: JsonPrimitiveUnfolder.to_str(j),
            lambda _: Result.failure(TypeError("Expected `str` but got `datetime`"), str).alt(
                cast_exception,
            ),
        ),
    )
    _success_at = _require_index(raw.data, 1).bind(
        lambda p: p.map(
            lambda _: Result.failure(
                TypeError("Expected `datetime` but got `JsonPrimitive`"),
                datetime,
            ).alt(cast_exception),
            lambda d: Result.success(d, Exception),
        ),
    )
    return _job.bind(lambda j: _success_at.map(lambda d: JobLastSuccess(j, d)))


def _assert_one(items: FrozenList[_T]) -> ResultE[_T]:
    if len(items) == 1:
        return Result.success(items[0])
    return Result.failure(Exception(ValueError(f"Expected one item; got {len(items)}")))


def _assert_bool(raw: RowData) -> ResultE[bool]:
    factory: ResultFactory[bool, Exception] = ResultFactory()
    return _require_index(raw.data, 0).bind(
        lambda p: p.map(
            JsonPrimitiveUnfolder.to_bool,
            lambda _: factory.failure(TypeError("expected `bool` but got `datetime`")),
        ),
    )


def _query_values(items: Dict[str, Primitive]) -> QueryValues:
    return QueryValues(DbPrimitiveFactory.from_raw_prim_dict(FrozenTools.freeze(items)))


@dataclass(frozen=True)
class _Client1:
    _sql: SnowflakeCursor
    _schema: str
    _table: str
    _name_column: str

    @property
    def _common_identifiers(self) -> FrozenDict[str, str]:
        identifiers = {
            "schema": self._schema,
            "table": self._table,
            "name_column": self._name_column,
        }
        return FrozenTools.freeze(identifiers)

    def get_job(self, job_name: JobName) -> Cmd[JobLastSuccess]:
        statement = """
            SELECT {name_column}, sync_date FROM {schema}.{table}
            WHERE {name_column}=%(job_name)s
        """
        query = Bug.assume_success(
            "get_job_query",
            inspect.currentframe(),
            (),
            SnowflakeQuery.dynamic_query(statement, self._common_identifiers),
        )
        args: Dict[str, Primitive] = {
            "job_name": job_name.raw,
        }
        return self._sql.execute(query, _query_values(args)).map(
            lambda r: Bug.assume_success("get_job", inspect.currentframe(), (str(job_name),), r),
        ) + self._sql.fetch_all.map(
            lambda r: Bug.assume_success(
                "get_job_fetch",
                inspect.currentframe(),
                (str(job_name),),
                r,
            ),
        ).map(
            lambda x: Bug.assume_success(
                "get_job_decode",
                inspect.currentframe(),
                (str(job_name),),
                _assert_one(x).bind(_decode_job_success),
            ),
        )

    def job_exist(self, job_name: JobName) -> Cmd[bool]:
        statement = """
            SELECT EXISTS (
                SELECT 1 FROM {schema}.{table}
                WHERE {name_column}=%(job_name)s
            )
        """
        query = Bug.assume_success(
            "job_exist_query",
            inspect.currentframe(),
            (),
            SnowflakeQuery.dynamic_query(statement, self._common_identifiers),
        )
        args: Dict[str, Primitive] = {
            "job_name": job_name.raw,
        }
        return self._sql.execute(query, _query_values(args)).map(
            lambda r: Bug.assume_success("job_exist", inspect.currentframe(), (str(job_name),), r),
        ) + self._sql.fetch_one.map(
            lambda r: Bug.assume_success(
                "job_exist_fetch",
                inspect.currentframe(),
                (str(job_name),),
                r,
            ),
        ).map(
            lambda m: Bug.assume_success(
                "job_exist_decode_row",
                inspect.currentframe(),
                (str(job_name),),
                m.to_result(),
            ),
        ).map(
            lambda m: Bug.assume_success(
                "job_exist_decode",
                inspect.currentframe(),
                (str(job_name),),
                _assert_bool(m),
            ),
        )

    def _new_timestamp_job(self, job_name: JobName) -> Cmd[None]:
        statement = """
            INSERT INTO {schema}.{table}
            ({name_column}, sync_date) VALUES
            (%(job_name)s, getdate())
        """
        query = Bug.assume_success(
            "_new_timestamp_job_query",
            inspect.currentframe(),
            (),
            SnowflakeQuery.dynamic_query(statement, self._common_identifiers),
        )
        args: Dict[str, Primitive] = {
            "job_name": job_name.raw,
        }
        return self._sql.execute(query, _query_values(args)).map(
            lambda r: Bug.assume_success(
                "_new_timestamp_job",
                inspect.currentframe(),
                (str(job_name),),
                r,
            ),
        )

    def _update_job(self, job_name: JobName) -> Cmd[None]:
        statement = """
            UPDATE {schema}.{table}
            set sync_date=getdate() WHERE {name_column}=%(job_name)s
        """
        query = Bug.assume_success(
            "_update_job_query",
            inspect.currentframe(),
            (),
            SnowflakeQuery.dynamic_query(statement, self._common_identifiers),
        )
        args: Dict[str, Primitive] = {
            "job_name": job_name.raw,
        }
        return self._sql.execute(query, _query_values(args)).map(
            lambda r: Bug.assume_success(
                "_update_job",
                inspect.currentframe(),
                (str(job_name),),
                r,
            ),
        )

    def upsert(self, job_name: JobName) -> Cmd[None]:
        return (
            self.job_exist(job_name)
            .map(lambda b: self._update_job if b else self._new_timestamp_job)
            .bind(lambda f: f(job_name))
        )


SCHEMA = "last_update"


def new_job_client(cursor: SnowflakeCursor) -> Client:
    client = _Client1(cursor, SCHEMA, "jobs", "job_name")
    return Client(client.get_job, client.upsert)


def new_compound_job_client(cursor: SnowflakeCursor, table: str) -> Client:
    client = _Client1(cursor, SCHEMA, table, "group_name")
    return Client(client.get_job, client.upsert)
