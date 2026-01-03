#!/usr/bin/env python3

# Standard libraries
from argparse import (
    _ArgumentGroup,
    ArgumentParser,
    Namespace,
    RawTextHelpFormatter,
)
from shutil import get_terminal_size
from sys import exit as sys_exit
from typing import List

# Components
from ..package.bundle import Bundle
from ..package.settings import Settings
from ..package.updates import Updates
from ..prints.colors import Colors
from ..system.platform import Platform
from .tools import Tools

# Constants
COMMANDS_DEFAULT: List[str] = [
    'git',
    'status',
    '--short',
    '--untracked-files',
]
HELP_POSITION: int = 23

# Git foreach, pylint: disable=duplicate-code
def git_foreach(
    commands: List[str],
    dry_run: bool = False,
    quiet: bool = False,
    recurse_submodules: bool = True,
) -> int:

    # Variables
    repositories: List[str]
    result: int = 0

    # Tool header
    if not quiet:
        print(' ')
        print(f'{Colors.GREEN} === {Tools.NAME} - Execute commands in Git repositories'
              f'{Colors.RESET}')
        Platform.flush()

    # Detect repositories
    repositories = Tools.git_repositories(submodules=recurse_submodules)
    if not repositories:
        if not quiet:
            print(' ')
            print(
                f'{Colors.YELLOW} {Tools.NAME}:'
                f'{Colors.RED} Could not detect Git repositories under current folder...'
                f'{Colors.RESET}')
            print(' ')
            Platform.flush()
        return -1

    # Iterate over repositories
    for repository in repositories:

        # Execution header
        if not quiet:
            print(' ')
            print(f'{Colors.BOLD} - Repository:'
                  f'{Colors.CYAN} {repository}'
                  f'{Colors.RESET}')
            print(' ')
            Platform.flush()

        # Show commands
        if not quiet or dry_run:
            print(f'   + {" ".join(commands)}')
            Platform.flush()

        # Run commands
        if not dry_run:
            result = Tools.run_command(
                commands,
                cwd=repository,
            )

    # Root footer
    if not quiet:
        print(' ')
        Platform.flush()

    # Result
    return result

# Main, pylint: disable=duplicate-code
def main() -> None:

    # Variables
    group: _ArgumentGroup
    result: int

    # Configure tool
    Tools.NAME = 'git foreach'
    Tools.DESCRIPTION = 'Execute commands in each Git repositories under current path'

    # Arguments creation
    parser: ArgumentParser = ArgumentParser(
        prog=Tools.NAME,
        description=f'{Tools.NAME}: {Tools.DESCRIPTION} ({Bundle.NAME})',
        add_help=False,
        formatter_class=lambda prog: RawTextHelpFormatter(
            prog,
            max_help_position=HELP_POSITION,
            width=min(
                120,
                get_terminal_size().columns - 2,
            ),
        ),
    )

    # Arguments tool definitions
    group = parser.add_argument_group('tool arguments')
    group.add_argument(
        '-h',
        '--help',
        dest='help',
        action='store_true',
        help='Show this help message',
    )
    group.add_argument(
        '-q',
        '--quiet',
        dest='quiet',
        action='store_true',
        help='Hide repositories context upon execution',
    )
    group.add_argument(
        '-n',
        '--dry-run',
        dest='dry_run',
        action='store_true',
        help='Show commands usage without execution',
    )
    group.add_argument(
        '-R',
        '--no-recurse-submodules',
        dest='no_recurse_submodules',
        action='store_true',
        help='Avoid recursing in repositories submodules',
    )
    group.add_argument(
        'commands',
        nargs='*',
        default=COMMANDS_DEFAULT,
        help=f'Command arguments to run (default: {" ".join(COMMANDS_DEFAULT)})',
    )

    # Arguments parser
    options: Namespace = parser.parse_args()

    # Help informations
    if options.help:
        print(' ')
        parser.print_help()
        print(' ')
        Platform.flush()
        sys_exit(0)

    # Instantiate settings
    settings: Settings = Settings(name=Bundle.NAME)

    # Prepare colors
    Colors.prepare()

    # Instantiate updates
    updates: Updates = Updates(
        name=Bundle.PACKAGE,
        settings=settings,
    )

    # Run tool
    result = git_foreach(
        commands=options.commands,
        dry_run=options.dry_run,
        quiet=options.quiet,
        recurse_submodules=not options.no_recurse_submodules,
    )

    # Check for daily updates
    if updates.enabled and updates.daily:
        updates.check()

    # Result
    sys_exit(0 if result >= 0 else result)

# Entrypoint
if __name__ == '__main__': # pragma: no cover
    main()
