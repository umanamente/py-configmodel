# -*- coding: utf-8 -*-
import time
import unittest

from configmodel.MixinDelayedWrite import InterruptibleTimer


def ms(milliseconds):
    """
    Convert milliseconds to seconds
    """
    return milliseconds / 1000


class TestInterruptibleTimer(unittest.TestCase):

    def test_timer(self):
        """
        Test that InterruptibleTimer works
        """
        start_time = time.time()
        end_time = 0.0

        def _set_end_time():
            nonlocal end_time
            end_time = time.time()

        timer = InterruptibleTimer(ms(100), _set_end_time)

        time.sleep(ms(150))
        time_diff = end_time - start_time
        self.assertGreaterEqual(time_diff, ms(0))
        self.assertGreater(time_diff, ms(99))
        self.assertLess(time_diff, ms(130))

    def test_fire_immediately(self):
        """
        Test that InterruptibleTimer fires immediately if timeout is 0
        """
        start_time = time.time()
        end_time = 0.0

        def _set_end_time():
            nonlocal end_time
            end_time = time.time()

        timer = InterruptibleTimer(ms(200), _set_end_time)
        # delay a bit
        time.sleep(ms(50))
        # fire immediately
        timer._on_exit()
        time.sleep(ms(200))
        self.assertIsNotNone(end_time)
        time_diff = end_time - start_time
        expected_delay = ms(50)
        self.assertLess(time_diff, expected_delay + ms(20))
        self.assertGreaterEqual(time_diff, expected_delay - ms(5))

    def test_timer_restart(self):
        """
        Test that InterruptibleTimer restarts
        """
        start_time = time.time()
        end_time = 0.0

        def _set_end_time():
            nonlocal end_time
            end_time = time.time()

        timer = InterruptibleTimer(ms(100), _set_end_time)
        time.sleep(ms(50))
        timer.restart(ms(100))
        time.sleep(ms(50))
        timer.restart(ms(100))

        time.sleep(ms(120))

        expected_delay = ms(50) + ms(50) + ms(100)

        time_diff = end_time - start_time
        self.assertGreaterEqual(time_diff, ms(0))
        self.assertGreater(time_diff, expected_delay - ms(20))
        self.assertLess(time_diff, expected_delay + ms(20))

    def test_timer_cancel(self):
        """
        Test that InterruptibleTimer cancels
        """
        was_called = False

        def _set_was_called():
            nonlocal was_called
            was_called = True

        timer = InterruptibleTimer(ms(100), _set_was_called)
        time.sleep(ms(20))
        timer.cancel()
        time.sleep(ms(120))

        self.assertEqual(False, was_called)

    def test_not_allowed_to_fire_twice(self):
        """
        Test that InterruptibleTimer is not allowed to fire twice
        """
        called_count = 0

        def _increment_called_count():
            nonlocal called_count
            called_count += 1

        timer = InterruptibleTimer(ms(100), _increment_called_count)
        timer._fire_callback()
        self.assertIsNone(timer.callback)
        timer._fire_callback()
        time.sleep(ms(120))

        self.assertEqual(1, called_count)


if __name__ == '__main__':
    unittest.main()
