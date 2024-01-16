# -*- coding: utf-8 -*-
import time
import unittest

from configmodel.MixinDelayedWrite import MixinDelayedWrite


def ms(milliseconds):
    """
    Convert milliseconds to seconds
    """
    return milliseconds / 1000


class MockMixinDelayedWrite(MixinDelayedWrite):
    DEFAULT_DELAY_SECONDS = 0.1

    def __init__(self, delayed_write_enabled=True, delay_seconds=DEFAULT_DELAY_SECONDS):
        MixinDelayedWrite.__init__(
            self,
            delayed_write_enabled=delayed_write_enabled,
            delay_seconds=delay_seconds
        )
        self.timer_fired_at = None

    def _commit_delayed_write(self):
        self.timer_fired_at = time.time()


class TestMixinDelayedWrite(unittest.TestCase):

    def test_delayed_write(self):
        """
        Test that delayed write works
        """
        mixin_delayed_write = MockMixinDelayedWrite(delayed_write_enabled=False)
        # change parameters
        expected_delay = ms(200)
        mixin_delayed_write._set_delayed_write(True, delay_seconds=expected_delay)
        # start timer
        start_time = time.time()
        mixin_delayed_write._restart_delayed_timer()
        # delay a bit
        time.sleep(ms(50))
        # check that timer was not fired
        self.assertIsNone(mixin_delayed_write.timer_fired_at)
        # wait for timer to fire
        time.sleep(ms(150) + ms(20))
        # check that timer was fired
        self.assertIsNotNone(mixin_delayed_write.timer_fired_at)
        delta_time = mixin_delayed_write.timer_fired_at - start_time
        self.assertGreaterEqual(delta_time, expected_delay - ms(5))
        self.assertLess(delta_time, expected_delay + ms(20))

    def test_delayed_write_disabled(self):
        """
        Test that commit is called immediately when delayed write is disabled
        """
        mixin_delayed_write = MockMixinDelayedWrite(delayed_write_enabled=True)
        # change parameters
        mixin_delayed_write._set_delayed_write(False)
        # start timer
        mixin_delayed_write._restart_delayed_timer()
        # check that timer was fired
        self.assertIsNotNone(mixin_delayed_write.timer_fired_at)

    def test_restart_delayed_timer(self):
        """
        Test that restart works
        """
        mixin_delayed_write = MockMixinDelayedWrite(delayed_write_enabled=False, delay_seconds=ms(900))
        # change parameters
        mixin_delayed_write._set_delayed_write(True, delay_seconds=ms(100))
        # start timer
        time_start = time.time()
        mixin_delayed_write._restart_delayed_timer()
        # delay a bit
        time.sleep(ms(50))
        # check that timer was not fired
        self.assertIsNone(mixin_delayed_write.timer_fired_at)
        # restart timer
        mixin_delayed_write._restart_delayed_timer()
        # check that timer was not fired
        self.assertIsNone(mixin_delayed_write.timer_fired_at)
        # delay a bit
        time.sleep(ms(50))
        # restart timer
        mixin_delayed_write._restart_delayed_timer()
        # check that timer was not fired
        self.assertIsNone(mixin_delayed_write.timer_fired_at)
        # wait for timer to fire
        time.sleep(ms(100) + ms(20))

        expected_delay = ms(50) + ms(50) + ms(100)

        # check that timer was fired
        self.assertIsNotNone(mixin_delayed_write.timer_fired_at)
        delta_time = mixin_delayed_write.timer_fired_at - time_start
        self.assertGreaterEqual(delta_time, expected_delay - ms(5))
        self.assertLess(delta_time, expected_delay + ms(20))


if __name__ == '__main__':
    unittest.main()
