# SPDX-License-Identifier: BSD-2-Clause
# Copyright nfsn-ddns Contributors

from enum import Enum
from pathlib import Path
import sys

# endpoint for NFSN DNS API
API_DNS_ENDPOINT = 'https://api.nearlyfreespeech.net/dns'

# default number of days before considering a cached public ip stale
DEFAULT_CACHE_DAYS = 7

# mininum cache days accepted (one day)
MIN_CACHE_DAYS = 1

# maximum cache days accepted (thirty days)
MAX_CACHE_DAYS = 30

# default files to cache last detected public ip
if sys.platform != 'win32':
    DEFAULT_CACHE_FILES = [
        Path('/run/nfsn-ddns/cached-ip'),
        Path('/run/user/{uid}/cached-ip'),
        Path('nfsn-ddns-cached-ip'),
    ]
else:
    DEFAULT_CACHE_FILES = [
        Path('nfsn-ddns-cached-ip'),
    ]

# default file for configuration data
DEFAULT_CFG_FILE = Path('config.yaml')

# default api endpoints to fetch current ip
DEFAULT_IP_FETCH_URLS = [
    'https://api.ipify.org',
    'https://checkip.amazonaws.com/',
    'https://ifconfig.me/ip',
    'https://ipinfo.io/ip',
    'https://trackip.net/ip',
]

# default timeout for any requests made
DEFAULT_TIMEOUT = 10

# mininum timeout for any requests made (one second)
MIN_TIMEOUT = 1

# maximum timeout for any requests made (two minutes)
MAX_TIMEOUT = 120

# http header required for api authentication
NFSN_AUTH_HEADER = 'X-NFSN-Authentication'

# prefix to use for environment-provided configuration options
NFSN_DDNS_ENV_PREFIX = 'NFSN_DDNS_'


class Action(Enum):
    # only attempt to check interaction with nfsn
    CHECK = 'check'
    # only attempt to fetch my external ip
    IP = 'ip'

    def __str__(self) -> str:
        return self.value
