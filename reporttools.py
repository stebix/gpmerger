"""
Tooling for command line reporting of file results.

@js 2023
"""
import re

from datetime import datetime
from pathlib import Path
from rich.table import Table
from rich.tree import Tree

from filetools import FileInfo


TIMESTAMP_FORMAT: str = '%y-%m-%d :: %H:%M:%S'

byte = re.compile('[bB]')
kilo = re.compile('[kK]i?[bB]')
mega = re.compile('[mM]i?[bB]')
giga = re.compile('[gG]i?[bB]')

patterns = {byte : 0, kilo : 1, mega : 2, giga: 3}



def format_unit(unit: str, /) -> str:
    last = len(unit) - 1
    elements = [
        char.upper() if i == 0 or i == last else char.lower()
        for i, char in enumerate(unit)
    ]
    return ''.join(elements)
        

def get_scaling(unit: str, /) -> int:
    """
    Retrieve the scaling factor by interpreting the unit string.
    Intended for use with numbers of 'byte'.
    """
    for pattern, exponent in patterns.items():
        match_result = pattern.match(unit)
        if match_result:
            break
    else:
        raise ValueError(f'invalid unit specification: \'{unit}\'')
    
    span = match_result.span()
    length = span[-1] - span[0]
    base = 1000 if length == 2 else 1024
    return base ** exponent
    
    
def format_bytecount(bytecount: int, unit: str = 'GiB') -> str:
    factor = get_scaling(unit)
    value = bytecount / factor
    return f'{value:.2f} {format_unit(unit)}'



def build_tree_report(accumulated_result: dict[str, list[FileInfo]],
                      source: str | Path,
                      size_unit: str = 'GB',
                      timestamp: str | None = None) -> Tree:
    """
    Build a report of the to-merge files in tree-like format.
    """
    if not timestamp:
        timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    base = Tree(f'Summary for directory: [yellow italic]\'{source}\'[/yellow italic] @ {timestamp}')
    for filenumber, subfiles in accumulated_result.items():
        branch = base.add(f'🗄️ stem file [bold green]{filenumber} [/bold green]')

        for subfile in subfiles:
            branch.add(f'🎞️ {subfile.chapter} :: {format_bytecount(subfile.size, unit=size_unit)}')
    
    return base


def build_table_report(accumulated_result: dict[str, list[FileInfo]],
                       source: str | Path,
                       size_unit: str = 'GB',
                       timestamp: str | None = None) -> Table:
    """
    Build a report of the to-merge files in tabular format.
    """
    if not timestamp:
        timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    table = Table(title=f'Summary for directory: [yellow italic]\'{source}\'[/yellow italic] @ {timestamp}',
                  header_style='bold', width=100)
    # build basal layout
    table.add_column('Stem Filenumber', style='cyan', header_style='bold cyan')
    table.add_column('Chapters', style='green', header_style='bold green')
    table.add_column('Cumulative Size', style='magenta', header_style='bold magenta')

    cumsize = 0
    files = len(accumulated_result)
    min_chapters = float('+inf')
    max_chapters = float('-inf')

    for filenumber, subfiles in accumulated_result.items():
        min_chapters = len(subfiles) if len(subfiles) < min_chapters else min_chapters
        max_chapters = len(subfiles) if len(subfiles) > max_chapters else max_chapters
        chapters = ' '.join(str(subfile.chapter) for subfile in subfiles)
        size = sum(subfile.size for subfile in subfiles)
        cumsize += size
        table.add_row(
            str(filenumber), str(chapters), format_bytecount(size, unit=size_unit)
        )

    table.add_section()

    table.add_row(f'{files} stem files',
                  f'{min_chapters} to {max_chapters} chapters',
                  f'{format_bytecount(cumsize, unit=size_unit)}')

    return table