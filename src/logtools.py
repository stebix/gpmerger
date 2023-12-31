"""
Tooling for logging.

@js 2023
"""
import os
import logging

DEFAULT_FORMAT: str = '%(asctime)s - %(name)s | %(levelname)s : %(message)s'
DEFAULT_LOGLEVEL: int = logging.WARNING

logger_name = '.'.join(('main', __file__))
logger = logging.getLogger(logger_name)

def deduce_loglevel() -> int:
    """Deduce logging level from environment variables."""
    value = os.environ.get('LOGLEVEL', default=None)
    if value:
        loglevel = logging.getLevelName(value.upper())
        logger.debug(f'Deduced loglevel {loglevel} from raw environment variable: \'{value}\'')
    else:
        loglevel = DEFAULT_LOGLEVEL
        logger.debug(f'No loglevel spec found in environment. Using default: \'{DEFAULT_LOGLEVEL}\'')
    return loglevel
