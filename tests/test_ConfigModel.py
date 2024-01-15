import unittest

__author__ = "Vasily Maslyukov"
__license__ = "MIT"

from unittest.mock import patch

from configmodel import ConfigModel, config_file, nested_field
from configmodel.Logger import Log
from mock_Serializer import mock_return_path_as_value, MockSerializer

TEST_CONFIG_FILE = "config.mock"
ANOTHER_CONFIG_FILE = "second_config.mock"

# enable logging
Log.logging_enabled = True


class TestConfigModel(unittest.TestCase):

    def setUp(self):
        super().setUp()
        # add mock serializer for *.mock extension
        MockSerializer.register_in_factory()

    def test_forbid_instances_of_static_config(self):
        """
        If @config_file decorator is used, ConfigModel should not be instantiated
        """
        @config_file(TEST_CONFIG_FILE)
        class StaticConfig(ConfigModel):
            product_key = "1234567890"

        with self.assertRaises(Exception):
            # this should fail
            StaticConfig()

    def test_allow_instances_of_non_static_config(self):
        """
        If @config_file decorator is not used, ConfigModel could be instantiated
        """
        class NonStaticConfig(ConfigModel):
            value1 = "default value"

        instance = NonStaticConfig(TEST_CONFIG_FILE)
        self.assertEqual("default value", instance.value1)

    def test_create_instances(self):
        """
        Create two instances of the same class.
        Check that they are different objects, and don't share values
        """
        class ConfigInstance(ConfigModel):
            value1 = "1001"
            value2 = "1002"

            class NestedConfig(ConfigModel):
                color = "2003"
                saturation = "2004"

            purple_config = NestedConfig()
            red_config = NestedConfig()

        # create two instances
        instance1 = ConfigInstance(TEST_CONFIG_FILE)
        instance2 = ConfigInstance(ANOTHER_CONFIG_FILE)

        # set different values
        instance1.purple_config.color = "orange"
        instance2.purple_config.color = "green"

        # check how many fields are defined in total (including nested)
        all_fields = instance1._get_all_fields_recursive()
        self.assertEqual(6, len(all_fields))

        # if a decorator is not used, classes should not act as singletons
        self.assertIsNone(instance1.NestedConfig._get_instance())
        self.assertIsNone(instance2.NestedConfig._get_instance())

        # check that instances are different
        self.assertIsNot(instance1._fields, instance2._fields)
        self.assertIsNot(instance1.purple_config, instance2.purple_config)

        self.assertNotEqual(instance1.purple_config.color, instance2.purple_config.color)

        # check that static variables are not changed (only instance variables shall be changed)
        self.assertEqual("2003", ConfigInstance.purple_config.color)

    def test_nested_instance_of_outer_class(self):
        """
        Define a nested class outside the main class.
        Check that it's possible to create an instance of the nested class.
        """
        class OuterNestedConfig(ConfigModel):
            value1 = "1001"
            value2 = "1002"

        class MainConfig(ConfigModel):
            value1 = "2001"
            value2 = "2002"
            outer_nested_config = OuterNestedConfig()

        instance1 = MainConfig(TEST_CONFIG_FILE)
        instance2 = MainConfig(ANOTHER_CONFIG_FILE)
        self.assertEqual(instance1.outer_nested_config.value1, "1001")

        # assign different values
        instance1.outer_nested_config.value1 = "red value"
        instance2.outer_nested_config.value1 = "green value"

        # check that instances are different
        self.assertIsNot(instance1.outer_nested_config, instance2.outer_nested_config)
        self.assertNotEqual(instance1.outer_nested_config.value1, instance2.outer_nested_config.value1)
        self.assertEqual("red value", instance1.outer_nested_config.value1)
        self.assertEqual("green value", instance2.outer_nested_config.value1)
        # check that static variables are not changed (only instance variables shall be changed)
        self.assertEqual("1001", MainConfig.outer_nested_config.value1)

    def test_forbid_both_nested_class_decorator_and_instance(self):
        """
        If nested class is decorated with @nested_field, it's not allowed to define an instance of the same class.
        """
        with self.assertRaises(Exception):
            @config_file(TEST_CONFIG_FILE)
            class RootConfig(ConfigModel):
                # use decorator
                @nested_field("nested_config")
                class NestedConfig(ConfigModel):
                    pass
                # also define instance (not allowed with decorator)
                other_instance = NestedConfig()

    def test_initialize_fields_decorated(self):
        """
        Check that fields are initialized correctly when using @nested_field decorator
        """
        # define config
        @config_file(TEST_CONFIG_FILE)
        class StaticConfig(ConfigModel):
            product_key = "1234567890"

            @nested_field("magenta_config")
            class NestedConfig(ConfigModel):
                parameter1 = "default value"

        # an instance of StaticConfig should be created because it's decorated
        root_instance = StaticConfig._get_instance()
        self.assertIsNotNone(root_instance)

        all_fields = root_instance._get_all_fields_recursive()
        self.assertEqual(2, len(all_fields))

        # check paths
        with patch.object(MockSerializer, "get_value", side_effect=mock_return_path_as_value) as mock_get_value:
            val = StaticConfig.product_key
            mock_get_value.assert_called_with(["product_key"])
            # accessing field using static class, but serializer should receive @nested_field path
            val = StaticConfig.NestedConfig.parameter1
            mock_get_value.assert_called_with(["magenta_config", "parameter1"])

    def test_paths(self):
        """
        Test complex config with multiple levels of nesting
        """
        # define config
        @config_file(TEST_CONFIG_FILE)
        class StaticConfig(ConfigModel):
            string_value = "1234567890"
            integer_value = 1234567890
            float_value = 1234567890.0
            boolean_value_true = True
            boolean_value_false = False

            class ApiKey(ConfigModel):
                client_id = "8298"
                secret = "98297821"

            class MultilevelConfig(ConfigModel):
                root_parameter = "root value"
                other_parameter = "other value"

                class RedConfig(ConfigModel):
                    red_parameter = "red value"
                    pink_parameter = "pink value"

                @nested_field("green_config")
                class RenamedConfig(ConfigModel):
                    green_parameter = "green value"
                    grass_price = 17

        # test get_value
        with patch.object(MockSerializer, "get_value", side_effect=mock_return_path_as_value) as mock_get_value:
            val = StaticConfig.string_value
            mock_get_value.assert_called_with(["string_value"])
            val = StaticConfig.ApiKey.client_id
            mock_get_value.assert_called_with(["api_key", "client_id"])
            val = StaticConfig.MultilevelConfig.RedConfig.red_parameter
            mock_get_value.assert_called_with(["multilevel_config", "red_config", "red_parameter"])
            val = StaticConfig.MultilevelConfig.RenamedConfig.green_parameter
            mock_get_value.assert_called_with(["multilevel_config", "green_config", "green_parameter"])

        # test set_value
        with patch.object(MockSerializer, "set_value") as mock_set_value:
            StaticConfig.string_value = "new value"
            mock_set_value.assert_called_with(["string_value"], "new value")
            StaticConfig.ApiKey.client_id = "new client id"
            mock_set_value.assert_called_with(["api_key", "client_id"], "new client id")
            StaticConfig.MultilevelConfig.RedConfig.red_parameter = "new red value"
            mock_set_value.assert_called_with(["multilevel_config", "red_config", "red_parameter"], "new red value")
            StaticConfig.MultilevelConfig.RenamedConfig.green_parameter = "new green value"
            mock_set_value.assert_called_with(["multilevel_config", "green_config", "green_parameter"], "new green value")


if __name__ == '__main__':
    unittest.main()

