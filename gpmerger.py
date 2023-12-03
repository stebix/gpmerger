import sys
import argparse
import warnings
import logging

from collections.abc import Iterable
from datetime import datetime
from pathlib import Path

from rich.console import Console

# logging setup - do this before importing other custom modules to correctly process 
# log messages
from logtools import DEFAULT_FORMAT, deduce_loglevel

logger = logging.getLogger('main')
handler = logging.StreamHandler()

formatter = logging.Formatter(fmt=DEFAULT_FORMAT)

loglevel = deduce_loglevel()

logger.setLevel(loglevel)
handler.setLevel(loglevel)

handler.setFormatter(formatter)
logger.addHandler(handler)

# deferred importing due to logging setup
from concattools import ConcatBackend, concatenate_bulk
from filetools import crawl, parse_filepath, accumulate_filenumberwise
from reporttools import TIMESTAMP_FORMAT, build_table_report, build_tree_report


def create_root() -> argparse.ArgumentParser:
    """Create entrypoint root parser."""
    parser = argparse.ArgumentParser(prog='MP4 File merger',
                                     usage='CLI utility to merge chaptered GoPro MP4 video files with gyroscopic metadata streams.')
    
    parser.add_argument('source', type=str, help='Source directory that will be crawled for chaptered GoPro MP4 files.')
    parser.add_argument('target', type=str, help='Set the target directory for the output files. Creation '
                                                    'of directory will be attempted if not already present.')
    parser.add_argument('-f', '--force', action='store_true', help='Set overwriting behaviour for output file.')
    parser.add_argument('-y', '--yes', action='store_true', help='Flag to auto-merge all available candidates without further interaction.')
    parser.add_argument('-r', '--report', type=str, choices=['table', 'tree'],
                        help='Set the file content report styling. Defaults to \'table\'.', default='table')
    parser.add_argument('-b', '--backend', choices=['mp4merge', 'ffmpeg'], default='ffmpeg', type=str,
                        help='Set the concatenation backend. Defaults to \'ffmpeg\'.')
    return parser
    

def select_action_cli(console: Console | None) -> bool | list[str]:
    # use specialized print function locally if console object is provided
    if console:
        print = console.print
        fmt_start = '[bold green]'
        fmt_end = '[/bold green]'
    else:
        fmt_start = ''
        fmt_end = ''

    print(f'\nInput (a)bort to exit without action. {fmt_start}Input space-separated filenumber(s) whose chapter are '
            f'concatenated into a monolithic file. Use \'all\' to select all filenumbers.{fmt_end}')
    
    userinput = input()
    userinput = [elem for elem in userinput.split(' ') if not elem.isspace()]

    if 'a' in userinput or 'abort' in userinput:
        if len(userinput) > 1:
            warnings.warn(f'received abort signal in user input with further parameters - '
                            f'ignoring other input: \'{userinput}\'')
        userinput = False

    elif 'all' in userinput:
        if len(userinput) > 1:
            warnings.warn(f'received all-selecting signal in user input with further parameters - '
                            f'ignoring other input: \'{userinput}\'')
        userinput = True

    return userinput


def sieve(candidates: Iterable[str], desired: Iterable[str]) -> dict[str, list[str]]:
    """
    Select a number of desired strings from a number of candidates strings.
    """
    candidates = set(candidates)
    desired = set(desired)

    if 'all' in desired:
        selected = candidates
        deselected = set()
        desired.remove('all')
        futile = desired
    else:
        selected = candidates & desired
        deselected = candidates - desired
        futile = desired - candidates
    
    return {'selected' : list(selected), 'deselected' : list(deselected), 'futile' : list(futile)}


def main():
    """Main CLI entrypoint and logic."""
    console = Console()
    rootparser = create_root()
    args = rootparser.parse_args()

    source = Path(args.source)
    target = Path(args.target)
    backend = ConcatBackend(args.backend)

    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)

    directory_content = crawl(source)
    videopaths = directory_content['video']
    fileinfos = [parse_filepath(p) for p in videopaths]

    accumulated = accumulate_filenumberwise(fileinfos)

    if args.report == 'table':
        build_report = build_table_report
    elif args.report == 'tree':
        build_report = build_tree_report
    else:
        raise ValueError(f'requested invalid report style \'{args.report}\'')

    report = build_report(accumulated, source=source, size_unit='GB',
                            timestamp=timestamp)
    console.print('')
    console.print(report)

    if args.yes:
        timedelta, result = concatenate_bulk(accumulated, target_directory=target,
                                             backend=backend, console=console)
        
    else:
        userinput = select_action_cli(console=console)

        if userinput is False:
            sys.exit('Aborting merging process')
        elif userinput is True:
            filenumbers = accumulated.keys()
        else:
            filenumbers = userinput

        sieveresult = sieve(candidates=accumulated.keys(), desired=filenumbers)
        # pretty report about the results
        selected = sieveresult['selected']
        deselected = sieveresult['deselected']
        futile = sieveresult['futile']
        console.rule(title=f'Selection Overview')
        console.print(f'[green]Selected filenumbers: [bold]{selected}[/bold][/green]')
        console.print(f'[light_coral]Deselected filenumbers: [bold]{deselected}[/bold][/light_coral]')
        console.print(f'[yellow]Futile input filenumbers: [bold]{futile}[/bold][/yellow]')

        accumulated_selected = {key : accumulated[key] for key in selected}
        timedelta, result = concatenate_bulk(accumulated_selected, target_directory=target,
                                                backend=backend, console=console)
    
    console.rule(title=f'Summary')
    console.print(f'Total duration: {timedelta}')

    return None



if __name__ == '__main__':
    main()
