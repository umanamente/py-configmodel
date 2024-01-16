# -*- coding: utf-8 -*-
import unittest

from configmodel.SerializerIni import SerializerIni
from configmodel.SerializersFactory import SerializersFactory
from mock_Serializer import MockSerializer


class TestSerializersFactory(unittest.TestCase):

    def test_mock_serializer(self):
        """
        Test that SerializersFactory.get_serializer_by_filename() returns correct serializer
        given .mock extension
        """
        MockSerializer.register_in_factory()
        serializer = SerializersFactory.get_serializer_by_filename("test.mock")
        self.assertIsInstance(serializer, MockSerializer)

    def test_get_serializer_by_filename(self):
        """
        Test that SerializersFactory.get_serializer_by_filename() returns correct serializer
        """

        serializer = SerializersFactory.get_serializer_by_filename("test.ini")
        self.assertIsInstance(serializer, SerializerIni)

    def test_unsupported_extension(self):
        """
        Test that SerializersFactory.get_serializer_by_filename() raises exception
        if extension is not supported
        """
        with self.assertRaises(Exception):
            SerializersFactory.get_serializer_by_filename("test.txt")


if __name__ == '__main__':
    unittest.main()
