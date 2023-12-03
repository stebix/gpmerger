"""
Tooling for crawling, parsing and sorting the video files from the file system.

@js 2023
"""
import os
import dataclasses
import logging
import warnings

from collections import defaultdict
from collections.abc import Iterable
from functools import cached_property
from pathlib import Path


VIDEO_SUFFIXES = {'.mp4'}
THUMBNAIL_SUFFIXES = {'.thm'}


def crawl(directory: Path) -> dict[str, list[Path]]:
    """Crawl the directory and sort results into three categories."""
    crawlresult = defaultdict(list)
    for item in directory.iterdir():
        if not item.is_file():
            crawlresult['unrecognized'].append(item)
            continue
        if item.suffix.lower() in VIDEO_SUFFIXES:
            crawlresult['video'].append(item)
        elif item.suffix.lower() in THUMBNAIL_SUFFIXES:
            crawlresult['thumbnail'].append(item)
        else:
            crawlresult['unrecognized'].append(item)

    video_count = len(crawlresult['video'])
    thumbnail_count = len(crawlresult['thumbnail'])
    unrecognized_count = len(crawlresult['unrecognized'])
    logging.info(f'Crawling {directory} returned {video_count} video files, '
                 f'{thumbnail_count} thumbnails and {unrecognized_count} unrecognized items.')
    return crawlresult



@dataclasses.dataclass
class FileInfo:
    prefix: str
    codec: str
    chapter: str
    number: str
    suffix: str
    path: str | Path | None = None

    @cached_property
    def size(self) -> int:
        """Return the size of the file in bytes."""
        return os.path.getsize(self.path)



def parse_filename(name: str, /) -> dict[str, str]:
    """
    Parse a GoPro video file name into its constituent parts.

    Issues warnings on unexpected component values.


    Parameters
    ----------

    name : str
        GoPro video file name.
    
        
    Returns
    -------

    info : dict
        Parsed file information.
    """
    prefix, codec, *stem = name

    chapter = ''.join(stem[0:2])
    number = ''.join(stem[2:6])
    suffix = ''.join(stem[6:])

    if prefix != 'G':
        warnings.warn(f'expected prefix \'G\' but got \'{prefix}\'')

    if codec not in {'H', 'X'}:
        warnings.warn(f'expected codec \'H\' (AVC) or \'X\' (HEVC) but got {codec}')

    if not suffix.lower().endswith('mp4'):
        warnings.warn(f'expected suffix \'MP4\' but got \'{suffix}\'')

    return {'prefix' : prefix, 'codec' : codec, 'chapter' : chapter,
            'number' : number, 'suffix' : suffix}



def parse_filepath(path: Path) -> dict[str, str | Path]:
    if not path.exists():
        warnings.warn(f'video file at "{path.resolve()}" does not exist')
    raw_fileinfo = {**parse_filename(path.name), 'path' : path}
    fileinfo = FileInfo(**raw_fileinfo)
    return fileinfo



def accumulate_filenumberwise(fileinfos: Iterable[FileInfo], /) -> dict[str, list[FileInfo]]:
    """
    Accumulate file information objects with identical file number (but possibly differing chapter)
    to retrieve lists of file information objects that correspond to single recordings.
    """
    accumulated_fileinfos = defaultdict(list)
    for fileinfo in fileinfos:
        accumulated_fileinfos[fileinfo.number].append(fileinfo)
    
    for chapters in accumulated_fileinfos.values():
        chapters.sort(key=lambda elem: int(elem.chapter))
    
    return accumulated_fileinfos