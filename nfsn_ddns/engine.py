# SPDX-License-Identifier: BSD-2-Clause
# Copyright nfsn-ddns Contributors

from __future__ import annotations
from datetime import datetime
from datetime import timezone
from enum import IntEnum
from nfsn_ddns.auth import NfsnAuth
from nfsn_ddns.config import Config
from nfsn_ddns.defs import API_DNS_ENDPOINT
from nfsn_ddns.defs import Action
from nfsn_ddns.defs import DEFAULT_CACHE_DAYS
from nfsn_ddns.defs import DEFAULT_CACHE_FILES
from nfsn_ddns.defs import DEFAULT_CFG_FILE
from nfsn_ddns.defs import DEFAULT_TIMEOUT
from nfsn_ddns.defs import MAX_CACHE_DAYS
from nfsn_ddns.defs import MAX_TIMEOUT
from nfsn_ddns.defs import MIN_CACHE_DAYS
from nfsn_ddns.defs import MIN_TIMEOUT
from nfsn_ddns.log import err
from nfsn_ddns.log import log
from nfsn_ddns.log import success
from nfsn_ddns.log import verbose
from nfsn_ddns.log import warn
from nfsn_ddns.myip import fetch_myip
from pathlib import Path
from requests.exceptions import HTTPError
from typing import TYPE_CHECKING
import os
import requests
import sys

if TYPE_CHECKING:
    from argparse import Namespace


class EngineState(IntEnum):
    # engine has executed as expected
    OK = 0
    # engine has detected a bad configuration
    BAD_CONFIG = 1
    # failure to fetch "my-ip" when running the engine
    MYIP_FETCH_FAILURE = 2
    # failure to talk with nfsn api (first call)
    NFSN_API_FAILURE_INIT = 3
    # failure to talk with nfsn api (n+1 calls)
    NFSN_API_FAILURE = 4


def engine(args: Namespace) -> int:
    """
    the nfsn-ddns engine

    Args:
        args: arguments provided at runtime

    Returns:
        the exit code
    """

    # prepare configuration
    cfg = Config()

    cfg_file = args.cfg if args.cfg else DEFAULT_CFG_FILE
    if not cfg.load(cfg_file, expected=args.cfg):
        return EngineState.BAD_CONFIG

    cfg.accept(args)

    if not cfg.validate():
        return EngineState.BAD_CONFIG

    api_endpoint = cfg.nfsn_api_endpoint()
    api_login = cfg.api_login()
    api_token = cfg.api_token()
    allow_caching = cfg.cache()
    cache_days = cfg.cache_days()
    cache_file = cfg.cache_file()
    ddns_domains = cfg.ddns_domains()
    timeout = cfg.timeout()

    # verified via cfg.validate()
    assert isinstance(api_login, str)
    assert isinstance(api_token, str)
    assert isinstance(ddns_domains, list)

    if sys.platform != 'win32':
        uid = os.getuid()
    else:
        uid = 1000

    if not api_endpoint:
        api_endpoint = API_DNS_ENDPOINT

    if cache_days is None:
        cache_days = DEFAULT_CACHE_DAYS
    elif cache_days < MIN_CACHE_DAYS:
        cache_days = MIN_CACHE_DAYS
    elif cache_days > MAX_CACHE_DAYS:
        cache_days = MAX_CACHE_DAYS

    cache_files = [cache_file] if cache_file else DEFAULT_CACHE_FILES

    if timeout is None:
        timeout = DEFAULT_TIMEOUT
    elif timeout < MIN_TIMEOUT:
        timeout = MIN_TIMEOUT
    elif timeout > MAX_TIMEOUT:
        timeout = MAX_TIMEOUT

    token_value = '(set)' if api_token else '(noset)'
    cache_file_value = cache_file if cache_file else '(default)'
    verbose(f'(config) api-endpoint: {api_endpoint}')
    verbose(f'(config) api-login: {api_login}')
    verbose(f'(config) api-token: {token_value}')
    verbose(f'(config) caching: {allow_caching}')
    verbose(f'(config) cache-days: {cache_days}')
    verbose(f'(config) cache-file: {cache_file_value}')
    verbose(f'(config) domains: {ddns_domains}')
    verbose(f'(config) timeout: {timeout}')

    # load any previously cached ip
    cached_ip = None
    if allow_caching:
        # find the first available file
        found_cache_file = None
        for cache_file_entry in cache_files:
            cache_file = Path(str(cache_file_entry).format(uid=uid))
            if cache_file.is_file():
                found_cache_file = cache_file
                break

        if found_cache_file:
            try:
                # if the cache file has not been updated in over a day,
                # consider it stale
                verbose(f'checking if cache file is stale: {found_cache_file}')
                mtime = found_cache_file.stat().st_mtime
                modified_dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
                duration = datetime.now(tz=timezone.utc) - modified_dt
                stale = duration.days >= cache_days

                if not stale:
                    remaining = cache_days - duration.days
                    verbose(f'cache not stale for another {remaining} days')
                    verbose('attempting to load cached ip from file')
                    with found_cache_file.open() as f:
                        cached_ip = f.read()
            except OSError:
                pass

    # acquire the known external ip address for this instance
    active_ip = ''

    if not args.action or args.action == Action.IP:
        endpoints = cfg.myip_api_endpoints()
        active_ip = fetch_myip(endpoints=endpoints, timeout=timeout)
        if not active_ip:
            return EngineState.MYIP_FETCH_FAILURE

    if args.action == Action.IP:
        success(f'detected ip: {active_ip}')
        return EngineState.OK

    # if the active ip matches the cached ip, we may not have to interact
    # with nfsn's api
    if allow_caching and cached_ip == active_ip:
        verbose('cached public ip matches detected; stopping')
        return EngineState.OK

    # prepare interaction with nfsn api endpoint
    session = requests.session()
    session.auth = NfsnAuth(api_login, api_token)

    for ddns_entry in ddns_domains:
        resource, _, tld = ddns_entry.rpartition('.')
        ddns_record, _, domain = resource.rpartition('.')
        ddns_domain = f'{domain}.{tld}'
        verbose('processing ddns entry...')
        verbose(f'ddns-domain: {ddns_domain}')
        verbose(f'ddns-record: {ddns_record}')

        # api endpoint for this domain
        base_url = f'{api_endpoint}/{ddns_domain}'

        # query the dns record for the existing ip address (if any)
        verbose(f'querying dns record: {ddns_record}')
        opts = {
            'name': ddns_record,
        }
        target_url = f'{base_url}/listRRs'
        verbose(f'(request) {target_url}')
        rsp = session.post(target_url, data=opts, timeout=timeout)
        try:
            rsp.raise_for_status()
        except HTTPError as e:
            err(f'failed to query the dns record\n{e}')
            return EngineState.NFSN_API_FAILURE_INIT

        if args.action == Action.CHECK:
            success('verified connection with nfsn')
            return EngineState.OK

        try:
            # if we have a dns record, check its value and see if it matches
            # the known external address
            rsp_data = rsp.json()
            if rsp_data:
                persisted_ip = rsp_data[0].get('data')

                if not persisted_ip:
                    err('invalid response from api (no data)')
                elif persisted_ip == active_ip:
                    verbose('ddns record matches external address')
                else:
                    verbose(f'ip do not match for record: {ddns_record}')
                    opts = {
                        'name': ddns_record,
                        'type': 'A',
                        'data': active_ip,
                    }
                    target_url = f'{base_url}/replaceRR'
                    verbose(f'(request) {target_url}')
                    rsp = session.post(target_url, data=opts, timeout=timeout)
                    rsp.raise_for_status()
                    log(f'record has been updated with new ip: {active_ip}')

            # we do not have a ddns record setup; add it now
            else:
                warn(f'no record found ({ddns_record}); creating a new one...')
                opts = {
                    'name': ddns_record,
                    'type': 'A',
                    'data': active_ip,
                }
                target_url = f'{base_url}/addRR'
                verbose(f'(request) {target_url}')
                rsp = session.post(target_url, data=opts, timeout=timeout)
                rsp.raise_for_status()
        except HTTPError as e:
            err(f'failed to query the dns record\n{e}')
            return EngineState.NFSN_API_FAILURE

    # save the newly detected ip if it has changed
    if allow_caching and cached_ip != active_ip:
        for cache_file_entry in cache_files:
            cache_file = Path(str(cache_file_entry).format(uid=uid))

            try:
                cache_container = cache_file.parent
                if not cache_container.exists():
                    verbose(f'preparing cache container: {cache_container}')
                    cache_container.mkdir(parents=True)

                verbose(f'persisting ip ({active_ip}) to cache: {cache_file}')
                with cache_file.open('w') as f:
                    f.write(active_ip)

                # if we are able to write to this catch file, we are done!
                break
            except OSError:
                pass

    return EngineState.OK
