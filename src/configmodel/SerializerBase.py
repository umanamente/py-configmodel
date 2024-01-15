# -*- coding: utf-8 -*-
from typing import List


class SerializerBase:

    class FieldDefaultValue:
        def __init__(self, path, value):
            self.path = path
            self.value = value

    def __init__(self, filename):
        self.filename = filename

    def set_value(self, path, value):
        raise NotImplementedError

    def get_value(self, path):
        raise NotImplementedError

    def write_default_values_from_model(self, default_values: List[FieldDefaultValue]):
        """
        Initialize default values
        """
        raise NotImplementedError
