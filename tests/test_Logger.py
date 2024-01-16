# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from configmodel.Logger import Log


class TestLogger(unittest.TestCase):

    def setUp(self):
        super().setUp()
        # save old value
        self._old_logging_enabled = Log.logging_enabled

    def tearDown(self):
        super().tearDown()
        # restore old value
        Log.logging_enabled = self._old_logging_enabled

    def test_logger_disabled(self):
        Log.logging_enabled = False
        with patch('builtins.print') as mock_print:
            Log.debug("debug message")
            Log.error("error message")
            mock_print.assert_not_called()

    def test_logger_enabled(self):
        Log.logging_enabled = True
        with patch('builtins.print') as mock_print:
            Log.debug("debug message")
            Log.error("error message")
            mock_print.assert_any_call("DEBUG: debug message")
            mock_print.assert_any_call("ERROR: error message")


if __name__ == '__main__':
    unittest.main()
