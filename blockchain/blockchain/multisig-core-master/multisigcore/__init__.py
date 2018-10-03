"""

"""
from pycoin.encoding import wif_to_secret_exponent
from pycoin.networks import wif_prefix_for_netcode

__author__ = 'devrandom'

from pycoin.tx.pay_to import build_p2sh_lookup, build_hash160_lookup
from pycoin.tx.tx_utils import LazySecretExponentDB
from .oracle import Oracle


class LazySecretExponentDBWithNetwork(LazySecretExponentDB):
    def __init__(self, netcode, wif_iterable, secret_exponent_db_cache):
        super(LazySecretExponentDBWithNetwork, self).__init__(wif_iterable, secret_exponent_db_cache)
        self.netcode = netcode
        self.wif_prefix = wif_prefix_for_netcode(netcode)

    def get(self, v):
        if v in self.secret_exponent_db_cache:
            return self.secret_exponent_db_cache[v]
        for wif in self.wif_iterable:
            secret_exponent = wif_to_secret_exponent(wif, self.wif_prefix)
            d = build_hash160_lookup([secret_exponent])
            self.secret_exponent_db_cache.update(d)
            if v in self.secret_exponent_db_cache:
                return self.secret_exponent_db_cache[v]
        self.wif_iterable = []
        return None


def local_sign(tx, redeem_scripts, keys):
    """
    Utility for locally signing a multisig transaction

    :param tx:
    :param scripts:
    :param keys: one key per transaction input
    :return:
    """
    lookup = None
    if redeem_scripts:
        raw_scripts = [script.script() for script in redeem_scripts]
        lookup = build_p2sh_lookup(raw_scripts)
    if keys:
        netcode = keys[0]._netcode
    else:
        # Nothing to do
        return
    db = LazySecretExponentDBWithNetwork(netcode, [key.wif() for key in keys], {})
    tx.sign(db, p2sh_lookup=lookup)


