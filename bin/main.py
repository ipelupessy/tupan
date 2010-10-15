#!/usr/bin/env python

"""
Performs a N-body Simulation
"""

import sys
import argparse
from pynbody import Simulation


def process_cmdline():
    """
    process command line arguments
    """
    # create the parser
    parser = argparse.ArgumentParser(
        description='Performs a N-body Simulation')

    # add the arguments
    parser.add_argument(
        '--log', type=argparse.FileType('w'), default=sys.stdout,
        help='the file where the log should be written (default: sys.stdout)')

    # parse the command line
    args = parser.parse_args()
    return args


def main():
    """
    The top level main function
    """
    args = process_cmdline()
    mysim = Simulation(args)
    mysim.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())


########## end of file ##########