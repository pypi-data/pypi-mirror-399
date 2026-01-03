from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from fa_purity import (
    Cmd,
    Result,
    ResultE,
)

from ._db_client import (
    JobName,
)

ChildJob = JobName


class SingleJob(Enum):
    batch_etl = "batch_etl"
    bugsnag = "bugsnag"
    ce_etl = "ce_etl"
    checkly = "checkly"
    cloudwatch_etl = "cloudwatch_etl"
    compute_bills = "compute_bills"
    delighted = "delighted"
    determine_dynamo_schema = "determine_dynamo_schema"
    flow_etl = "flow_etl"
    gitlab_datahub = "gitlab_datahub"
    gitlab_universe = "gitlab_universe"
    gitlab_dora = "gitlab_dora"
    sorts_lead_scoring = "sorts_lead_scoring"
    timedoctor_backup = "timedoctor_backup"
    timedoctor_etl = "timedoctor_etl"
    zoho_crm_etl = "zoho_crm_etl"
    zoho_crm_prepare = "zoho_crm_prepare"

    @staticmethod
    def decode(raw: str) -> ResultE[SingleJob]:
        try:
            return Result.success(SingleJob(raw))
        except ValueError as err:
            return Result.failure(err)


class CompoundJob(Enum):
    code_upload = "code_upload"
    code_upload_snowflake = "code_upload_snowflake"

    @staticmethod
    def decode(raw: str) -> ResultE[CompoundJob]:
        try:
            return Result.success(CompoundJob(raw))
        except ValueError as err:
            return Result.failure(err)


@dataclass(frozen=True)
class IndicatorsClient:
    update_single_job: Callable[[SingleJob], Cmd[None]]
    update_compound_job: Callable[[CompoundJob, ChildJob], Cmd[None]]
