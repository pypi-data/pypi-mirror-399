#!/usr/bin/env python3
import argparse
import logging
import sys

from gnuscreen import gnuscreen_logger, GnuScreen,__version__ as gnuscreen_version


def main():
    logging.basicConfig()
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--loglevel', default='WARN', help="Python logging level")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--list',action='store_true', help="List screens")
    group.add_argument('--start',help="Start screen if necesary")
    group.add_argument('--query',help="Test for existing screen")
    group.add_argument('--close',help="Close screen if it exits")
    group.add_argument('--execute',nargs='+',help="Execute commands on screen: screen name, commands")
    group.add_argument('--version',action='store_true', help="show version")

    args = parser.parse_args()
    gnuscreen_logger.setLevel(getattr(logging,args.loglevel))
    if args.version:
        print(gnuscreen_version)
    if args.list:
        for gs in GnuScreen.list():
            print(gs)
    if args.start:
        print(GnuScreen.get(args.start))
    if args.query:
        scr = GnuScreen.query(args.query)
        print(scr)
        if scr is None:
            sys.exit(1)
    if args.execute:
        name = args.execute[0]
        commands = args.execute[1:]
        if commands:
            gs = GnuScreen.get(name)
            gs.execute(commands)
        else:
            print('--execute requires 2 or more arguments',file=sys.stderr)
            sys.exit(2)
    if args.close:
        if (gs:=GnuScreen.query(args.close)) is not None:
            gs.close()
        else:
            print(f'{args.close} not found')



if __name__ == "__main__":
    main()

