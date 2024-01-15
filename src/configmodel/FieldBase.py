# -*- coding: utf-8 -*-

class FieldBase:

    def __init__(self, name, default_value=None):
        self.name = name
        self.default_value = default_value
