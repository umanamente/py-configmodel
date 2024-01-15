# -*- coding: utf-8 -*-
import unittest

from configmodel.Logger import Log
from configmodel.SerializerBase import SerializerBase
from configmodel.SerializersFactory import SerializersFactory


def path_to_string(path):
    return ".".join(path)


def mock_return_path_as_value(path):
    return path_to_string(path)


class MockSerializer(SerializerBase):

    def __init__(self, filename):
        super().__init__(filename)
        self.cached_values = {}

    @staticmethod
    def register_in_factory():
        SerializersFactory.SUPPORTED_SERIALIZERS.append([MockSerializer, [".mock"]])

    def set_value(self, path, value):
        self.cached_values[path_to_string(path)] = value
        Log.debug("MockSerializer.set_value: path: {}, value: {}".format(path, value))

    def get_value(self, path):
        path_str = path_to_string(path)
        if path_str in self.cached_values:
            return self.cached_values[path_str]
        else:
            return None

    def write_default_values_from_model(self, default_values):
        for default_value in default_values:
            self.cached_values[path_to_string(default_value.path)] = default_value.value


class TestMockSerializer(unittest.TestCase):

    def test_mock_serializer(self):
        MockSerializer.register_in_factory()
        serializer = SerializersFactory.get_serializer_by_filename("test.mock")

        self.assertIsInstance(serializer, MockSerializer)

        serializer.set_value(["a", "b", "c"], 1)
        self.assertEqual(serializer.get_value(["a", "b", "c"]), 1)
        serializer.set_value(["a", "b", "c"], 2)
        self.assertEqual(serializer.get_value(["a", "b", "c"]), 2)


if __name__ == '__main__':
    unittest.main()
