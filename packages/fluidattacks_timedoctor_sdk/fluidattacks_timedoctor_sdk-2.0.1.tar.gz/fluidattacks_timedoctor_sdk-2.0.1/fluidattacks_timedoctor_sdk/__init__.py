import logging

from fa_purity import (
    Unsafe,
)

from ._logger import (
    set_logger,
)

__version__ = "2.0.1"

Unsafe.compute(set_logger(__name__, __version__))
LOG = logging.getLogger(__name__)
