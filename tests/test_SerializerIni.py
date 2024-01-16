# -*- coding: utf-8 -*-
import configparser
import os
import random
import string
import tempfile
import unittest

from configmodel import config_file, ConfigModel
from configmodel.SerializerIni import SerializerIni


class TestSerializerIni(unittest.TestCase):
    def setUp(self):
        super().setUp()
        # get temporary directory
        self._temp_dir = tempfile.TemporaryDirectory(prefix="test_SerializerIni_")

    def tearDown(self):
        super().tearDown()
        # delete temporary directory
        self._temp_dir.cleanup()

    def _get_temp_file(self, suffix=".ini"):
        """
        Generate unique file name in temporary directory.
        It is guaranteed that the file does not exist.

        :return: Full path to file
        """
        for _ in range(10):
            rand_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            filename = rand_str + suffix
            full_path = os.path.join(self._temp_dir.name, filename)
            if not os.path.isfile(full_path):
                return full_path
        raise Exception("Could not generate unique file name")

    def test_file_creation(self):
        filename = self._get_temp_file()

        @config_file(filename)
        class StaticConfig(ConfigModel):
            product_key = "1234"

        self.assertTrue(os.path.isfile(filename))

        # parse file and check that it contains correct values
        parser = configparser.ConfigParser()
        parser.read(filename)
        self.assertTrue(parser.has_section(SerializerIni.DEFAULT_SECTION))
        self.assertTrue(parser.has_option(SerializerIni.DEFAULT_SECTION, "product_key"))
        self.assertEqual("1234", parser[SerializerIni.DEFAULT_SECTION]["product_key"])

    def test_merge_defaults_with_existing_ini(self):
        ini_content = """
        [Global]
        product_key = 9810347
        secret = zzzz
        [api_key]
        client_id = 8298
        secret = 98297821       
        """
        filename = self._get_temp_file()
        with open(filename, "w") as f:
            f.write(ini_content)

        @config_file(filename)
        class StaticConfig(ConfigModel):
            product_key = "1234"
            secret = "abcd"
            new_parameter = "new value"
            color = "blue"

            class ApiKey(ConfigModel):
                client_id = "<insert client id>"
                secret = "<insert secret>"
                foo = "bar"

        # parse file and check that existing values are preserved and new values are added
        parser = configparser.ConfigParser()
        parser.read(filename)
        self.assertTrue(parser.has_section(SerializerIni.DEFAULT_SECTION))
        self.assertTrue(parser.has_option(SerializerIni.DEFAULT_SECTION, "product_key"))
        self.assertEqual("9810347", parser[SerializerIni.DEFAULT_SECTION]["product_key"])
        self.assertTrue(parser.has_option(SerializerIni.DEFAULT_SECTION, "secret"))
        self.assertEqual("zzzz", parser[SerializerIni.DEFAULT_SECTION]["secret"])
        self.assertTrue(parser.has_option(SerializerIni.DEFAULT_SECTION, "new_parameter"))
        self.assertEqual("new value", parser[SerializerIni.DEFAULT_SECTION]["new_parameter"])
        self.assertTrue(parser.has_option(SerializerIni.DEFAULT_SECTION, "color"))
        self.assertEqual("blue", parser[SerializerIni.DEFAULT_SECTION]["color"])

        self.assertTrue(parser.has_section("api_key"))
        self.assertTrue(parser.has_option("api_key", "client_id"))
        self.assertEqual("8298", parser["api_key"]["client_id"])
        self.assertTrue(parser.has_option("api_key", "secret"))
        self.assertEqual("98297821", parser["api_key"]["secret"])
        self.assertTrue(parser.has_option("api_key", "foo"))
        self.assertEqual("bar", parser["api_key"]["foo"])

        # get values
        self.assertEqual("9810347", StaticConfig.product_key)
        self.assertEqual("zzzz", StaticConfig.secret)
        self.assertEqual("new value", StaticConfig.new_parameter)
        self.assertEqual("blue", StaticConfig.color)
        self.assertEqual("8298", StaticConfig.ApiKey.client_id)
        self.assertEqual("98297821", StaticConfig.ApiKey.secret)
        self.assertEqual("bar", StaticConfig.ApiKey.foo)

        # set values
        StaticConfig.product_key = "5678"
        self.assertEqual("5678", StaticConfig.product_key)
        StaticConfig.ApiKey.client_id = "98"
        self.assertEqual("98", StaticConfig.ApiKey.client_id)
        StaticConfig.ApiKey.foo = "asdf"

        # check that values are written to file
        parser = configparser.ConfigParser()
        parser.read(filename)
        self.assertTrue(parser.has_section(SerializerIni.DEFAULT_SECTION))
        self.assertTrue(parser.has_option(SerializerIni.DEFAULT_SECTION, "product_key"))
        self.assertEqual("5678", parser[SerializerIni.DEFAULT_SECTION]["product_key"])
        self.assertTrue(parser.has_section("api_key"))
        self.assertTrue(parser.has_option("api_key", "client_id"))
        self.assertEqual("98", parser["api_key"]["client_id"])
        self.assertTrue(parser.has_option("api_key", "foo"))
        self.assertEqual("asdf", parser["api_key"]["foo"])

    def test_ini_changed_in_the_process(self):
        """
        Test that the following scenario works:
            User changes INI file while the application is running,
            ConfigModel shouldn't freak out.
        """
        filename = self._get_temp_file()

        @config_file(filename)
        class StaticConfig(ConfigModel):
            product_key = "1234"
            secret = "abcd"
            new_parameter = "new value"
            color = "blue"

            class ApiKey(ConfigModel):
                client_id = "<insert client id>"
                secret = "<insert secret>"
                foo = "bar"

        # at this point the ini file is created and contains default values
        # let's change it
        parser = configparser.ConfigParser()
        parser.read(filename)
        # change value
        parser[SerializerIni.DEFAULT_SECTION]["product_key"] = "changed value"
        # add new section
        parser["new_section"] = {}
        parser["new_section"]["new_parameter"] = "new value"

        with open(filename, "w") as f:
            parser.write(f)

        # change some config values in the application
        StaticConfig.secret = "777777777"
        StaticConfig.ApiKey.secret = "888888888"

        # check that user values were not overwritten, and application values were written to file
        parser = configparser.ConfigParser()
        parser.read(filename)
        self.assertTrue(parser.has_section(SerializerIni.DEFAULT_SECTION))
        self.assertTrue(parser.has_option(SerializerIni.DEFAULT_SECTION, "product_key"))
        self.assertEqual("changed value", parser[SerializerIni.DEFAULT_SECTION]["product_key"])
        self.assertTrue(parser.has_option(SerializerIni.DEFAULT_SECTION, "secret"))
        self.assertEqual("777777777", parser[SerializerIni.DEFAULT_SECTION]["secret"])
        self.assertTrue(parser.has_section("new_section"))
        self.assertTrue(parser.has_option("new_section", "new_parameter"))
        self.assertEqual("new value", parser["new_section"]["new_parameter"])
        self.assertTrue(parser.has_section("api_key"))
        self.assertTrue(parser.has_option("api_key", "secret"))
        self.assertEqual("888888888", parser["api_key"]["secret"])

    def test_ini_cleared_in_the_process(self):
        """
        Test that the following scenario works:
            User removes INI section while the application is running,
            ConfigModel shouldn't freak out.
        """
        filename = self._get_temp_file()

        @config_file(filename)
        class StaticConfig(ConfigModel):
            product_key = "1234"
            secret = "abcd"
            new_parameter = "new value"
            color = "blue"

            class ApiKey(ConfigModel):
                client_id = "<insert client id>"
                secret = "<insert secret>"
                foo = "bar"

        # at this point the ini file is created and contains default values
        # let's clear it
        with open(filename, "w") as f:
            f.write("")
            f.close()

        # change some config values in the application
        StaticConfig.secret = "777777777"
        StaticConfig.ApiKey.secret = "888888888"

        # check that user values were not overwritten, and application values were written to file
        parser = configparser.ConfigParser()
        parser.read(filename)
        self.assertTrue(parser.has_section(SerializerIni.DEFAULT_SECTION))
        self.assertTrue(parser.has_section("api_key"))
        self.assertTrue(parser.has_option("api_key", "secret"))
        self.assertEqual("888888888", parser["api_key"]["secret"])
        # default values should be written to file
        self.assertTrue(parser.has_option(SerializerIni.DEFAULT_SECTION, "product_key"))
        self.assertEqual("1234", parser[SerializerIni.DEFAULT_SECTION]["product_key"])

    def test_invalid_parameters(self):
        """
        Test that ConfigModel raises exception if parameter name is invalid
        """
        filename = self._get_temp_file()

        class AppConfig(ConfigModel):
            product_key = "1234"
            secret = "abcd"

        app_config = AppConfig(filename)
        serializer = app_config._serializer

        with self.assertRaises(Exception):
            serializer.get_value([])
        with self.assertRaises(Exception):
            serializer.set_value([], "value")


if __name__ == '__main__':
    unittest.main()
