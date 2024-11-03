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
from nfsn_ddns.myip import fetch_myipv4
from nfsn_ddns.myip import fetch_myipv6
from nfsn_ddns.myip_cmd import fetch_myipv4_cmd
from nfsn_ddns.myip_cmd import fetch_myipv6_cmd
from pathlib import Path
from requests.exceptions import HTTPError
from typing import TYPE_CHECKING
import json
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
    ipv4 = cfg.ipv4()
    ipv6 = cfg.ipv6()
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

    # query ipv4 by default is not configured
    if ipv4 is None:
        ipv4 = True

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
    verbose(f'(config) ipv4: {ipv4}')
    verbose(f'(config) ipv6: {ipv6}')
    verbose(f'(config) timeout: {timeout}')

    # ensure we have at least one operating mode
    if args.action != Action.CHECK and not ipv4 and not ipv6:
        err('both ipv4 and ipv6 querying is disabled by configuration')
        return EngineState.BAD_CONFIG

    # load any previously cached ip
    cached_data = {}
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
                        cached_data = json.load(f)
            except (json.JSONDecodeError, OSError):
                pass

    # acquire the known external ip address for this instance
    active_ipv4 = ''
    active_ipv6 = ''
    ip_fetch_state = EngineState.OK

    if not args.action or args.action == Action.IP:
        if ipv4:
            myipv4_cmd = cfg.myipv4_api_endpoint_cmd()
            if myipv4_cmd:
                active_ipv4 = fetch_myipv4_cmd(myipv4_cmd)
            else:
                endpoints = cfg.myipv4_api_endpoints()
                active_ipv4 = fetch_myipv4(endpoints=endpoints, timeout=timeout)

            if not active_ipv4:
                ip_fetch_state = EngineState.MYIP_FETCH_FAILURE
            elif args.action == Action.IP:
                success(f'detected ipv4: {active_ipv4}')

        if ipv6:
            myipv6_cmd = cfg.myipv6_api_endpoint_cmd()
            if myipv6_cmd:
                active_ipv6 = fetch_myipv6_cmd(myipv6_cmd)
            else:
                endpoints = cfg.myipv6_api_endpoints()
                active_ipv6 = fetch_myipv6(endpoints=endpoints, timeout=timeout)

            if not active_ipv6:
                ip_fetch_state = EngineState.MYIP_FETCH_FAILURE
            elif args.action == Action.IP:
                success(f'detected ipv6: {active_ipv6}')

    if args.action == Action.IP:
        return ip_fetch_state

    # if the active ip matches the cached ip, we may not have to interact
    # with nfsn's api
    ipv4_cache_hit = cached_data.get('ipv4') == active_ipv4
    ipv6_cache_hit = cached_data.get('ipv6') == active_ipv6
    if allow_caching:
        if ipv4 and not ipv4_cache_hit:
            verbose('ipv4 cache was not a match')
        elif ipv6 and not ipv6_cache_hit:
            verbose('ipv6 cache was not a match')
        else:
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

        # populate desired record entries
        pending_cfgs = {}
        if ipv4:
            pending_cfgs['A'] = active_ipv4
        if ipv6:
            pending_cfgs['AAAA'] = active_ipv6

        try:
            rsp_data = rsp.json()

            # if we have a dns record, process each response record into a
            # dictionary that we can use for comparisions
            reported_rrs = {}
            if rsp_data:
                for rr_entry in rsp_data:
                    rr_type = rr_entry.get('type')
                    rr_data = rr_entry.get('data')
                    if rr_type and rr_data:
                        reported_rrs[rr_type] = rr_data

            # cycle through pending configurations and update any record that
            # has stale data
            for rr_type in list(pending_cfgs):
                new_value = pending_cfgs[rr_type]
                persisted_ip = reported_rrs.get(rr_type)
                if not persisted_ip:
                    continue

                if persisted_ip == new_value:
                    verbose(f'ddns record ({rr_type}) matches external address')
                else:
                    verbose(f'ip do not match for record: {ddns_record}')
                    opts = {
                        'name': ddns_record,
                        'type': rr_type,
                        'data': new_value,
                    }
                    target_url = f'{base_url}/replaceRR'
                    verbose(f'(request) {target_url}')
                    rsp = session.post(target_url, data=opts, timeout=timeout)
                    rsp.raise_for_status()
                    log(f'record ({rr_type}) has been updated: {new_value}')

                del pending_cfgs[rr_type]

            # for any entries that do not have a ddns record setup, add it now
            for rr_type, new_value in pending_cfgs.items():
                warn(f'no record found ({ddns_record}; {rr_type}); creating...')
                opts = {
                    'name': ddns_record,
                    'type': rr_type,
                    'data': new_value,
                }
                target_url = f'{base_url}/addRR'
                verbose(f'(request) {target_url}')
                rsp = session.post(target_url, data=opts, timeout=timeout)
                rsp.raise_for_status()
        except HTTPError as e:
            err(f'failed to query the dns record\n{e}')
            return EngineState.NFSN_API_FAILURE

    # save the newly detected ip if it has changed
    if allow_caching and (not ipv4_cache_hit or not ipv6_cache_hit):
        for cache_file_entry in cache_files:
            cache_file = Path(str(cache_file_entry).format(uid=uid))

            try:
                cache_container = cache_file.parent
                if not cache_container.exists():
                    verbose(f'preparing cache container: {cache_container}')
                    cache_container.mkdir(parents=True)

                verbose(f'persisting cache: {cache_file}')
                with cache_file.open('w') as f:
                    json.dump({
                        'ipv4': active_ipv4,
                        'ipv6': active_ipv6,
                    }, f)

                # if we are able to write to this catch file, we are done!
                break
            except OSError:
                pass

    return EngineState.OK
