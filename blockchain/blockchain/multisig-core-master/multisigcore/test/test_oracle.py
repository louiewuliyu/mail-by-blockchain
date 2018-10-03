import io
import json

from httmock import HTTMock
import dateutil.parser

from multisigcore.oracle import OracleError, OracleDeferralException, OracleRejectionException, OracleLockoutException, \
    PersonalInformation
from multisigcore.testing import *


__author__ = 'devrandom'

import unittest
from multisigcore import Oracle, local_sign

class OracleTest(unittest.TestCase):
    def setUp(self):
        self.wallet_private_key = MasterKey.from_seed("aaa-2015-02-10".encode('utf8'))
        self.tx_db = dict()
        self.input_tx = Tx.tx_from_hex("0100000001d7e5d290d1363f9a3a1ee992d729f5e2f6938539e1eb6fd98ddd32f5211b66b8010000006a473044022043ac09592090ec32e75fe104aa97e87d31852d23ee17595659ea82e9e177822b0220727a37d1f93a088a99f907f924b92f2938b3a1e5093af32ee854382275fe06c1012103070454c3e8fea7c8e7e4a9c4d4a15e7e3088a0555e2ed303ec25d0f9bb0a75a6ffffffff02e09304000000000017a9141bbf6712630dd01fab4e70ac91a06925d138f27387d2906406000000001976a9149fe455808b8f32c84f4c96db7865cfb2475bffbc88ac00000000")
        self.tx_db[self.input_tx.hash()] = self.input_tx
        self.account = make_multisig_account()
        self.oracle = Oracle(self.account, tx_db=self.tx_db)

    def make_partially_signed_tx(self):
        f = io.BytesIO(h2b(
            "01000000019cb9e92cd3f91087852382150f19b5d99259be47106d860055d1afb8110022250000000000ffffffff01d06c04000000000017a914f155ba65bdb30930da320ec51a0d6c913dfce06b8700000000e09304000000000017a9141bbf6712630dd01fab4e70ac91a06925d138f27387"))
        unsigned = Tx.parse(f)
        unsigned.parse_unspents(f)
        script = self.account.script_for_path(TEST_PATH)
        child_key = self.wallet_private_key.subkey_for_path(TEST_PATH)
        local_sign(unsigned, [script], [child_key])
        return unsigned

    def test_pointers(self):
        self.assertEqual([self.oracle], self.account.oracles)

    def test_sign_request(self):
        # generated with `tx -i 34DjTcNWGReJV4xx7R1AWK7FTz3xMwMcjA  3Ph5UGYHCyvYFQifw76T8iqKL9EkGKDBMz/100000 -o tx.hex`
        unsigned = self.make_partially_signed_tx()
        req = self.oracle._create_oracle_request([TEST_PATH], [], None, unsigned)
        self.assertEqual("01000000019cb9e92cd3f91087852382150f19b5d99259be47106d860055d1afb81100222500000000b500473044022042b1b79675985a46e021c056708420f0bade9cdc4b336b55c53d0f22488f34e40220795cbd8291f083ea32eb29e8ace895852823611927b9ba7e94a333f022f5dd4301004c69522102fa0e06db47e8924274c670503238db30367d11ccaca00d385ac370fed93578d2210379014532a465b19fcf1ead9921488274821fd58178542b2aa54007bcc5a29d34210381c235ee18d9e85e3b28200200df3a2276c6b9473f18946ef8740ccaebfa4b1e53aeffffffff01d06c04000000000017a914f155ba65bdb30930da320ec51a0d6c913dfce06b8700000000",
                         req['transaction']['bytes'])

    def make_partially_signed_tx_with_change(self):
        # generated with `tx -i 34DjTcNWGReJV4xx7R1AWK7FTz3xMwMcjA  3Ph5UGYHCyvYFQifw76T8iqKL9EkGKDBMz/90000 34DjTcNWGReJV4xx7R1AWK7FTz3xMwMcjA/200000 -o tx1.hex`
        # signing would be with `digital_oracle sign P:aaa-2015-02-10 P:bbb tx1.hex -i 0/0/1 -c - 0/0/1`
        f = io.BytesIO(h2b(
            "01000000019cb9e92cd3f91087852382150f19b5d99259be47106d860055d1afb8110022250000000000ffffffff02905f01000000000017a914f155ba65bdb30930da320ec51a0d6c913dfce06b87400d03000000000017a9141bbf6712630dd01fab4e70ac91a06925d138f2738700000000e09304000000000017a9141bbf6712630dd01fab4e70ac91a06925d138f27387"))
        unsigned = Tx.parse(f)
        unsigned.parse_unspents(f)
        script = self.account.script_for_path(TEST_PATH)
        child_key = self.wallet_private_key.subkey_for_path(TEST_PATH)
        local_sign(unsigned, [script], [child_key])
        return unsigned

    def test_sign_request_change(self):
        unsigned = self.make_partially_signed_tx_with_change()
        req = self.oracle._create_oracle_request([TEST_PATH], [None, TEST_PATH], None, unsigned)
        self.assertEqual("01000000019cb9e92cd3f91087852382150f19b5d99259be47106d860055d1afb81100222500000000b600483045022100a90e9e7e4ddc7de0e8f39166e40819a8c99a1b68389cf0e6e3518d592e3e271502201eab29e5069988188886827a31248faacecb723c28da228626b1e77f080a2e7701004c69522102fa0e06db47e8924274c670503238db30367d11ccaca00d385ac370fed93578d2210379014532a465b19fcf1ead9921488274821fd58178542b2aa54007bcc5a29d34210381c235ee18d9e85e3b28200200df3a2276c6b9473f18946ef8740ccaebfa4b1e53aeffffffff02905f01000000000017a914f155ba65bdb30930da320ec51a0d6c913dfce06b87400d03000000000017a9141bbf6712630dd01fab4e70ac91a06925d138f2738700000000",
                         req['transaction']['bytes'])
        JSON = '{"walletAgent": "multisig-core-0.01", "transaction": {"outputChainPaths": [null, "0/0/1"], "bytes": "01000000019cb9e92cd3f91087852382150f19b5d99259be47106d860055d1afb81100222500000000b600483045022100a90e9e7e4ddc7de0e8f39166e40819a8c99a1b68389cf0e6e3518d592e3e271502201eab29e5069988188886827a31248faacecb723c28da228626b1e77f080a2e7701004c69522102fa0e06db47e8924274c670503238db30367d11ccaca00d385ac370fed93578d2210379014532a465b19fcf1ead9921488274821fd58178542b2aa54007bcc5a29d34210381c235ee18d9e85e3b28200200df3a2276c6b9473f18946ef8740ccaebfa4b1e53aeffffffff02905f01000000000017a914f155ba65bdb30930da320ec51a0d6c913dfce06b87400d03000000000017a9141bbf6712630dd01fab4e70ac91a06925d138f2738700000000", "inputScripts": ["522102fa0e06db47e8924274c670503238db30367d11ccaca00d385ac370fed93578d2210379014532a465b19fcf1ead9921488274821fd58178542b2aa54007bcc5a29d34210381c235ee18d9e85e3b28200200df3a2276c6b9473f18946ef8740ccaebfa4b1e53ae"], "masterKeys": ["xpub661MyMwAqRbcFqtR38s6kVQudQxKpHzNJyWEXmz2TnuDoR8FpZR7EuL158B5QDaYvxCfp3LAEa8VwdtxNgKHNha4JKqGrqkzBGboJFwgyrR", "xpub661MyMwAqRbcGmRK6wKJrfMXoenZ86PMUfBWNvmmp5c51PyyzjY7yJL9venRUYqmSqNo7iGqHbVWkTVYzY2drw57vr45iHxV7NsAqF4ZWg5"], "chainPaths": ["0/0/1"], "inputTransactions": ["0100000001d7e5d290d1363f9a3a1ee992d729f5e2f6938539e1eb6fd98ddd32f5211b66b8010000006a473044022043ac09592090ec32e75fe104aa97e87d31852d23ee17595659ea82e9e177822b0220727a37d1f93a088a99f907f924b92f2938b3a1e5093af32ee854382275fe06c1012103070454c3e8fea7c8e7e4a9c4d4a15e7e3088a0555e2ed303ec25d0f9bb0a75a6ffffffff02e09304000000000017a9141bbf6712630dd01fab4e70ac91a06925d138f27387d2906406000000001976a9149fe455808b8f32c84f4c96db7865cfb2475bffbc88ac00000000"]}}'
        self.maxDiff = None
        self.assertEqual(json.loads(json.dumps(req)), json.loads(JSON))

    def test_sign(self):
        self._request = None
        def digitaloracle_mock(url, request):
            self._request = request
            return {
                "status_code": 200,
                "content": json.dumps({"result": "success", "now": "2010-01-01 00:00:00Z", "spendId": "aaa"}).encode("utf8")
            }

        with HTTMock(digitaloracle_mock):
            unsigned = self.make_partially_signed_tx_with_change()
            payto = self.account.payto_for_path(TEST_PATH)
            verifications = {"otp": "123456"}
            res = self.oracle.sign_with_paths(unsigned, [TEST_PATH], [None, TEST_PATH], verifications=verifications)
            req = json.loads(self._request.body)
            self.assertEqual(req['transaction']['chainPaths'], ["0/0/1"])
            self.assertEqual(req['transaction']['outputChainPaths'], [None, "0/0/1"])
            self.assertEqual(req['verifications'], verifications)
            self.assertEqual("01000000019cb9e92cd3f91087852382150f19b5d99259be47106d860055d1afb81100222500000000b600483045022100a90e9e7e4ddc7de0e8f39166e40819a8c99a1b68389cf0e6e3518d592e3e271502201eab29e5069988188886827a31248faacecb723c28da228626b1e77f080a2e7701004c69522102fa0e06db47e8924274c670503238db30367d11ccaca00d385ac370fed93578d2210379014532a465b19fcf1ead9921488274821fd58178542b2aa54007bcc5a29d34210381c235ee18d9e85e3b28200200df3a2276c6b9473f18946ef8740ccaebfa4b1e53aeffffffff02905f01000000000017a914f155ba65bdb30930da320ec51a0d6c913dfce06b87400d03000000000017a9141bbf6712630dd01fab4e70ac91a06925d138f2738700000000",
                             req['transaction']['bytes'])
            self.assertEqual(res.spend_id, "aaa")

    def test_sign_fail(self):
        self._request = None
        def digitaloracle_mock(url, request):
            self._request = request
            return {
                "status_code": 400,
                "content": json.dumps({"error": "failed"}).encode("utf8")
            }

        with HTTMock(digitaloracle_mock):
            unsigned = self.make_partially_signed_tx_with_change()
            payto = self.account.payto_for_path(TEST_PATH)
            try:
                self.oracle.sign_with_paths(unsigned, [TEST_PATH], [None, TEST_PATH])
                self.fail()
            except OracleError as e:
                pass #expected

    def test_sign_defer(self):
        self._request = None
        until = "2010-01-01 00:01:00Z"

        def digitaloracle_mock(url, request):
            self._request = request
            return {
                "status_code": 200,
                "content": json.dumps({"result": "deferred",
                                       "now": "2010-01-01 00:00:00Z",
                                       "spendId": "aaa",
                                       "deferral": {"reason": "delay", "until": until, "verifications":["otp"]}}).encode("utf8")
            }

        with HTTMock(digitaloracle_mock):
            unsigned = self.make_partially_signed_tx_with_change()
            payto = self.account.payto_for_path(TEST_PATH)
            try:
                self.oracle.sign_with_paths(unsigned, [TEST_PATH], [None, TEST_PATH])
                self.fail()
            except OracleDeferralException as e:
                self.assertEquals(e.until, dateutil.parser.parse(until))
                self.assertEquals(e.verifications, ["otp"])

    def test_sign_rejected(self):
        self._request = None
        until = "2010-01-01 00:01:00Z"

        def digitaloracle_mock(url, request):
            self._request = request
            return {
                "status_code": 200,
                "content": json.dumps({"result": "rejected",
                                       "now": "2010-01-01 00:00:00Z"}).encode("utf8")
            }

        with HTTMock(digitaloracle_mock):
            unsigned = self.make_partially_signed_tx_with_change()
            payto = self.account.payto_for_path(TEST_PATH)
            try:
                self.oracle.sign_with_paths(unsigned, [TEST_PATH], [None, TEST_PATH])
                self.fail()
            except OracleRejectionException as e:
                pass # expected

    def test_sign_lockout(self):
        self._request = None
        until = "2010-01-01 00:01:00Z"

        def digitaloracle_mock(url, request):
            self._request = request
            return {
                "status_code": 200,
                "content": json.dumps({"result": "locked",
                                       "now": "2010-01-01 00:00:00Z"}).encode("utf8")
            }

        with HTTMock(digitaloracle_mock):
            unsigned = self.make_partially_signed_tx_with_change()
            payto = self.account.payto_for_path(TEST_PATH)
            try:
                self.oracle.sign_with_paths(unsigned, [TEST_PATH], [None, TEST_PATH])
                self.fail()
            except OracleLockoutException as e:
                pass # expected

    def test_create(self):
        new_account = make_incomplete_multisig_account()
        oracle = Oracle(new_account)
        calls = ['email']
        parameters = {
            "levels": [
                {"asset": "BTC", "period": 60, "value": 0.001},
                {"delay": 0, "calls": calls}
            ]
        }
        self._request = None

        def digitaloracle_mock(url, request):
            self._request = request
            return {
                "status_code": 200,
                "content": json.dumps({"result": "success", "now": "2010-01-01 00:00:00Z", "keys": {"default": [oracle_key.hwif()]}}).encode('utf8')
            }

        with HTTMock(digitaloracle_mock):
            personal_info = PersonalInformation(email="a@b.com")
            oracle.create(parameters, personal_info)
            self.assertTrue(new_account.complete)
            self.assertEqual(self.account.address(111), new_account.address(111))

    def test_verify(self):
        new_account = make_incomplete_multisig_account()
        oracle = Oracle(new_account)
        calls = ['email']
        self._request = None
        def digitaloracle_mock(url, request):
            self._request = request
            return {
                "status_code": 200,
                "content": json.dumps({"result": "success", "now": "2010-01-01 00:00:00Z"}).encode("utf8")
            }

        with HTTMock(digitaloracle_mock):
            personal_info = PersonalInformation(email="a@b.com", phone="+14155551212")
            oracle.verify_personal_information(personal_info, call="phone", callback="http://a.com/")