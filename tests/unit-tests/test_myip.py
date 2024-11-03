# SPDX-License-Identifier: BSD-2-Clause
# Copyright nfsn-ddns Contributors

from nfsn_ddns.myip import fetch_myipv4
from nfsn_ddns.myip import fetch_myipv6
from tests import NfsnDdnsTestCase
import responses


class TestMyIp(NfsnDdnsTestCase):
    @responses.activate
    def test_myip_fetch_address_invalid_unknown_data(self) -> None:
        expected_id = 'some-data'
        responses.get(
            url='https://example.com/ip',
            body=expected_id,
        )

        found_ip = fetch_myipv4(endpoints='https://example.com/ip')
        self.assertFalse(found_ip)

    @responses.activate
    def test_myip_fetch_address_unexpected_ipv4(self) -> None:
        expected_id = '203.0.113.1'
        responses.get(
            url='https://example.com/ip',
            body=expected_id,
        )

        found_ip = fetch_myipv6(endpoints='https://example.com/ip')
        self.assertFalse(found_ip)

    @responses.activate
    def test_myip_fetch_address_unexpected_ipv6(self) -> None:
        expected_id = '2001:db8::2'
        responses.get(
            url='https://example.com/ip',
            body=expected_id,
        )

        found_ip = fetch_myipv4(endpoints='https://example.com/ip')
        self.assertFalse(found_ip)

    @responses.activate
    def test_myip_fetch_address_valid_ipv4(self) -> None:
        expected_ip = '203.0.113.1'
        responses.get(
            url='https://example.com/ip',
            body=expected_ip,
        )

        found_ip = fetch_myipv4(endpoints='https://example.com/ip')
        self.assertEqual(found_ip, expected_ip)

    @responses.activate
    def test_myip_fetch_address_valid_ipv6(self) -> None:
        expected_ip = '2001:db8::1'
        responses.get(
            url='https://example.com/ip',
            body=expected_ip,
        )

        found_ip = fetch_myipv6(endpoints='https://example.com/ip')
        self.assertEqual(found_ip, expected_ip)

    @responses.activate
    def test_myip_multiset_failure(self) -> None:
        rsp1 = responses.get(
            url='https://example.com/ip1',
            body='',
        )

        rsp2 = responses.get(
            url='https://example.com/ip2',
            body='',
        )

        rsp3 = responses.get(
            url='https://example.org/ip3',
            body='',
        )

        endpoints = [
            'https://example.com/ip1',
            'https://example.com/ip2',
            'https://example.org/ip3',
        ]

        found_ip = fetch_myipv4(endpoints=endpoints)
        self.assertFalse(found_ip)
        self.assertEqual(rsp1.call_count, 1)
        self.assertEqual(rsp2.call_count, 1)
        self.assertEqual(rsp3.call_count, 1)

    @responses.activate
    def test_myip_multiset_find(self) -> None:
        expected_ip = '203.0.113.2'

        responses.get(
            url='https://example.com/ip1',
            body='',
        )

        responses.get(
            url='https://example.com/ip2',
            body='',
        )

        responses.get(
            url='https://example.org/ip3',
            body='',
        )

        responses.get(
            url='https://example.org/ip4',
            body=expected_ip,
        )

        endpoints = [
            'https://example.com/ip1',
            'https://example.com/ip2',
            'https://example.org/ip3',
            'https://example.org/ip4',
        ]

        found_ip = fetch_myipv4(endpoints=endpoints)
        self.assertEqual(found_ip, expected_ip)
