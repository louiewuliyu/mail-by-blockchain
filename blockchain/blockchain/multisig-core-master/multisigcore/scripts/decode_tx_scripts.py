#!/usr/bin/python
from __future__ import print_function
import sys

from pycoin.tx import Tx
from pycoin.tx.script.tools import disassemble

def main():
    tx = Tx.tx_from_hex(sys.argv[1])
    print('Input Scripts:')
    for inp in tx.txs_in:
        print(' - ' + disassemble(inp.script))
    print('Output Scripts:')
    for out in tx.txs_out:
        print(' - ' + disassemble(out.script))

if __name__ == '__main__':
    main()
