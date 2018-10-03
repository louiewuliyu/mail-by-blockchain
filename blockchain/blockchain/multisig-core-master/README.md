BitOasis / CryptoCorp's Multisig python API implementation using the pycoin library.
[![Build Status](https://travis-ci.org/devrandom/multisig-core.svg?branch=master)](https://travis-ci.org/devrandom/multisig-core)

Examples
===
```bash
    export PYCOIN_CACHE_DIR=~/.pycoin_cache
    export PYCOIN_SERVICE_PROVIDERS=BLOCKR_IO:BLOCKCHAIN_INFO:BITEASY:BLOCKEXPLORER

    digital_oracle --email a@b.com create P:aaa P:bbb
       # not recommended - both keys on one machine

    digital_oracle --email a@b.com create P:aaa xpub...

    digital_oracle -i 0/0/123 address P:aaa xpub...
       # shows deposit address

    tx -i SOURCE_ADDRESS DESTINATION_ADDRESS/100000 CHANGE_ADDRESS -o tx.bin

    digital_oracle sign P:aaa xpub... tx.bin -i 0/0/123
       # signs and shows tx hex)

    digital_oracle sign P:aaa xpub... tx.bin -i 0/0/123 0/0/124 -c - 0/1/44
       # signs tx with two inputs and two outputs.  The second output is change.
```

Programmatic Examples
===

```python
    from multisigcore import *
    from multisigcore.providers.electrum import ElectrumService
    from multisigcore.oracle import PersonalInformation, OracleUnknownKeychainException
    from multisigcore.hierarchy import MasterKey, MultisigAccount
    from pycoin.services import insight, get_tx_db
    from pycoin.serialize import b2h, h2b
    
    secrets = [WALLET_PHRASE, RECOVERY_PHRASE] # don't put both phrases on one machine in real life
    keys = [MasterKey.from_master_secret(x).bip44_account(0) for x in secrets]
    account = MultisigAccount(keys, complete=False)
    oracle = Oracle(account, tx_db=get_tx_db())
    oracle.verbose = 0
    parameters = {"levels": [ {
                              "asset": "BTC",
                              "period": 3600,
                              "value": 1.0
                          }]}
    try: oracle.get()
    except OracleUnknownKeychainException: oracle.create(parameters, PersonalInformation())
    
    print("http://btc.blockr.io/address/info/" + account.address(0))
    account.set_lookahead(0)
    service = insight.InsightService('https://insight.bitpay.com/')
    #service = ElectrumService("electrum.no-ip.org", 50002)
    account._provider = service
    print(account.balance())
    print(oracle._url())

    tx = account.tx([(DEST_ADDRESS, 50000)])
    account.sign(tx)
    res = oracle.sign(tx, "spend003")
    print(res)
    print(res.transaction.as_hex())
```

Testing
===
```bash
    python -m unittest discover
```