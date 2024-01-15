# -*- coding: utf-8 -*-

class Log:

    logging_enabled = False

    @classmethod
    def debug(cls, message):
        if not cls.logging_enabled:
            return
        print("DEBUG: %s" % message)

    @classmethod
    def error(cls, message):
        if not cls.logging_enabled:
            return
        print("ERROR: %s" % message)

