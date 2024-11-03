#!/usr/bin/env python

import os

if os.getenv('NFSN_DDNS_FETCH_IPV6'):
    print('2001:db8::2')
elif os.getenv('NFSN_DDNS_FETCH_IPV4'):
    print('203.0.113.63')
