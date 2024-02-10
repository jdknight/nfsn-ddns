# SPDX-License-Identifier: BSD-2-Clause
# Copyright nfsn-ddns Contributors

from calendar import timegm
from time import gmtime
import random
import string


# populated characters used for nfsn salt generation
SALT_CHARS = ''.join([  # noqa: FLY002
    string.ascii_lowercase,
    string.ascii_uppercase,
    string.digits,
])


def generate_nfsn_api_salt() -> str:
    """
    generate an nfsn api-compatible salt

    NFSN's API requires a randomly-generated 16 character alphanumeric value
    (a-z, A-Z, 0-9) salt value. This call will generate a string value
    representing this salt value.

    Returns:
        the salt
    """
    return ''.join([random.choice(SALT_CHARS) for x in range(16)])  # noqa: S311


def generate_nfsn_api_timestamp() -> str:
    """
    generate an nfsn api-compatible timestamp

    NFSN's API requires a standard 32-bit unsigned Unix timestamp value as
    part of an authentication header. This call will generate a string value
    representing this timestamp.

    Returns:
        the timestamp
    """
    return str(timegm(gmtime()))


def str2bool(value: str) -> bool:
    """
    returns the boolean value for a string

    Returns the boolean value for a provided string. Acceptable values for a
    ``True`` case includes ``y``, ``yes``, ``t``, ``true``, ``on`` and ``1``;
    for a ``False`` case includes ``n``, ``no``, ``f``, ``false``, ``off`` and
    ``0``. Raises ``ValueError`` on error.

    Args:
        value: the raw value

    Returns:
        the boolean interpretation

    Raises:
        ``ValueError`` is raised if the string value is not an accepted string
    """

    value = str(value).lower()

    if value in ['y', 'yes', 't', 'true', 'on', '1']:
        return True

    if value in ['n', 'no', 'f', 'false', 'off', '0']:
        return False

    raise ValueError
