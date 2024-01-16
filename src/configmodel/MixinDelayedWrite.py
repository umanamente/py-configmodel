# -*- coding: utf-8 -*-
import atexit
import threading
import time


class InterruptibleTimer:
    """
    Performs a callback after a specified timeout.
    The timer can be restarted by calling prolong() method.
    """
    def __init__(self, timeout_seconds, callback):
        self.callback = callback
        self.thread = threading.Thread(target=self._target)
        self.event = threading.Event()
        self.lock = threading.Lock()
        self.end_time = time.time() + timeout_seconds

        # register atexit handler to make sure that changes are committed at exit
        atexit.register(self._on_exit)

        # start timer
        self.thread.start()

    def _target(self):
        while True:
            timeout = self.end_time - time.time()
            timer_expired = self.event.wait(timeout)
            # check if end_time reached in case of timer restart
            if self.end_time <= time.time():
                self._fire_callback()
                break
            # check if callback was already fired
            with self.lock:
                if self.callback is None:
                    break

    def _fire_callback(self):
        with self.lock:
            if self.callback is not None:
                self.callback()
                self.callback = None

    def restart(self, timeout_seconds):
        # Reset the event and add extra time to the timeout
        self.end_time = time.time() + timeout_seconds
        self.event.clear()

    def cancel(self):
        with self.lock:
            self.callback = None
        self.event.set()

    def _on_exit(self):
        """
        Fire immediately
        """
        self.end_time = 0
        self.event.set()
        self.thread.join()


class MixinDelayedWrite:
    """
    Mixin for delayed write
    """
    DEFAULT_DELAY_SECONDS = 1.0

    def __init__(self, delayed_write_enabled=False, delay_seconds=DEFAULT_DELAY_SECONDS):
        self._delayed_write_enabled = delayed_write_enabled
        self._delay_seconds = delay_seconds
        self._timer = None

    def _set_delayed_write(self, delayed_write_enabled, delay_seconds=DEFAULT_DELAY_SECONDS):
        """
        Set delayed write
        """
        self._delayed_write_enabled = delayed_write_enabled
        self._delay_seconds = delay_seconds

    def _restart_delayed_timer(self):
        """
        Restart delayed timer
        """
        if not self._delayed_write_enabled or self._delay_seconds <= 0:
            # fire immediately
            self._commit_delayed_write()
        else:
            # restart timer
            if self._timer is None:
                self._timer = InterruptibleTimer(self._delay_seconds, self._on_timer_expired)
            else:
                self._timer.restart(self._delay_seconds)

    def _on_timer_expired(self):
        """
        On timer expired
        """
        self._commit_delayed_write()

    def _commit_delayed_write(self):
        """
        Commit delayed write.
        This method should be implemented in derived classes.
        """
        raise NotImplementedError()
