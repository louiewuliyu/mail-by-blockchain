import json
from urllib2 import urlopen
from pycoin.convention import btc_to_satoshi
from pycoin.serialize import h2b, h2b_rev
from pycoin.services.insight import InsightService
from pycoin.tx import Spendable
from . import BatchService

__author__ = 'devrandom'

CHUNK_SIZE = 100


class InsightBatchService(InsightService, BatchService):
    def __init__(self, base_url):
        InsightService.__init__(self, base_url)

    def spendables_for_addresses(self, bitcoin_addresses):
        """
        Return a list of Spendable objects for the
        given bitcoin address.
        """
        r = []
        for i in xrange(0, len(bitcoin_addresses), CHUNK_SIZE):
            addresses = bitcoin_addresses[i:i+CHUNK_SIZE]
            url = "%s/api/addrs/%s/utxo" % (self.base_url, ",".join(addresses))
            r.extend(json.loads(urlopen(url).read().decode("utf8")))
        spendables = []
        for u in r:
            coin_value = btc_to_satoshi(str(u.get("amount")))
            script = h2b(u.get("scriptPubKey"))
            previous_hash = h2b_rev(u.get("txid"))
            previous_index = u.get("vout")
            spendables.append(Spendable(coin_value, script, previous_hash, previous_index))
        return spendables