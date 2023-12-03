"""
Tooling for logging.

@js 2023
"""
import os
import logging

DEFAULT_FORMAT: str = '%(asctime)s - %(name)s | %(levelname)s : %(message)s'
DEFAULT_LOGLEVEL: int = logging.WARNING

def deduce_loglevel() -> int:
    """Deduce logging level from environment variables."""
    value = os.environ.get('LOGLEVEL', default=None)
    if value:
        loglevel = logging.getLevelName(value.upper())
    else:
        loglevel = DEFAULT_LOGLEVEL
    return loglevel
