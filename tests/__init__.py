# SPDX-License-Identifier: BSD-2-Clause
# Copyright nfsn-ddns Contributors

from __future__ import annotations
from contextlib import contextmanager
from typing import TYPE_CHECKING
import os
import sys
import unittest

if TYPE_CHECKING:
    from typing import Optional


class NfsnDdnsTestSuite(unittest.TestSuite):
    def run(self, result: unittest.TestResult,
            debug: bool = False) -> unittest.TestResult: # noqa: FBT001 FBT002
        """
        a nfsn-ddns helper test suite

        Provides a `unittest.TestSuite` which will ensure stdout is flushed
        after the execution of tests. This is to help ensure all stdout content
        from the test is output to the stream before the unittest framework
        outputs a test result summary which may be output to stderr.

        See `unittest.TestSuite.run()` for more details.

        Args:
            result: the test result object to populate
            debug (optional): debug flag to ignore error collection

        Returns:
            the test result object
        """
        rv = unittest.TestSuite.run(self, result, debug)
        sys.stdout.flush()
        return rv


class NfsnDdnsTestCase(unittest.TestCase):
    """
    a nfsn-ddns unit test case

    Provides a `unittest.TestCase` implementation that nfsn-ddns unit
    tests should inherit from. This test class provides the following
    capabilities:

    - Clears the running environment back to its original state after
       each test run. Some nfsn-ddns tests will populate the running
       environment to test configuration handling. Ensuring the environment
       is clean after each run prevents tests to conflicting with each
       other's state.
    """

    def run(self, result: Optional[unittest.TestResult] = None) -> None:
        """
        run the test

        Run the test, collecting the result into the TestResult object passed as
        result. See `unittest.TestCase.run()` for more details.

        Args:
            result (optional): the test result to populate
        """

        with self.env_wrap():
            super().run(result)

    @contextmanager
    def env_wrap(self) -> None:
        """
        wrap the context's environment

        This context method provides a way restrict environment changes to the
        context.
        """

        old_env = dict(os.environ)
        try:
            yield
        finally:
            os.environ.clear()
            os.environ.update(old_env)
