__author__ = 'devrandom'


class BatchService(object):
    """Marker class for providers that implement spendables_for_addresses"""
    def spendables_for_addresses(self, addresses):
        """
        :param list[str] addresses:
        :rtype: list[pycoin.tx.Spendable.Spendable]
        """
        raise NotImplementedError()