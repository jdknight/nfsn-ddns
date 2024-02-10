# SPDX-License-Identifier: BSD-2-Clause
# Copyright nfsn-ddns Contributors

from nfsn_ddns.utils import str2bool
from tests import NfsnDdnsTestCase


class TestUtilStr2Bool(NfsnDdnsTestCase):
    def test_util_str2bool_invalid(self) -> None:
        with self.assertRaises(ValueError):
            str2bool(None)

        with self.assertRaises(ValueError):
            str2bool(2)

        with self.assertRaises(ValueError):
            str2bool({})

    def test_util_str2bool_true(self) -> None:
        self.assertTrue(str2bool('on'))
        self.assertTrue(str2bool('ON'))
        self.assertTrue(str2bool('true'))
        self.assertTrue(str2bool('TRUE'))
        self.assertTrue(str2bool('yes'))
        self.assertTrue(str2bool('YES'))
        self.assertTrue(str2bool('1'))
        self.assertTrue(str2bool(1))

    def test_util_str2bool_false(self) -> None:
        self.assertFalse(str2bool('false'))
        self.assertFalse(str2bool('FALSE'))
        self.assertFalse(str2bool('no'))
        self.assertFalse(str2bool('NO'))
        self.assertFalse(str2bool('off'))
        self.assertFalse(str2bool('OFF'))
        self.assertFalse(str2bool('0'))
        self.assertFalse(str2bool(0))
