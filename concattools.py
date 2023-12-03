"""
Core tooling for concatenation of MP4 files under preservation of
gyroscopic metadata streams.

@js 2023
"""
import enum
import subprocess
import tempfile
import warnings
import logging
import tomllib

from datetime import datetime, timedelta
from collections.abc import Callable, Iterable
from pathlib import Path
from rich.status import Status
from rich.console import Console

from filetools import FileInfo

logger = logging.getLogger('main.concattools')

# load core configuration settings
CONF_PATH = Path('./conf.toml')

assert CONF_PATH.exists(), 'missing required configuration file'
with open(CONF_PATH, mode='rb') as handle:
    CONF = tomllib.load(handle)

FFMPEG_PATH: Path = Path(CONF['binaries']['FFMPEG'])
MP4MERGE_PATH: Path = Path(CONF['binaries']['MP4MERGE'])

logger.debug(f'set \'FFMPEG_PATH\' = \'{FFMPEG_PATH}\'')
logger.debug(f'set \'MP4MERGE_PATH\' = \'{MP4MERGE_PATH}\'')


class ConcatBackend(enum.Enum):
    MP4MERGE = 'mp4merge'
    FFMPEG = 'ffmpeg'


def concatenate_mp4merge(paths: Iterable[Path, str], target: Path | str) -> subprocess.CompletedProcess:
    """
    Concatenate many MP4 files via `mp4merge` utility.
    Should conserve any gyro- and gravitational metadata.
    """
    paths = [str(path) for path in paths]
    retval = subprocess.run(
        [str(MP4MERGE_PATH), *paths, '--out', str(target)]
    )
    return retval


def concatenate_ffmpeg(paths: Iterable[Path, str], target: str | Path) -> subprocess.CompletedProcess:
    """Concatenate MP4 video files with intact metadata via FFMPEG."""
    # Create video file list as temporary file.
    data = [
        f'file \'{str(path)}\'\n'
        for path in paths
    ]
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_handle:
        # write file list into temporary file and jump to beginning
        temp_handle.writelines(data)
        temp_handle.seek(0)
        # run FFMPEG concatenation
        retval = subprocess.run(
            [str(FFMPEG_PATH), '-f', 'concat', '-safe', '0', '-i', temp_handle.name,
             '-c', 'copy', '-map', '0:v', '-map', '0:a', '-map', '0:3', '-copy_unknown', str(target)],
            capture_output=True
        )
    return retval


backend_to_concat_fn: dict[ConcatBackend, Callable] = {
    ConcatBackend.MP4MERGE : concatenate_mp4merge,
    ConcatBackend.FFMPEG : concatenate_ffmpeg
}


def concatenate_files(paths: Iterable[Path, str], target: str | Path,
                      backend: ConcatBackend) -> subprocess.CompletedProcess:
    """
    Concatenate MP4 video files and conserve gyroscopic metadata.
    """
    try:
        concatenate = backend_to_concat_fn[backend]
    except KeyError:
        raise KeyError(f'Invalid file concatenation backend: \'{backend}\'')

    return concatenate(paths=paths, target=target)


def concatenate_bulk(accumulated_result: dict[str, list[FileInfo]],
                     target_directory: str | Path,
                     backend: ConcatBackend = ConcatBackend.FFMPEG,
                     console: Console | None = None,
                     force: bool = False,
                     ) -> tuple[timedelta, list[Path]]:
    """
    Concatenate multiple subfiles to multiple resulting files.

    Parameters
    ----------

    accumulated_results : dict[str, list[FileInfo]]
        Mapping structure indicating the multiple chapter subfiles that should
        be concatenated into a monolithic file.
    
    target_directory : str or Path
        Resulting monolithic files will be stored there. Filenames are deduced
        from stem filenumber.

    backend : ConcatBackend, optional
        Concatenation backend method identifier. Defaults to 'ConcatBackend.FFMPEG'.
    
    console : Console or None, optional
        Specify output console object (`rich` object). Defaults to None, e.g. stdout.

    force : bool, optional
        Set force overwriting behaviour. Defaults to `False`, e.g. no overwriting.
    """
    total = len(accumulated_result)

    target_directory = Path(target_directory)

    if not target_directory.is_dir():
        warnings.warn('indicated target directory is not a directory - attempting to create')
        target_directory.mkdir(parents=True)
    
    prefix = 'concatenated'
    concatenate = backend_to_concat_fn[backend]
    targets: list[Path] = []

    t_start = datetime.now()

    with Status(status='Starting concatenation ...', console=console) as status:
        for i, (filenumber, subfiles) in enumerate(accumulated_result.items(), start=1):
            target = target_directory / f'{prefix}-{filenumber}.mp4'

            if target.exists():
                if force:
                    logger.info(f'overwriting preexisting file with concatenation at \'{target}\'')
                else:
                    logger.warning(f'skipping concatenation with target: \'{target}\' - file exists')
                    continue

            status.update(status=f'Concatenating item [italic yellow]{i}/{total}[/italic yellow] '
                                 f'@[bold green] stem number {filenumber}[/]')
            
            targets.append(target)
            paths = [file.path for file in subfiles]
            process_result = concatenate(paths, target)
            logger.debug(f'successfully concatenated {paths} into {target}')

    delta = datetime.now() - t_start
    return (delta, targets)

