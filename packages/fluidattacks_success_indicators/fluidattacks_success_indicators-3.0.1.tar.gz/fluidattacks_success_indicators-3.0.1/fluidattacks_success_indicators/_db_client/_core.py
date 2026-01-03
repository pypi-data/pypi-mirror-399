from __future__ import (
    annotations,
)

from collections.abc import (
    Callable,
)
from dataclasses import (
    dataclass,
)
from datetime import (
    datetime,
)

from fa_purity import (
    Cmd,
)


@dataclass(frozen=True)
class JobLastSuccess:
    job: str
    last_success: datetime


@dataclass(frozen=True)
class JobName:
    raw: str


@dataclass(frozen=True)
class Client:
    get_job: Callable[[JobName], Cmd[JobLastSuccess]]
    upsert: Callable[[JobName], Cmd[None]]
