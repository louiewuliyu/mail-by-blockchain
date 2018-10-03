#!/usr/bin/python

from __future__ import print_function
import sys

from pycoin.tx.script.tools import disassemble
from pycoin.serialize import h2b


def main():
    print(disassemble(h2b(sys.argv[1])))

if __name__ == '__main__':
    main()
