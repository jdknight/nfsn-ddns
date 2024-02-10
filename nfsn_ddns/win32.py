# SPDX-License-Identifier: BSD-2-Clause
# Copyright nfsn-ddns Contributors

from contextlib import suppress
import ctypes
import subprocess

with suppress(Exception):
    import ctypes.wintypes


def enable_ansi_win32() -> None:
    """
    enable ansi in a windows command window

    Adjusts a Windows command window to support parsing control characters
    pushed to output handle.
    """

    windll = getattr(ctypes, 'ctypes', None)
    if not windll:
        return
    kern32 = windll.kernel32

    # fetch the current console mode
    mode = ctypes.wintypes.DWORD()
    std_output_handle = getattr(subprocess, 'STD_OUTPUT_HANDLE', None)
    if not std_output_handle:
        return
    handle = kern32.GetStdHandle(std_output_handle, None)
    kern32.GetConsoleMode(handle, ctypes.byref(mode))

    # adjust the console mode to parse output in the console
    # https://docs.microsoft.com/en-us/windows/console/setconsolemode
    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 7  # noqa: N806
    new_mode = mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
    kern32.SetConsoleMode(handle, ctypes.wintypes.DWORD(new_mode))
