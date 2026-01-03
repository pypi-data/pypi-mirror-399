#!/usr/bin/env python3

# Standard libraries
from argparse import (
    _ArgumentGroup,
    ArgumentParser,
    Namespace,
    RawTextHelpFormatter,
)
from os import (
    environ,
    getcwd,
    path,
)
from pathlib import Path
from shutil import get_terminal_size, which
from sys import exit as sys_exit
from time import sleep
from typing import List

# Components
from ..package.bundle import Bundle
from ..package.settings import Settings
from ..package.updates import Updates
from ..prints.colors import Colors
from ..system.platform import Platform
from .tools import Tools

# Constants
BINARY_BYOBU: str = 'byobu'
BINARY_FZF: str = 'fzf'
BINARY_SCREEN: str = 'screen'
BINARY_TMUX: str = 'tmux'
CONFIGURATION_PATH: str = 'dashboard-panel.conf'
DEFAULT_DISCOVERY: bool = True
HELP_POSITION: int = 26
LABEL_CONFIGURE: str = 'Configure dashboard'
LABEL_EXIT: str = 'Exit dashboard'
LABEL_RELOAD: str = 'Reload dashboard'
SEPARATOR_SHORT: str = '────────────────────────'
SEPARATOR_LONG: str = '────────────────────────────────────────────────'

# Open new panel
def open_new_panel(selection: str) -> int:

    # Variables
    name: str = path.basename(selection)
    multiplexers: List[str]

    # Open byobu panel
    if which(BINARY_BYOBU):
        return Tools.run_command([
            BINARY_BYOBU,
            'new-window',
            '-c',
            selection,
            '-n',
            name,
        ])

    # Open tmux panel
    if which(BINARY_TMUX):
        return Tools.run_command([
            BINARY_TMUX,
            'new-window',
            '-c',
            selection,
            '-n',
            name,
        ])

    # Open screen panel
    if which(BINARY_SCREEN):
        return Tools.run_command([
            BINARY_SCREEN,
            '-t',
            name,
            selection,
        ])

    # Missing multiplexer support
    multiplexers = [
        BINARY_BYOBU,
        BINARY_SCREEN,
        BINARY_TMUX,
    ]
    print(' ')
    print(f'{Colors.YELLOW} {Tools.NAME}:'
          f'{Colors.RED} No supported terminal multiplexer detected'
          f'{Colors.CYAN} (Supported: {", ".join(multiplexers)})'
          f'{Colors.RESET}')
    print(' ')
    Platform.flush()
    sleep(3)
    return -1

# Provide fzf preview command
def provide_fzf_preview(configuration: str, ) -> str:

    # Variables
    fzf_file = '{}'

    # Provide command
    return f'''
        if [ -d {fzf_file} ]; then
            ls -lah --color=always {fzf_file};
        elif [ -f {fzf_file} ]; then
            cat {fzf_file};
        elif [ {fzf_file} = "{LABEL_CONFIGURE}" ]; then
            cat {configuration};
        fi
    '''

# Provide fzf reload command
def provide_fzf_reload(
    configuration: str,
    depth: int,
    discover: bool,
) -> str:

    # Variables
    discover_block: str = ''

    # Enable discovery
    if discover:
        discover_block = f"""
            find \
                -maxdepth '{depth}' \
                -name '.git' \
                -not -path '*/.cache/*' \
                -not -path '*/build/*' \
              | sed 's#/\\.git##g';
        """

    # Provide command
    return f"""
        echo '{LABEL_RELOAD}';
        echo '{LABEL_CONFIGURE}';
        echo '{LABEL_EXIT}';
        echo '{SEPARATOR_SHORT}';
        sed \
            -e 's|^~/|{environ.get("HOME", "")}/|' \
            -e 's/^$/{SEPARATOR_SHORT}/' \
            '{configuration}';
        echo '{SEPARATOR_LONG}';
        {discover_block}
    """

# Run fzf menu
def run_fzf(
    configuration: str,
    depth: int,
    discover: bool,
) -> str:

    # Configure fzf
    environ['FZF_DEFAULT_OPTS'] = """
        --color 'bg:#1B1D1E,bg+:#293739'
        --color 'border:#808080'
        --color 'spinner:#E6DB74'
        --color 'hl:#7E8E91,hl+:#F92672'
        --color 'fg:#F8F8F2,fg+:#F8F8F2'
        --color 'header:#7E8E91,header-border:#6699cc,header-label:#99ccff'
        --color 'info:#A6E22E'
        --color 'input-border:#996666,input-label:#ffcccc'
        --color 'label:#808080'
        --color 'list-border:#669966,list-label:#99cc99'
        --color 'marker:#F92672'
        --color 'pointer:#A6E22E'
        --color 'prompt:#F92672'
        --color 'preview-border:#9999cc,preview-label:#ccccff'
    """

    # Show fzf
    return Tools.run_output(
        [
            BINARY_FZF,
            '--bind',
            'focus:transform-preview-label:[ ! -z {} ] && printf " Preview: %s " {}',
            '--bind',
            'focus:+transform-header:[ -e {} ] && file --brief {} || echo "-"',
            '--bind',
            'enter:accept+abort',
            '--bind',
            f'start:reload-sync:{provide_fzf_reload(configuration, depth, discover)}',
            '--border',
            '--border-label',
            f' {Tools.NAME} ({Bundle.NAME}) ',
            '--header-label',
            ' Selection type ',
            '--input-label',
            ' Create panel with selection ',
            '--layout',
            'reverse',
            '--list-label',
            ' Dashboard list ',
            '--padding',
            '1,10',
            '--phony',
            '--preview',
            f'{provide_fzf_preview(configuration)}',
            '--preview-label',
            ' Preview ',
            '--preview-window',
            'right:45%',
            '--prompt',
            '> ',
            '--style',
            'full',
        ],
        stderr=False,
    )

# Dashboard panel of Git paths, pylint: disable=duplicate-code
def git_dashboard_panel(
    discovery: bool,
    depth: int,
    editor: str,
) -> int:

    # Variables
    configuration: Path
    selection: str
    userspace: Path

    # Validate dependencies
    if not which(BINARY_FZF):
        print(' ')
        print(f'{Colors.YELLOW} {Tools.NAME}:'
              f'{Colors.RED} Missing dependency \'{BINARY_FZF}\' detected'
              f'{Colors.RESET}')
        print(' ')
        Platform.flush()
        sleep(3)
        return -1

    # Prepare configuration
    userspace = Platform.userspace(name=Bundle.NAME)
    userspace.mkdir(parents=True, exist_ok=True)
    configuration = userspace / CONFIGURATION_PATH
    if not path.exists(configuration):
        with open(configuration, 'w', encoding='utf-8') as file:
            print(environ.get('HOME', ''), file=file)
            print('', file=file)
            print(getcwd(), file=file)

    # Run entrypoint
    while True:

        # Show menu
        selection = run_fzf(
            configuration=str(configuration),
            depth=depth,
            discover=discovery,
        )

        # Interrupt menu
        if not selection or selection == LABEL_EXIT:
            break

        # Reload dashboard
        if selection == LABEL_RELOAD:
            continue

        # Ignore separators
        if selection in (
                SEPARATOR_SHORT,
                SEPARATOR_LONG,
        ):
            continue

        # Edit dashboard
        if selection == LABEL_CONFIGURE:
            Tools.run_command([
                editor,
                str(configuration),
            ])
            continue

        # Open panel
        open_new_panel(selection)

        # Delay
        sleep(0.1)

    # Result
    return 0

# Main, pylint: disable=duplicate-code
def main() -> None:

    # Variables
    discovery: bool
    group: _ArgumentGroup
    result: int

    # Configure tool
    Tools.NAME = 'git dashboard-panel'
    Tools.DESCRIPTION = 'Dashboard panel of Git paths with interactive selection'

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
        '--enable-discovery',
        dest='enable_discovery',
        action='store_true',
        help='Enable automatic Git paths discovery',
    )
    group.add_argument(
        '--disable-discovery',
        dest='disable_discovery',
        action='store_true',
        help='Disable automatic Git paths discovery',
    )
    group.add_argument(
        '--depth',
        dest='depth',
        type=int,
        default=10,
        help='Maximum depth for Git paths discovery',
    )
    group.add_argument(
        '--editor',
        dest='editor',
        default=environ.get('EDITOR', 'nano'),
        help='Editor binary to use for configuration editing',
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

    # Parse discovery
    if options.disable_discovery:
        discovery = False
    elif options.enable_discovery:
        discovery = True
    else:
        discovery = DEFAULT_DISCOVERY

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
    result = git_dashboard_panel(
        discovery=discovery,
        depth=options.depth,
        editor=options.editor,
    )

    # Check for daily updates
    if updates.enabled and updates.daily:
        updates.check()

    # Result
    sys_exit(0 if result >= 0 else result)

# Entrypoint
if __name__ == '__main__': # pragma: no cover
    main()
