"""Utility functions for HDB Valuation Engine.

This module contains shared utilities including logging configuration
and version information.
"""

from __future__ import annotations

import logging

__version__: str = "0.4.0"


def configure_logging(verbosity: int) -> None:
    """Configure root logger formatting and level.

    Parameters
    ----------
    verbosity : int
        Verbosity level from CLI:
        - 0: WARNING
        - 1: INFO
        - 2+: DEBUG
    """
    level = logging.WARNING
    if verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
