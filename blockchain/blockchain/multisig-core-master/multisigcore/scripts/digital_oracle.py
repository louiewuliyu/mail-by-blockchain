#!/usr/bin/env python

from __future__ import print_function
import io
import sys
import argparse
import textwrap

import codecs
import os
from multisigcore.hierarchy import MultisigAccount

from pycoin import encoding
from pycoin.serialize import b2h, stream_to_bytes
from pycoin.key import Key
from pycoin.key.BIP32Node import BIP32Node
from pycoin.networks import NETWORK_NAMES
from pycoin.tx import Tx
from pycoin.services import get_tx_db
from multisigcore import Oracle, local_sign
from itertools import izip_longest


def main():
    parser = argparse.ArgumentParser(
        description='DigitalOracle HD multisig command line utility',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('-e', '--email',
                        help='e-mail for create')
    parser.add_argument('-p', '--phone',
                        help='phone number for create - in the format +14155551212')
    parser.add_argument('-n', '--network',
                        default='BTC', choices=NETWORK_NAMES)
    parser.add_argument('-i', "--inputpath",
                        nargs='+',
                        help='HD subkey path for each input (example: 0/2/15)')
    parser.add_argument('-c', "--changepath",
                        nargs='+',
                        help='HD subkey path for each change output (example: 0/2/15) or a dash for non-change outputs')
    parser.add_argument('-s', "--spendid",
                        help='an additional hex string to disambiguate spends to the same address')
    parser.add_argument('-u', "--baseurl",
                        help='the API endpoint, defaults to the sandbox - https://s.digitaloracle.co/')
    parser.add_argument('-v', "--verbose", default=0, action="count",
                        help="Verbosity, use more -v flags for more verbosity")
    parser.add_argument('command',
                        help="""a command""")
    parser.add_argument('item',
                        nargs='+', help="""a key""")
    parser.epilog = textwrap.dedent("""
    Items:
     * P:wallet_passphrase - a secret for deriving an HD hierarchy with private keys
     * xpub - an account extended public key for deriving an HD hierarchy with public keys only
     * FILE.bin - unsigned transaction binary
     * FILE.hex - unsigned transaction hex

    Commands:
     * dump - dump the public subkeys
     * create - create Oracle account based on the supplied leading key with with any additional keys
     * address - get the deposit address for a subkey path
     * sign - sign a transaction, tx.bin or tx.hex must be supplied. Only one subkey path is supported.

    Notes:
     * --subkey is applicable for the address and sign actions, but not the create action
    """)
    args = parser.parse_args()

    keys = []
    txs = []
    for item in args.item:
        key = None
        tx = None
        if item.startswith('P:'):
            s = item[2:]
            key = BIP32Node.from_master_secret(s.encode('utf8'), netcode=args.network)
            keys.append(key)
        else:
            try:
                key = Key.from_text(item)
                keys.append(key)
            except encoding.EncodingError:
                pass
        if key is None:
            if os.path.exists(item):
                try:
                    with open(item, "rb") as f:
                        if f.name.endswith("hex"):
                            f = io.BytesIO(codecs.getreader("hex_codec")(f).read())
                        tx = Tx.parse(f)
                        txs.append(tx)
                        try:
                            tx.parse_unspents(f)
                        except Exception as ex:
                            pass
                        continue
                except Exception as ex:
                    print('could not parse %s %s' % (item, ex), file=sys.stderr)
                    pass
        if tx is None and key is None:
            print('could not understand item %s' % (item,))

    account = MultisigAccount(keys, complete=False)
    oracle = Oracle(account, tx_db=get_tx_db(), base_url=args.baseurl)
    oracle.verbose = args.verbose

    if args.command == 'dump':
        sub_keys = [key.subkey_for_path(path or "") for key, path in izip_longest(keys, args.inputpath)]
        for key in sub_keys:
            print(key.wallet_key(as_private=False))
    elif args.command == 'create':
        calls = []
        if args.email:
            calls.append('email')
        if args.phone:
            calls.append('phone')
        parameters = {
            "levels": [
                {"asset": "BTC", "period": 60, "value": 0.001},
                {"delay": 0, "calls": calls}
            ]
        }
        oracle.create(parameters, email=args.email, phone=args.phone)
    elif args.command == 'address':
        oracle.get()
        path = args.inputpath[0] if args.inputpath else ""
        payto = account.payto_for_path(path)
        if args.verbose > 0:
            sub_keys = [key.subkey_for_path(path) for key in account.keys]
            print("* account keys")
            print(account.keys)
            print("* child keys")
            for key in sub_keys:
                print(key.wallet_key(as_private=False))
            print("* address")
        print(payto.address(netcode=args.network))
    elif args.command == 'sign':
        oracle.get()
        scripts = [account.script_for_path(path) for path in args.inputpath]
        change_paths = [None if path == '-' else path for path in (args.changepath or [])]
        for tx in txs:
            print(tx.id())
            print(b2h(stream_to_bytes(tx.stream)))
            sub_keys = [keys[0].subkey_for_path(path) for path in args.inputpath]
            # sign locally
            local_sign(tx, scripts, sub_keys)
            # have Oracle sign
            result = oracle.sign_with_paths(tx, args.inputpath, change_paths, spend_id=args.spendid)
            print("Result:")
            print(result)
            if 'transaction' in result:
                print("Hex serialized transaction:")
                print(b2h(stream_to_bytes(result['transaction'].stream)))
    else:
        print('unknown command %s' % (args.command,), file=sys.stderr)


if __name__ == '__main__':
    main()
