from fa_purity import (
    Unsafe,
)

from ._core import CompoundJob, IndicatorsClient, SingleJob
from ._factory import ClientFactory
from ._logger import (
    set_logger,
)

__version__ = "3.0.0"

Unsafe.compute(set_logger(__name__, __version__))

__all__ = [
    "ClientFactory",
    "CompoundJob",
    "IndicatorsClient",
    "SingleJob",
]
