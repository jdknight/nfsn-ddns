# SPDX-License-Identifier: BSD-2-Clause
# Copyright nfsn-ddns Contributors

from __future__ import annotations
from nfsn_ddns.defs import DEFAULT_IP_FETCH_URLS
from nfsn_ddns.log import err
from nfsn_ddns.log import warn
from nfsn_ddns.log import verbose
from typing import TYPE_CHECKING
import ipaddress
import random
import requests

if TYPE_CHECKING:
    from typing import Union


def fetch_myip(endpoints: Union[None, str, list[str]] = None,
        timeout: int = 3) -> str:
    """
    query for the external ip address for this instance

    This call will query an available API endpoint to determine the remote
    IP (external) address for this instance. This address will assumed to be
    the address target to apply for a DDNS record.

    By default, a random endpoint will be used to determine this address. A
    series of endpoint services are managed internally. If an endpoint fails
    to provide an expected address, another random endpoint will be selected
    until an address is resolved or if there are no longer any endpoints to
    query. If an endpoint is provided into this fetch request, only the
    provided endpoint will be attempted on.

    Args:
        endpoints (optional): the explicit endpoint(s) to query on
        timeout (optional): timeout for any requests made

    Returns:
        the ip address; `None` on failure
    """

    if endpoints:
        if isinstance(endpoints, list):
            available_endpoints = list(endpoints)
        else:
            available_endpoints = [
                endpoints,
            ]
    else:
        available_endpoints = DEFAULT_IP_FETCH_URLS

    while available_endpoints:
        endpoint_idx = random.randrange(len(available_endpoints))  # noqa: S311
        target = available_endpoints.pop(endpoint_idx)

        session = requests.Session()
        session.headers.update({
            'User-Agent': 'nfsn-ddns',
        })

        try:
            verbose(f'(myip) attempting to query endpoint: {target}')
            rsp = session.get(target, timeout=timeout)
            rsp.raise_for_status()

            try:
                ip = ipaddress.ip_address(rsp.text.strip())
            except ValueError:
                warn(f'(myip) endpoint provided invalid address: {target}')
            else:
                ip_str = str(ip)
                verbose(f'(myip) resolved self address: {ip_str}')
                return ip_str
        except requests.exceptions.RequestException as e:
            warn(f'(myip) fail to fetch on endpoint: {target}\n{e}')

    err('(myip) unable to determine self address (exhausted endpoints)')
    return ''
