# SPDX-License-Identifier: BSD-2-Clause
# Copyright nfsn-ddns Contributors

from __future__ import annotations
from nfsn_ddns.defs import NFSN_AUTH_HEADER
from nfsn_ddns.utils import generate_nfsn_api_salt
from nfsn_ddns.utils import generate_nfsn_api_timestamp
from requests.auth import AuthBase
from typing import TYPE_CHECKING
from urllib.parse import urlparse
import hashlib

if TYPE_CHECKING:
    from requests import PreparedRequest


class NfsnAuth(AuthBase):
    def __init__(self, account: str, token: str) -> None:
        """
        nfsn requests authentication handler

        Provides an authentication handler for Requests, building a required
        authentication token to interact with NFSN's API endpoint.

        Args:
            account: the account used to authenticate
            token: the api token
        """
        self.hash_method = hashlib.sha1
        self.account = account
        self.token = token

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        """
        call operater invoked when authenticating a request

        The hook called when Requests processes authentication for a request.

        Args:
            r: the request to authenticate

        Returns:
            the updated request
        """
        request_uri = urlparse(r.path_url).path

        if isinstance(r.body, bytes):
            encoded_body = r.body
        else:
            encoded_body = r.body.encode('utf-8') if r.body else b''
        hashed_body = self._hash(encoded_body)

        salt = generate_nfsn_api_salt()
        timestamp = generate_nfsn_api_timestamp()

        hash_contents = ';'.join([  # noqa: FLY002
            self.account,
            timestamp,
            salt,
            self.token,
            request_uri,
            hashed_body,
        ])
        hashed = self._hash(hash_contents.encode('utf-8'))

        request_data = ';'.join([  # noqa: FLY002
            self.account,
            timestamp,
            salt,
            hashed,
        ])

        r.headers[NFSN_AUTH_HEADER] = request_data
        return r

    def _hash(self, value: bytes) -> str:
        """
        utility to generate a hash from a string value

        Args:
            value: the value to hash

        Returns:
            the hashed value
        """
        return self.hash_method(value).hexdigest()
