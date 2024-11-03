# SPDX-License-Identifier: BSD-2-Clause
# Copyright nfsn-ddns Contributors

from __future__ import annotations
from nfsn_ddns.log import err
from nfsn_ddns.log import verbose
import ipaddress
import os
import subprocess


def fetch_myipv4_cmd(cmd: str) -> str:
    """
    query for the external ipv4 address for this instance using a command

    This call invoke a command to determine the remote IPv4 (external)
    address for this instance. See `_fetch` for more details.

    Args:
        endpoints (optional): the explicit endpoint(s) to query on
        timeout (optional): timeout for any requests made

    Returns:
        the ip address; `None` on failure
    """
    return _fetch(ipaddress.IPv4Address, cmd)


def fetch_myipv6_cmd(cmd: str) -> str:
    """
    query for the external ipv6 address for this instance using a command

    This call invoke a command to determine the remote IPv6 (external)
    address for this instance. See `_fetch` for more details.

    Args:
        cmd: the command to invoke

    Returns:
        the ip address; `None` on failure
    """
    return _fetch(ipaddress.IPv6Address, cmd)


def _fetch(type_: type[ipaddress.IPv4Address | ipaddress.IPv6Address],
        cmd: str) -> str:
    """
    query for the external ip address for this instance using a command

    This call invoke a command to determine the remote IP (external) address
    for this instance. This address will assumed to be the address target to
    apply for a DDNS record.

    It is expected that the command returns a valid IP address in its
    standard output stream. However, this call is somewhat flexible with
    how the output processed. If a key-value pair is detected (`key=value`),
    the value will attempt to be extracted. In addition, values wrapped with
    bracket types and quotes will also be stripped.

    Args:
        type_: the type of address being fetched
        cmd: the command to invoke

    Returns:
        the ip address; `None` on failure
    """

    cmd_env = os.environ.copy()
    os.environ.pop('NFSN_DDNS_FETCH_IPV4', None)
    os.environ.pop('NFSN_DDNS_FETCH_IPV6', None)

    if type_ == ipaddress.IPv4Address:
        cmd_env['NFSN_DDNS_FETCH_IPV4'] = '1'

    if type_ == ipaddress.IPv6Address:
        cmd_env['NFSN_DDNS_FETCH_IPV6'] = '1'

    verbose(f'(myip-cmd) issuing command: {cmd}')
    try:
        result = subprocess.run(cmd, env=cmd_env, shell=True,  # noqa: S602
            check=False, capture_output=True, text=True)
    except FileNotFoundError:
        err(f'(myip-cmd) command does not exist: {cmd}')
        return ''

    if result.returncode != 0:
        verbose(result.stdout)
        err(f'(myip-cmd) command failed to run (rv: {result.returncode})')
        return ''

    raw_output = result.stdout

    if '=' in raw_output:
        _, raw_output = raw_output.split('=', 1)

    for c in ['[', ']', '(', ')', '{', '}', '"', "'"]:
        raw_output = raw_output.replace(c, '')

    target = raw_output.strip()

    try:
        ip = ipaddress.ip_address(target)
    except ValueError:
        err('(myip-cmd) command provided invalid address')
    else:
        if not isinstance(ip, type_):
            err(f'(myip-cmd) command provided unexpected ipv: {target}')
        else:
            ip_str = str(ip)
            verbose(f'(myip-cmd) resolved self address: {ip_str}')
            return ip_str

    return ''
