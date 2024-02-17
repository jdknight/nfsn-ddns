# SPDX-License-Identifier: BSD-2-Clause
# Copyright nfsn-ddns Contributors

from nfsn_ddns import __version__ as nfsn_ddns_version
from nfsn_ddns.defs import Action
from nfsn_ddns.engine import engine
from nfsn_ddns.log import err
from nfsn_ddns.log import log
from nfsn_ddns.log import nfsn_ddns_log_configuration
from nfsn_ddns.log import verbose
from nfsn_ddns.win32 import enable_ansi_win32
from pathlib import Path
import argparse
import os
import sys


def main() -> int:
    """
    mainline

    The mainline for the nfsn-ddns utility.

    Returns:
        the exit code
    """
    retval = 1

    try:
        parser = argparse.ArgumentParser(prog='nfsn-ddns',
            add_help=False, usage=usage())
        parser.add_argument('action', nargs='?',
            type=Action, choices=list(Action))
        parser.add_argument('--api-login')
        parser.add_argument('--api-token')
        parser.add_argument('--cache', action='store_true')
        parser.add_argument('--cache-days', type=int)
        parser.add_argument('--cache-file', type=Path)
        parser.add_argument('--cfg', type=Path)
        parser.add_argument('--ddns-domain', action='append', nargs='+')
        parser.add_argument('--help', '-h', action='store_true')
        parser.add_argument('--no-cache', action='store_true')
        parser.add_argument('--nocolorout', action='store_true')
        parser.add_argument('--quiet', action='store_true')
        parser.add_argument('--timeout', type=int)
        parser.add_argument('--verbose', '-V', action='store_true')
        parser.add_argument('--version', action='version',
            version='%(prog)s ' + nfsn_ddns_version)
        args = parser.parse_args()
        if args.help:
            print(usage())
            sys.exit(0)

        # force color off if `NO_COLOR` is configured
        if os.environ.get('NO_COLOR'):
            args.nocolorout = True

        nfsn_ddns_log_configuration(
            nocolor=args.nocolorout,
            verbose_=args.verbose)

        # toggle on ansi colors by default for commands
        if not args.nocolorout:
            os.environ['CLICOLOR_FORCE'] = '1'

            # support character sequences (for color output on win32 cmd)
            if sys.platform == 'win32':
                enable_ansi_win32()

        if args.cache_file:
            args.cache = True

        banner_call = log
        if args.quiet:
            banner_call = verbose

        banner_call('nfsn-ddns {}', nfsn_ddns_version)
        verbose('({})', __file__)

        if args.cfg and not args.cfg.is_file():
            err(f'missing configuration file: {args.cfg}')
            return 1

        retval = engine(args)
    except KeyboardInterrupt:
        print('')

    return retval


def usage() -> str:
    """
    display the usage for this utility

    Returns a command line usage string for all options provided by
    this utility.

    Returns:
        the usage string
    """
    return """nfsn-ddns <options> [action]

(actions)
 check                     Only attempt to check interaction with NFSN
 ip                        Only attempt to fetch my external IP

(options)
 --api-login <login>       The API login to authenticate with NFSN
 --api-token <token>       The API token to authenticate with NFSN
 --cache                   Whether to cache public IP for change checks
 --cache-days <duration>   Number of days to consider cache stale
 --cache-file <file>       Cache file when caching public IP
 --cfg <file>              Configuration file to load
 --ddns-domain <domain>    The domain to be updated
 -h, --help                Show this help
 --no-cache                Explicitly disable any cache attempts
 --nocolorout              Explicitly disable colorized output
 --quiet                   Suppress startup banner
 --timeout <duration>      Number of seconds for any web request
 -V, --verbose             Show additional messages
 --version                 Show the version
"""


if __name__ == '__main__':
    sys.exit(main())
