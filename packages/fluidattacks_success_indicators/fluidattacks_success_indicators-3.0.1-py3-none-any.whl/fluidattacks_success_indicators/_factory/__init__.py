import logging
from dataclasses import dataclass

from fa_purity import Cmd, Result
from fluidattacks_connection_manager import (
    ConnectionConf,
    DbClients,
)
from snowflake_client._core import SnowflakeCredentials

from fluidattacks_success_indicators._core import CompoundJob, IndicatorsClient, SingleJob
from fluidattacks_success_indicators._db_client import (
    JobName,
    new_compound_job_client,
    new_job_client,
)

from ._connection import with_custom_connection, with_observes_connection

LOG = logging.getLogger(__name__)

COMPOUND_JOBS_TABLES: dict[CompoundJob, str] = {
    CompoundJob.code_upload: "code_upload",
    CompoundJob.code_upload_snowflake: "code_upload",
}


def _single_job(client: DbClients, job: SingleJob) -> Cmd[None]:
    return (
        client.connection.cursor(LOG)
        .map(new_job_client)
        .bind(lambda d: d.upsert(JobName(job.value)))
    )


def _compound_job(client: DbClients, job: CompoundJob, child: JobName) -> Cmd[None]:
    return client.connection.cursor(LOG).bind(
        lambda sql: new_compound_job_client(sql, COMPOUND_JOBS_TABLES[job]).upsert(child),
    )


@dataclass(frozen=True)
class ClientFactory:
    @staticmethod
    def observes_client() -> IndicatorsClient:
        return IndicatorsClient(
            lambda j: with_observes_connection(
                lambda d: _single_job(d, j).map(lambda x: Result.success(x, Exception)),
            ),
            lambda j, c: with_observes_connection(
                lambda d: _compound_job(d, j, c).map(lambda x: Result.success(x, Exception)),
            ),
        )

    @staticmethod
    def custom_client(conf: ConnectionConf, creds: SnowflakeCredentials) -> IndicatorsClient:
        return IndicatorsClient(
            lambda j: with_custom_connection(
                lambda d: _single_job(d, j).map(lambda x: Result.success(x, Exception)),
                conf,
                creds,
            ),
            lambda j, c: with_custom_connection(
                lambda d: _compound_job(d, j, c).map(lambda x: Result.success(x, Exception)),
                conf,
                creds,
            ),
        )
