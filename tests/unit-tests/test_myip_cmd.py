# SPDX-License-Identifier: BSD-2-Clause
# Copyright nfsn-ddns Contributors

from __future__ import annotations
from nfsn_ddns.myip_cmd import fetch_myipv4_cmd
from nfsn_ddns.myip_cmd import fetch_myipv6_cmd
from pathlib import Path
from tests import NfsnDdnsTestCase
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypeVar

    T = TypeVar('T', bound='NfsnDdnsTestCase')


class TestMyIpCmd(NfsnDdnsTestCase):
    @classmethod
    def setUpClass(cls: type[T]) -> None:
        test_dir = Path(__file__).parent
        cls.assets = test_dir / 'assets'

    def test_myip_cmd_fetch_args(self) -> None:
        expected_ip = '203.0.113.45'
        cmd = f'python {self.assets / "fetch-ipv4.py"} --some-arg'

        found_ip = fetch_myipv4_cmd(cmd)
        self.assertEqual(found_ip, expected_ip)

    def test_myip_cmd_fetch_bad_data(self) -> None:
        cmd = f'python {self.assets / "fetch-bad-ip.py"}'

        found_ip = fetch_myipv4_cmd(cmd)
        self.assertFalse(found_ip)

    def test_myip_cmd_fetch_format_keyvalue(self) -> None:
        expected_ip = '203.0.113.47'
        cmd = f'python {self.assets / "fetch-ip-format-keyvalue.py"}'

        found_ip = fetch_myipv4_cmd(cmd)
        self.assertEqual(found_ip, expected_ip)

    def test_myip_cmd_fetch_format_wrapped(self) -> None:
        expected_ip = '2001:db8::4'
        cmd = f'python {self.assets / "fetch-ip-format-wrapped.py"}'

        found_ip = fetch_myipv6_cmd(cmd)
        self.assertEqual(found_ip, expected_ip)

    def test_myip_cmd_fetch_multiple(self) -> None:
        expected_ipv4 = '203.0.113.63'
        expected_ipv6 = '2001:db8::2'
        cmd = f'python {self.assets / "fetch-ip-both.py"}'

        found_ip = fetch_myipv4_cmd(cmd)
        self.assertEqual(found_ip, expected_ipv4)

        found_ip = fetch_myipv6_cmd(cmd)
        self.assertEqual(found_ip, expected_ipv6)

    def test_myip_cmd_fetch_no_data(self) -> None:
        cmd = f'python {self.assets / "fetch-no-data.py"}'

        found_ip = fetch_myipv4_cmd(cmd)
        self.assertFalse(found_ip)

    def test_myip_cmd_fetch_unexpected_ipv4(self) -> None:
        cmd = f'python {self.assets / "fetch-ipv4.py"}'

        found_ip = fetch_myipv6_cmd(cmd)
        self.assertFalse(found_ip)

    def test_myip_cmd_fetch_unexpected_ipv6(self) -> None:
        cmd = f'python {self.assets / "fetch-ipv6.py"}'

        found_ip = fetch_myipv4_cmd(cmd)
        self.assertFalse(found_ip)

    def test_myip_cmd_fetch_valid_ipv4(self) -> None:
        expected_ip = '203.0.113.45'
        cmd = f'python {self.assets / "fetch-ipv4.py"}'

        found_ip = fetch_myipv4_cmd(cmd)
        self.assertEqual(found_ip, expected_ip)

    def test_myip_cmd_fetch_valid_ipv6(self) -> None:
        expected_ip = '2001:db8::57'
        cmd = f'python {self.assets / "fetch-ipv6.py"}'

        found_ip = fetch_myipv6_cmd(cmd)
        self.assertEqual(found_ip, expected_ip)
