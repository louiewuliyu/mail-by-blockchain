from unittest import TestCase
from multisigcore.hierarchy import *
from multisigcore.testing import make_multisig_account, make_unsorted_multisig_account, TEST_PATH

from pycoin.encoding import bitcoin_address_to_hash160_sec
from pycoin.networks import address_prefix_for_netcode
from pycoin.scripts.tx import dump_tx
from pycoin.serialize import h2b
from pycoin.tx import Spendable
from pycoin.tx.pay_to import ScriptPayToAddress

__author__ = 'devrandom'


class MySimpleTestnetProvider(object):
    def spendables_for_address(self, address):
        if address == "mgMy4vmqChGT8XeKPb1zD6RURWsiNmoNvR":
            script = ScriptPayToAddress(
                bitcoin_address_to_hash160_sec(address, address_prefix_for_netcode('XTN')))
            return [Spendable(coin_value=10000,
                              script=script.script(),
                              tx_out_index=0, tx_hash=b'2'*32)]
        else:
            return []


class MySimpleProvider(object):
    def spendables_for_address(self, address):
        if address == "1r1msgrPfqCMRAhg23cPBD9ZXH1UQ6jec":
            return [Spendable(coin_value=10000,
                              script=ScriptPayToAddress(bitcoin_address_to_hash160_sec(address)).script(),
                              tx_out_index=0, tx_hash=b'2'*32)]
        else:
            return []

class HierarchyTest(TestCase):
    def setUp(self):
        self.master_key = MasterKey.from_seed(h2b("000102030405060708090a0b0c0d0e0f"))
        self.master_key1 = MasterKey.from_seed(h2b("fffcf9f6f3f0edeae7e4e1dedbd8d5d2cfccc9c6c3c0bdbab7b4b1aeaba8a5a29f9c999693908d8a8784817e7b7875726f6c696663605d5a5754514e4b484542"))
        self.multisig_account = make_multisig_account()

    def test_master(self):
        self.assertEqual(self.master_key.as_text(), MasterKey.from_seed_hex("000102030405060708090a0b0c0d0e0f").as_text())
        self.assertEqual(self.master_key.as_text(), "xpub661MyMwAqRbcFtXgS5sYJABqqG9YLmC4Q1Rdap9gSE8NqtwybGhePY2gZ29ESFjqJoCu1Rupje8YtGqsefD265TMg7usUDFdp6W1EGMcet8")
        self.assertEqual(self.master_key.as_text(as_private=True), "xprv9s21ZrQH143K3QTDL4LXw2F7HEK3wJUD2nW2nRk4stbPy6cq3jPPqjiChkVvvNKmPGJxWUtg6LnF5kejMRNNU3TGtRBeJgk33yuGBxrMPHi")
        self.assertEqual(self.master_key1.as_text(), "xpub661MyMwAqRbcFW31YEwpkMuc5THy2PSt5bDMsktWQcFF8syAmRUapSCGu8ED9W6oDMSgv6Zz8idoc4a6mr8BDzTJY47LJhkJ8UB7WEGuduB")
        self.assertEqual(self.master_key1.as_text(as_private=True), "xprv9s21ZrQH143K31xYSDQpPDxsXRTUcvj2iNHm5NUtrGiGG5e2DtALGdso3pGz6ssrdK4PFmM8NSpSBHNqPqm55Qn3LqFtT2emdEXVYsCzC2U")

    def test_account(self):
        account = self.master_key.account_for_path("0H/1/2H")
        self.assertEqual(account.as_text(), "xpub6D4BDPcP2GT577Vvch3R8wDkScZWzQzMMUm3PWbmWvVJrZwQY4VUNgqFJPMM3No2dFDFGTsxxpG5uJh7n7epu4trkrX7x7DogT5Uv6fcLW5")
        self.assertEqual(account.as_text(as_private=True), "xprv9z4pot5VBttmtdRTWfWQmoH1taj2axGVzFqSb8C9xaxKymcFzXBDptWmT7FwuEzG3ryjH4ktypQSAewRiNMjANTtpgP4mLTj34bhnZX7UiM")
        leaf = account.leaf_for_path("2/1000000000")
        self.assertEqual(leaf.as_text(), "xpub6H1LXWLaKsWFhvm6RVpEL9P4KfRZSW7abD2ttkWP3SSQvnyA8FSVqNTEcYFgJS2UaFcxupHiYkro49S8yGasTvXEYBVPamhGW6cFJodrTHy")
        self.assertEqual(leaf.as_text(as_private=True), "xprvA41z7zogVVwxVSgdKUHDy1SKmdb533PjDz7J6N6mV6uS3ze1ai8FHa8kmHScGpWmj4WggLyQjgPie1rFSruoUihUZREPSL39UNdE3BBDu76")

    def test_electrum(self):
        # Electrum seed v6: fade really needle dinner excuse half rabbit sorry stomach confusion bid twice suffer
        m = MasterKey.from_seed(h2b("7043e6911790bbcc5d0c5c00ab4c3deb2641af606f987113bcc28b7ccd94b2b6be3a0203be1c61fe64e6d6e4e806107fec9e80d5bf9a62284d3bb45550d797f0"))
        a = m.electrum_account(0)
        l = a.leaf(0)
        self.assertEqual(l.address(), "1AGWXxRe7FwWJJ6k5uAfwcoA7Sov9AYNVK")
        # Simulate generation of an Electrum master public key for the 1of1 hierarchy
        em = MasterKey.from_key(m.account_for_path("0H").hwif())
        a1 = em.bip32_account(0, hardened=False)
        self.assertEqual(a.hwif(), a1.hwif())

    def test_multisig_payto(self):
        payto = self.multisig_account.payto_for_path(TEST_PATH)
        self.assertEqual("34DjTcNWGReJV4xx7R1AWK7FTz3xMwMcjA", payto.address())
        uma = make_unsorted_multisig_account()
        payto = uma.payto_for_path(TEST_PATH)
        self.assertEqual("3EyjKmfhbcrBHUCi9a7Qg8NYcMBK27aaDa", payto.address())

    def test_multisig_address(self):
        uma = make_unsorted_multisig_account()
        self.assertEqual("3MhrgJ9BtL3GTsUU6EqAqDGKdUAv8C15EN", self.multisig_account.address(0))
        # Happens to already be sorted
        self.assertEqual("3MhrgJ9BtL3GTsUU6EqAqDGKdUAv8C15EN", uma.address(0))

        self.assertEqual("3CWheC3YFPXAxVPBKkevMV5YFhy2h2oVSu", self.multisig_account.address(1))
        # Happens to already be sorted
        self.assertEqual("3CWheC3YFPXAxVPBKkevMV5YFhy2h2oVSu", uma.address(1))

        self.assertEqual("335QrAenpWLGFRNZT7VpzbkT1bPzRUkWna", self.multisig_account.address(2))
        # Sort generates different address for this index
        self.assertEqual("3Qc7D1EiXhGdZo7szB2VpQUnbBx6hAWtzm", uma.address(2))

    def test_simple_account_testnet(self):
        master_key = MasterKey.from_seed(h2b("000102030405060708090a0b0c0d0e0f"), netcode='XTN')
        account_key = master_key.account_for_path("0H/1/2H")
        account = SimpleAccount(account_key)
        self.assertEqual('mgMy4vmqChGT8XeKPb1zD6RURWsiNmoNvR', account.current_address())
        account._provider = MySimpleTestnetProvider()
        self.assertEqual(1, len(account.spendables()))
        tx = account.tx([("mvccWwntgfQaj7TVYEw2C2avymxHwjixDz", 2000)])
        account.sign(tx)

    def test_simple_account_testnet_batch(self):
        master_key = MasterKey.from_seed(h2b("000102030405060708090a0b0c0d0e0f"), netcode='XTN')
        account_key = master_key.account_for_path("0H/1/2H")
        account = SimpleAccount(account_key)

        class MyProvider(BatchService):
            def spendables_for_addresses(self, addresses):
                results = {}
                for address in addresses:
                    if address == "mgMy4vmqChGT8XeKPb1zD6RURWsiNmoNvR":
                        results[address] =\
                            [Spendable(coin_value=10000,
                                       script=ScriptPayToAddress(bitcoin_address_to_hash160_sec(address, address_prefix_for_netcode('XTN'))).script(),
                                       tx_out_index=0, tx_hash=b'2'*32)]
                return results
        account._provider = MyProvider()
        self.assertEqual(1, len(account.spendables()))

    def test_simple_account_cache(self):
        account_key = self.master_key.account_for_path("0H/1/2H")
        account = SimpleAccount(account_key)
        self.assertEqual("1r1msgrPfqCMRAhg23cPBD9ZXH1UQ6jec", account.address(0, False))
        account1 = SimpleAccount(account_key, account.cache)
        self.assertEqual("1r1msgrPfqCMRAhg23cPBD9ZXH1UQ6jec", account1.address(0, False))

    def test_multisig_account(self):
        account_key = self.master_key.account_for_path("0H/1/2H")
        recover_key = self.master_key.account_for_path("0H/1/3H")
        oracle_key = self.master_key.account_for_path("0H/1/4H")
        keys = [account_key, recover_key, oracle_key]
        account = MultisigAccount(keys=keys, sort=False)

        # Create the redeem script for the provider
        secs = [key.subkey_for_path("0/0").sec() for key in keys]
        redeem_script = ScriptMultisig(2, secs)
        payto_script = ScriptPayToScript(encoding.hash160(redeem_script.script()))

        class MyProvider(object):
            def spendables_for_address(self, address):
                if address == "32pQeKJ8KzRfb3ox9Me8EHn3ud8xo6mqAu":
                    if address != payto_script.address():
                        raise ValueError()
                    return [Spendable(coin_value=10000,
                                      script=payto_script.script(),
                                      tx_out_index=0, tx_hash=b'2'*32)]
                else:
                    return []
        account._provider = MyProvider()
        account.set_lookahead(2)
        self.assertEqual(2, len(account.addresses()))
        self.assertEqual(6, len(account.addresses(True)))
        self.assertEqual("32pQeKJ8KzRfb3ox9Me8EHn3ud8xo6mqAu", account.address(0, False))
        self.assertEqual("3QdW9Lr7sX5M2XmsukWg87tXcM6bj6aTV4", account.current_change_address())
        self.assertEqual(10000, account.balance())
        tx = account.tx([("3FfiLhj1yXkXRFRRb9CMsMXBNZXQEv23Pi", 2000)])
        account.sign(tx)
        # Countersign
        multisigcore.local_sign(tx, [redeem_script], [oracle_key.subkey_for_path("0/0")])
        self.assertTrue(tx.is_signature_ok(0))

    def test_simple_account(self):
        account_key = self.master_key.account_for_path("0H/1/2H")
        account = SimpleAccount(account_key)

        account._provider = MySimpleProvider()
        account.set_lookahead(2)
        self.assertEqual(2, len(account.addresses()))
        self.assertEqual(6, len(account.addresses(True)))
        self.assertEqual("1r1msgrPfqCMRAhg23cPBD9ZXH1UQ6jec", account.address(0, False))
        self.assertEqual("1r1msgrPfqCMRAhg23cPBD9ZXH1UQ6jec", account.addresses()[0])
        self.assertEqual("1r1msgrPfqCMRAhg23cPBD9ZXH1UQ6jec", account.current_address())
        self.assertEqual("19Fi5VpcosH3CtCFjd5HyveM5c4Kecirza", account.current_change_address())
        self.assertEqual(10000, account.balance())
        spendables = account.spendables()
        self.assertEqual(1, len(spendables))
        tx = account.tx([("3FfiLhj1yXkXRFRRb9CMsMXBNZXQEv23Pi", 2000)])
        self.assertEqual(1, len(tx.txs_in))
        self.assertEqual(2, len(tx.txs_out))
        self.assertEqual(2000, tx.txs_out[0].coin_value)
        self.assertEqual(7000, tx.txs_out[1].coin_value)
        self.assertEqual(b'', tx.txs_in[0].script)
        self.assertEqual(b'2'*32, tx.txs_in[0].previous_hash)
        self.assertIsNotNone(account.tx([("3FfiLhj1yXkXRFRRb9CMsMXBNZXQEv23Pi", 9000)]))
        with self.assertRaises(InsufficientBalanceException) as e:
            account.tx([("3FfiLhj1yXkXRFRRb9CMsMXBNZXQEv23Pi", 9001)])
        self.assertEqual(10000, e.exception.balance)
        account.sign(tx)
        self.assertTrue(tx.is_signature_ok(0))
        self.assertEqual(["0/0"], tx.input_chain_paths())
        self.assertEqual([None, "1/0"], tx.output_chain_paths())

    def test_tx_serialize(self):
        account_key = self.master_key.account_for_path("0H/1/2H")
        account = SimpleAccount(account_key)

        account._provider = MySimpleProvider()
        account.set_lookahead(2)
        spendables = account.spendables()
        self.assertEqual(1, len(spendables))
        tx1 = account.tx([("3FfiLhj1yXkXRFRRb9CMsMXBNZXQEv23Pi", 2000)])
        tx = AccountTx.deserialize(tx1.serialize())
        self.assertEqual(1, len(tx.txs_in))
        self.assertEqual(2, len(tx.txs_out))
        self.assertEqual(2000, tx.txs_out[0].coin_value)
        self.assertEqual(7000, tx.txs_out[1].coin_value)
        self.assertEqual(b'', tx.txs_in[0].script)
        self.assertEqual(b'2'*32, tx.txs_in[0].previous_hash)
        account.sign(tx)
        self.assertTrue(tx.is_signature_ok(0))
        self.assertEqual(["0/0"], tx.input_chain_paths())
        self.assertEqual([None, "1/0"], tx.output_chain_paths())

    def test_next_address(self):
        account_key = self.master_key.account_for_path("0H/1/2H")
        account = SimpleAccount(account_key)
        self.assertEqual("1r1msgrPfqCMRAhg23cPBD9ZXH1UQ6jec", account.current_address())
        self.assertEqual("181yMj2Es6RNvoHgj6bX82r2Vm38rmHV8C", account.next_address())
        self.assertEqual("181yMj2Es6RNvoHgj6bX82r2Vm38rmHV8C", account.current_address())
        self.assertEqual("1AdEBCFQJHBzHKgWX517rQWCWwQ6qvYfAB", account.next_change_address())
        self.assertEqual("1AdEBCFQJHBzHKgWX517rQWCWwQ6qvYfAB", account.current_change_address())
        account1 = SimpleAccount(account_key, cache=account.cache)
        self.assertEqual("181yMj2Es6RNvoHgj6bX82r2Vm38rmHV8C", account1.current_address())
        self.assertEqual("1AdEBCFQJHBzHKgWX517rQWCWwQ6qvYfAB", account1.current_change_address())

    def test_rotate_address(self):
        account_key = self.master_key.account_for_path("0H/1/2H")
        account = SimpleAccount(account_key)
        first = "1r1msgrPfqCMRAhg23cPBD9ZXH1UQ6jec"
        first_change = "19Fi5VpcosH3CtCFjd5HyveM5c4Kecirza"
        self.assertEqual(first, account.current_address())
        self.assertEqual(first_change, account.current_change_address())
        tx = Tx(DEFAULT_VERSION, [], [TxOut(1, standard_tx_out_script("3FfiLhj1yXkXRFRRb9CMsMXBNZXQEv23Pi"))])
        account.rotate_addresses(tx)
        self.assertEqual("1r1msgrPfqCMRAhg23cPBD9ZXH1UQ6jec", account.current_address())
        tx = Tx(DEFAULT_VERSION, [], [TxOut(1, standard_tx_out_script(first)), TxOut(33, standard_tx_out_script(first_change))])
        self.assertTrue(account.rotate_addresses(tx))
        self.assertNotEqual(first, account.current_address())
        self.assertNotEqual(first_change, account.current_change_address())
