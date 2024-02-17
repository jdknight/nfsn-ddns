# SPDX-License-Identifier: BSD-2-Clause
# Copyright nfsn-ddns Contributors

from __future__ import annotations
from nfsn_ddns.defs import NFSN_DDNS_ENV_PREFIX
from nfsn_ddns.log import err
from nfsn_ddns.log import verbose
from nfsn_ddns.utils import str2bool
from pathlib import Path
from typing import TYPE_CHECKING
import os
import yaml

if TYPE_CHECKING:
    from argparse import Namespace
    from typing import Optional


class Config:
    def __init__(self) -> None:
        """
        nfsn-ddns configuration instance

        Holds the configuration state for an nfsn-ddns instance.
        """
        self.config = {}  # type: dict[str, str]

    def load(self, path: Path, *, expected: bool = False) -> bool:
        """
        load configuration information from a provided file

        This call will open a YAML configuration file and populate various
        configuration options. Options will be populated from content inside
        a `nfsn-ddns` key.

        Args:
            path: the path of the configuration file to load
            expected (optional): whether the provided path is expected to load

        Returns:
            whether a file was loaded
        """

        try:
            verbose(f'attempting to load configuration file: {path}')
            with path.open() as f:
                try:
                    raw_config = yaml.safe_load(f)
                    if 'nfsn-ddns' in raw_config:
                        self.config = raw_config['nfsn-ddns']
                        return True

                    err(f'invalid nfsn-ddns configuration: {path}')
                except yaml.YAMLError as e:
                    err(f'unable to load configuration file: {path}')
                    err(str(e))
        except FileNotFoundError:
            if expected:
                err(f'configuration file does not exist: {path}')
        except OSError as e:
            err(f'unable to load configuration file: {path}')
            err(str(e))

        return not expected

    def accept(self, args: Namespace) -> None:
        """
        accept configuration arguments into the configuration instance

        This call accepts arguments populated from a parsed argparse instance.
        Any existing options will be overridden by a newly set options.

        Args:
            args: the arguments
        """

        if args.api_login:
            self.config['api-login'] = args.api_login

        if args.api_token:
            self.config['api-token'] = args.api_token

        if args.cache:
            self.config['cache'] = 'true'

        if args.cache_days:
            self.config['cache-days'] = args.cache_days

        if args.cache_file:
            self.config['cache-file'] = args.cache_file

        if args.ddns_domain:
            self.config['domains'] = args.ddns_domain

        if args.no_cache:
            self.config['cache'] = 'false'

        if args.timeout:
            self.config['timeout'] = args.timeout

    def api_login(self) -> Optional[str]:
        """
        returns the configured api login value

        Returns:
            the api login value
        """
        return self._fetch('api-login')

    def api_token(self) -> Optional[str]:
        """
        returns the configured api token value

        Returns:
            the api token value
        """
        return self._fetch('api-token')

    def cache(self) -> Optional[bool]:
        """
        returns the configured cache state value

        Returns:
            the cache state value
        """
        raw_value = self._fetch('cache')
        if not raw_value:
            return None

        try:
            return str2bool(raw_value)
        except ValueError:
            return None

    def cache_days(self) -> Optional[int]:
        """
        returns the configured cache days value

        Returns:
            the days value
        """
        raw_value = self._fetch('cache-days')
        if not raw_value:
            return None

        try:
            return int(raw_value)
        except ValueError:
            return None

    def cache_file(self) -> Optional[Path]:
        """
        returns the configured cache file value

        Returns:
            the file value
        """
        raw_value = self._fetch('cache-file')
        if not raw_value:
            return None

        try:
            return Path(raw_value)
        except TypeError:
            return None

    def ddns_domains(self) -> Optional[list[str]]:
        """
        returns the configured ddns domains value

        Returns:
            the domains value
        """
        raw_domains = self._fetch('domains')

        if isinstance(raw_domains, list):
            domains = raw_domains
        elif isinstance(raw_domains, str):
            domains = raw_domains.split(';')
        else:
            domains = None

        return domains

    def nfsn_api_endpoint(self) -> Optional[str]:
        """
        returns the configured nfsn api endpoint value

        Returns:
            the endpoint value
        """
        return self._fetch('nfsn-api-endpoint')

    def myip_api_endpoints(self) -> Optional[list[str]]:
        """
        returns the configured myip api endpoints value

        Returns:
            the endpoints value
        """
        raw_endpoints = self._fetch('myip-api-endpoints')

        if isinstance(raw_endpoints, list):
            endpoints = raw_endpoints
        elif isinstance(raw_endpoints, str):
            endpoints = raw_endpoints.split(';')
        else:
            endpoints = None

        return endpoints

    def timeout(self) -> Optional[int]:
        """
        returns the configured timeout value

        Returns:
            the timeout value
        """
        raw_value = self._fetch('timeout')
        if not raw_value:
            return None

        try:
            return int(raw_value)
        except ValueError:
            return None

    def validate(self) -> bool:
        """
        validates required options for this configuration

        A subset of configuration options need to be set in order for the
        engine to operate as expected. For example, configuring the API
        credentials to interact with NFSN. This call will return whether
        the minimum configuration options has been set, and populate stderr
        with any detected issues.

        Returns:
            whether the configuration is valid
        """

        rv = True

        if not self.api_login():
            err('(config) missing api login value')
            rv = False

        if not self.api_token():
            err('(config) missing api token value')
            rv = False

        if not self.ddns_domains():
            err('(config) missing ddns domains value')
            rv = False

        return rv

    def _fetch(self, key: str, *, env: bool = True) -> Optional[str]:
        """
        fetch a specific key from the configuration

        This is a helper call used to acquire a known configuration for
        a specific "key" value. If a specific key's value is tracked, it
        will be returned. If not, fallback options that exist in the
        configured environment can be used. In all other cases, a `None`
        will be returned.

        Args:
            key: the configuration key
            env (optional): whether to fallback on the environment

        Returns:
            the key's value
        """

        value = self.config.get(key, None)

        if not value and env:
            env_key = key.upper().replace('-', '_')
            value = os.environ.get(f'{NFSN_DDNS_ENV_PREFIX}{env_key}', None)

        return value
