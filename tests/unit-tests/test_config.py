# SPDX-License-Identifier: BSD-2-Clause
# Copyright nfsn-ddns Contributors

from __future__ import annotations
from nfsn_ddns.config import Config
from pathlib import Path
from tests import NfsnDdnsTestCase
from typing import TYPE_CHECKING
import os

if TYPE_CHECKING:
    from typing import TypeVar
    from typing import Union

    T = TypeVar('T', bound='NfsnDdnsTestCase')


class MockedArgs(dict):
    def __getattr__(self, name: str) -> Union[None, str]:
        if name in self:
            return self[name]

        return None

    def __setattr__(self, name: str, value: Union[None, str]) -> None:
        self[name] = value


class TestConfiguration(NfsnDdnsTestCase):
    @classmethod
    def setUpClass(cls: type[T]) -> None:
        test_dir = Path(os.path.realpath(__file__)).parent
        cls.dataset = test_dir / 'assets'

    def setUp(self) -> None:
        self.cfg = Config()

    def test_config_none(self) -> None:
        self.assertIsNone(self.cfg.api_login())
        self.assertIsNone(self.cfg.api_token())
        self.assertIsNone(self.cfg.cache())
        self.assertIsNone(self.cfg.cache_days())
        self.assertIsNone(self.cfg.cache_file())
        self.assertIsNone(self.cfg.ddns_domains())
        self.assertIsNone(self.cfg.nfsn_api_endpoint())
        self.assertIsNone(self.cfg.myip_api_endpoints())
        self.assertIsNone(self.cfg.timeout())

    def test_config_args_api_login(self) -> None:
        args = MockedArgs()
        args.api_login = 'aqua-platinum-pekingese'
        self.cfg.accept(args)
        self.assertEqual(self.cfg.api_login(), args.api_login)

    def test_config_args_api_token(self) -> None:
        args = MockedArgs()
        args.api_token = 'navy-brass-greyhound'  # noqa: S105
        self.cfg.accept(args)
        self.assertEqual(self.cfg.api_token(), args.api_token)

    def test_config_args_cache(self) -> None:
        args = MockedArgs()
        args.cache = True
        self.cfg.accept(args)
        self.assertEqual(self.cfg.cache(), args.cache)

    def test_config_args_cache_days(self) -> None:
        args = MockedArgs()
        args.cache_days = 20
        self.cfg.accept(args)
        self.assertEqual(self.cfg.cache_days(), args.cache_days)

    def test_config_args_cache_file(self) -> None:
        args = MockedArgs()
        args.cache_file = Path('maroon-bronzeai-redale')
        self.cfg.accept(args)
        self.assertEqual(self.cfg.cache_file(), args.cache_file)

    def test_config_args_ddns_domain(self) -> None:
        args = MockedArgs()
        args.ddns_domain = [
            'tellow-titanium-labrador',
            'purple-zinc-labrador',
        ]
        self.cfg.accept(args)
        self.assertEqual(self.cfg.ddns_domains(), args.ddns_domain)

    def test_config_args_timeout(self) -> None:
        args = MockedArgs()
        args.timeout = 4
        self.cfg.accept(args)
        self.assertEqual(self.cfg.timeout(), args.timeout)

    def test_config_env_api_login(self) -> None:
        expected = 'green-nickel-fox-terrier'
        os.environ['NFSN_DDNS_API_LOGIN'] = expected
        self.assertEqual(self.cfg.api_login(), expected)

    def test_config_env_api_token(self) -> None:
        expected = 'black-nickel-greyhound'
        os.environ['NFSN_DDNS_API_TOKEN'] = expected
        self.assertEqual(self.cfg.api_token(), expected)

    def test_config_env_cache(self) -> None:
        expected = True
        os.environ['NFSN_DDNS_CACHE'] = '1'
        self.assertEqual(self.cfg.cache(), expected)

    def test_config_env_cache_days(self) -> None:
        expected = 34
        os.environ['NFSN_DDNS_CACHE_DAYS'] = '34'
        self.assertEqual(self.cfg.cache_days(), expected)

    def test_config_env_cache_file(self) -> None:
        expected = Path('green-zinc-siberian-husky')
        os.environ['NFSN_DDNS_CACHE_FILE'] = str(expected)
        self.assertEqual(self.cfg.cache_file(), expected)

    def test_config_env_ddns_domains(self) -> None:
        value = 'lime-nickel-boxer;white-silver-chihuahua'
        expected = [
            'lime-nickel-boxer',
            'white-silver-chihuahua',
        ]
        os.environ['NFSN_DDNS_DOMAINS'] = value
        self.assertEqual(self.cfg.ddns_domains(), expected)

    def test_config_env_nfsn_api_endpoint(self) -> None:
        expected = 'fuschia-aluminium-chow-chow'
        os.environ['NFSN_DDNS_NFSN_API_ENDPOINT'] = expected
        self.assertEqual(self.cfg.nfsn_api_endpoint(), expected)

    def test_config_env_myip_api_endpoints(self) -> None:
        value = 'maroon-copper-hound'
        expected = [
            'maroon-copper-hound',
        ]
        os.environ['NFSN_DDNS_MYIP_API_ENDPOINTS'] = value
        self.assertListEqual(self.cfg.myip_api_endpoints(), expected)

        value = 'olive-mercury-spitz;gray-gold-dachshund'
        expected = [
            'olive-mercury-spitz',
            'gray-gold-dachshund',
        ]
        os.environ['NFSN_DDNS_MYIP_API_ENDPOINTS'] = value
        self.assertListEqual(self.cfg.myip_api_endpoints(), expected)

    def test_config_env_timeout(self) -> None:
        expected = 2
        os.environ['NFSN_DDNS_TIMEOUT'] = '2'
        self.assertEqual(self.cfg.timeout(), expected)

    def test_config_file_default(self) -> None:
        fname = self.dataset / 'sample.yaml'
        loaded = self.cfg.load(fname, expected=True)
        self.assertTrue(loaded)

        self.assertEqual(self.cfg.api_login(), 'my-api-login')
        self.assertEqual(self.cfg.api_token(), 'my-api-token')
        self.assertEqual(self.cfg.cache(), True)
        self.assertEqual(self.cfg.cache_days(), 2)
        self.assertEqual(self.cfg.cache_file(), Path('my-cache-file'))
        self.assertEqual(self.cfg.ddns_domains(), [
            'my-record1.my-domain1',
            'my-record2.my-domain2',
        ])
        self.assertEqual(self.cfg.nfsn_api_endpoint(), 'my-nfsn-api-endpoint')
        self.assertListEqual(self.cfg.myip_api_endpoints(), [
            'my-myip-api-endpoint-1',
            'my-myip-api-endpoint-2',
            'my-myip-api-endpoint-3',
        ])
        self.assertEqual(self.cfg.timeout(), 10)

    def test_config_file_invalid(self) -> None:
        fname = self.dataset / 'invalid.yaml'
        loaded = self.cfg.load(fname, expected=True)
        self.assertFalse(loaded)

    def test_config_file_missing(self) -> None:
        fname = self.dataset / 'missing.yaml'
        loaded = self.cfg.load(fname, expected=True)
        self.assertFalse(loaded)
