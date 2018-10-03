from multisigcore.hierarchy import *

__author__ = 'devrandom'

recover_key = AccountKey.from_key("xpub661MyMwAqRbcGmRK6wKJrfMXoenZ86PMUfBWNvmmp5c51PyyzjY7yJL9venRUYqmSqNo7iGqHbVWkTVYzY2drw57vr45iHxV7NsAqF4ZWg5")
wallet_key = AccountKey.from_key("xpub661MyMwAqRbcFqtR38s6kVQudQxKpHzNJyWEXmz2TnuDoR8FpZR7EuL158B5QDaYvxCfp3LAEa8VwdtxNgKHNha4JKqGrqkzBGboJFwgyrR")
oracle_key = AccountKey.from_key("xpub68rQ8y4gfKeqG3sxQQE7uNwjnjcTiEZDQCrr2witfS3VrZ3QkeR2XuiQWUpdQRUVShcyVzjX2ZvDWHS2SZcZJXaGC7HybSPVMDXErbRRHwn")
TEST_PATH = "0/0/1"

def make_multisig_account():
    return MultisigAccount(keys=[wallet_key, recover_key, oracle_key])


def make_unsorted_multisig_account():
    return MultisigAccount(keys=[wallet_key, recover_key, oracle_key], sort=False)


def make_incomplete_multisig_account():
    return MultisigAccount(keys=[wallet_key, recover_key], complete=False)


