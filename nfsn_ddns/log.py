# SPDX-License-Identifier: BSD-2-Clause
# Copyright nfsn-ddns Contributors

from __future__ import annotations
from typing import TYPE_CHECKING
import sys

if TYPE_CHECKING:
    from typing import TextIO


# flag to track the disablement of colorized messages
NFSN_DDNS_LOG_NOCOLOR_FLAG = False

# flag to track the enablement of verbose messages
NFSN_DDNS_LOG_VERBOSE_FLAG = False


def log(msg: str, *args: str) -> None:
    """
    log a message

    Logs a (normal) message to standard out with a trailing new line.

    .. code-block:: python

        log('this is a message')

    Args:
        msg: the message
        *args: an arbitrary set of positional and keyword arguments used when
            generating a formatted message
    """
    __log('', '', msg, sys.stdout, *args)


def err(msg: str, *args: str) -> None:
    """
    log an error message

    Logs an error message to standard error with a trailing new line and (if
    enabled) a red colorization.

    .. code-block:: python

        err('this is an error message')

    Args:
        msg: the message
        *args: an arbitrary set of positional and keyword arguments used when
            generating a formatted message
    """
    sys.stdout.flush()
    __log('(error) ', '\033[1;31m', msg, sys.stderr, *args)
    sys.stderr.flush()


def success(msg: str, *args: str) -> None:
    """
    log a success message

    Logs a success message to standard error with a trailing new line and (if
    enabled) a green colorization.

    .. code-block:: python

        success('this is a success message')

    Args:
        msg: the message
        *args: an arbitrary set of positional and keyword arguments used when
            generating a formatted message
    """
    __log('(success) ', '\033[1;32m', msg, sys.stdout, *args)


def verbose(msg: str, *args: str) -> None:
    """
    log a verbose message

    Logs a verbose message to standard out with a trailing new line and (if
    enabled) an inverted colorization. By default, verbose messages will not be
    output to standard out unless the instance is configured with verbosity.

    .. code-block:: python

        verbose('this is a verbose message')

    Args:
        msg: the message
        *args: an arbitrary set of positional and keyword arguments used when
            generating a formatted message
    """
    if NFSN_DDNS_LOG_VERBOSE_FLAG:
        __log('(verbose) ', '\033[2m', msg, sys.stdout, *args)


def warn(msg: str, *args: str) -> None:
    """
    log a warning message

    Logs a warning message to standard error with a trailing new line and (if
    enabled) a purple colorization.

    .. code-block:: python

        warn('this is a warning message')

    Args:
        msg: the message
        *args: an arbitrary set of positional and keyword arguments used when
            generating a formatted message
    """
    sys.stdout.flush()
    __log('(warn) ', '\033[1;35m', msg, sys.stderr, *args)
    sys.stderr.flush()


def __log(prefix: str, color: str, msg: str, file: TextIO, *args: str) -> None:
    """
    utility logging method

    A log method to help format a message based on provided prefix and color.

    Args:
        prefix: prefix to add to the message
        color: the color to apply to the message
        msg: the message
        file: the file to write to
        *args: an arbitrary set of positional and keyword arguments used when
            generating a formatted message
    """
    if NFSN_DDNS_LOG_NOCOLOR_FLAG:
        color = ''
        post = ''
    else:
        post = '\033[0m'
    msg = str(msg)
    if args:
        msg = msg.format(*args)
    print(f'{color}{prefix}{msg}{post}', file=file)


def nfsn_ddns_log_configuration(*, nocolor: bool, verbose_: bool) -> None:
    """
    configure the global logging state of the running instance

    Adjusts the running instance's active state for logging-related
    configuration values. This method is best invoked near the start of the
    process's life cycle to provide consistent logging output. This method does
    not required to be invoked to invoke provided logging methods.

    Args:
        nocolor: toggle the disablement of colorized messages
        verbose_: toggle the enablement of verbose messages
    """
    global NFSN_DDNS_LOG_NOCOLOR_FLAG  # noqa: PLW0603
    global NFSN_DDNS_LOG_VERBOSE_FLAG  # noqa: PLW0603
    NFSN_DDNS_LOG_NOCOLOR_FLAG = nocolor
    NFSN_DDNS_LOG_VERBOSE_FLAG = verbose_
