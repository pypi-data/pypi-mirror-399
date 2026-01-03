# coding=utf-8
'''
Copyright (C) 2023-2025 Siogeen

Created on 4.1.2023

@author: Reimund Renner
'''

import argparse

def get_parser():
    """Get CLI parser"""
    ret = argparse.ArgumentParser(
        description='Check for IO-Link masters and devices',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Examples:
  python -m siogeen.tools.cli.IoddComChecker
  python -m siogeen.tools.cli.IoddComChecker -a 10.0.0.17 -a 10.0.0.19 --auto -s ETH
  python -m siogeen.tools.cli.IoddComChecker -s USB --gui''')
    ret.add_argument("-a", "--address", action='append',
                        help="Specify one or more master addresses (default all)")
    ret.add_argument("--auto", action='store_true',
                        help="Activate master ports if all are disabled")
    ret.add_argument("-s", "--select",
                        help="Select specific master types: ETH (ethernet) or USB")
    ret.add_argument("--verbose", default=2, help="Select verbosity 0..3")
    ret.add_argument("--version", action='store_true',
        help="Print version")
    ret.add_argument("--gui", action='store_true',
                        help="Start the graphical user interface")
    ret.add_argument("--gui-mode", default='Dark', choices=('Dark', 'Light'),
                        help="GUI screen mode")

    return ret

if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    #args = parser.parse_args(['--auto'])
    #args = parser.parse_args(['-a', '/dev/ttyUSB0'])
    #args = parser.parse_args(['-a', '192.168.178.77'])
    #args = parser.parse_args(['-a', '192.168.178.77', '-a', '192.168.178.73'])
    #args = parser.parse_args(['-a', '192.168.178.77', '--auto'])
    #args = parser.parse_args(['--gui', '--version'])
    #args = parser.parse_args(['--gui', '--gui-mode', 'Light', '--select', 'USB'])

    from siogeen.tools import IoddComChecker
    if args.gui:
        from siogeen.tools.gui import IoddComChecker as GC

    if args.version:
        sgui = f" (GUI {GC.__version__})" if args.gui and IoddComChecker.__version__ != GC.__version__ else ""
        print(f"IoddComChecker {IoddComChecker.__version__}" + sgui)
    elif args.gui:
        GC.IoddComCheckerGui(args.address, args.auto, args.verbose, args.select, args.gui_mode).run()
    else:
        IoddComChecker.check(args.address, args.auto, verbose=args.verbose, select=args.select)
