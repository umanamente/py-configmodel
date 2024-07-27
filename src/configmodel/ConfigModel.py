# -*- coding: utf-8 -*-
import copy
from typing import Dict, Any, Union, List

from configmodel.FieldBase import FieldBase
from configmodel.Logger import Log
from configmodel.SerializerBase import SerializerBase
from configmodel.SerializersFactory import SerializersFactory
from configmodel.Utils import pascal_case_to_snake_case


class FieldInstance:
    serializer: Union[SerializerBase, None]
    name: Union[str, None]
    definition: Union[FieldBase, Any, None]

    def __init__(self):
        self.parent_field = None
        self.serializer = None
        self.name = None
        self.definition = None

    def get_value(self):
        assert self.serializer is not None, "Serializer is not set. This is a bug in ConfigModel library, please report it."
        assert self.name is not None, "Field name is not set. This is a bug in ConfigModel library, please report it."
        return self.serializer.get_value(self.get_path())

    def set_value(self, value):
        assert self.serializer is not None, "Serializer is not set. This is a bug in ConfigModel library, please report it."
        assert self.name is not None, "Field name is not set. This is a bug in ConfigModel library, please report it."
        self.serializer.set_value(self.get_path(), value)

    def get_path(self):
        """
        Get path to this field
        """
        path = []
        if self.parent_field is not None:
            path = self.parent_field.get_path()
        if self.name is not None:
            path.append(self.name)
        return path


class MetaConfigModel(type):
    """
    Metaclass for Config Models
    """
    pass

    def __getattribute__(cls, name):
        if name.startswith("_"):
            return super().__getattribute__(name)
        # check if class is registered as static config
        instance = cls._get_instance()
        if instance is None:
            # class is not registered as static config
            return super().__getattribute__(name)
        # noinspection PyProtectedMember
        if instance._fields is None or name not in instance._fields:
            return super().__getattribute__(name)
        return instance.__getattribute__(name)

    def __setattr__(cls, name, value):
        if name.startswith("_"):
            super().__setattr__(name, value)
            return
        # check if class is registered as static config
        instance = cls._get_instance()
        if instance is None:
            # class is not registered as static config
            super().__setattr__(name, value)
            return
        # noinspection PyProtectedMember
        if instance._fields is None or name not in instance._fields:
            super().__setattr__(name, value)
            return
        instance.__setattr__(name, value)


class ConfigModel(metaclass=MetaConfigModel):
    """
    Base class for Config Models
    """

    def __init__(self, filename=None, **kwargs):
        # check if class was already registered as config
        if self._get_instance() is not None:
            class_name = self.__class__.__name__
            raise Exception(f"{class_name} is already registered using class decorator. "
                            f"Creating instances is not allowed. Remove decorator to create instances of {class_name}.")
        self._serializer = None
        self._fields = None
        self._field_instance = None

        # check if "field_instance" attribute is in kwargs
        if "field_instance" in kwargs:
            self._field_instance = kwargs["field_instance"]

        if filename is not None:
            self._initialize_config(filename)

    def __getattribute__(self, name):
        if name.startswith("_"):
            return super().__getattribute__(name)
        fields = self._fields
        if fields is None:
            return super().__getattribute__(name)
        # check if this is a field
        if name in fields:
            # this is a field
            field: FieldInstance = fields[name]
            # check if this is a nested class
            if isinstance(field.definition, ConfigModel):
                # this is a nested class instance
                return field.definition

            assert isinstance(field.definition, FieldBase), "Unknown type of field definition. This is a bug in ConfigModel library, please report it."
            # this is a field definition
            # must return the value
            return field.get_value()
        return super().__getattribute__(name)

    def __setattr__(self, name, value):
        if name.startswith("_"):
            super().__setattr__(name, value)
            return
        fields = self._fields
        if fields is None:
            super().__setattr__(name, value)
            return
        # check if this is a field
        if name in fields:
            # this is a field
            field: FieldInstance = fields[name]
            # check if this is a nested class
            if isinstance(field.definition, ConfigModel):
                # this is a nested class instance
                raise Exception("Nested class instances are read-only")

            assert isinstance(field.definition, FieldBase), "Unknown type of field definition. This is a bug in ConfigModel library, please report it."
            # this is a field definition
            # must set the value
            field.set_value(value)
            return
        super().__setattr__(name, value)

    def _initialize_config(self, filename):
        """
        Initialize config model
        """
        pass
        self._serializer = SerializersFactory.get_serializer_by_filename(filename)

        root_field_instance = FieldInstance()
        root_field_instance.parent_field = None
        root_field_instance.name = None
        root_field_instance.definition = None
        root_field_instance.serializer = self._serializer
        self._initialize_fields(root_field_instance)

    @classmethod
    def _get_instance(cls):
        """
        :rtype: ConfigModel
        """
        # check if "_instance" attribute is set
        if "_instance" in cls.__dict__:
            return cls._instance
        return None

    @classmethod
    def _register_as_static_config(cls, filename):
        """
        Set this class as the main config model
        and allows to get/set values by using static attributes
        """
        Log.debug(f"Registering config file: {filename}")
        cls._instance = cls(filename)

    @classmethod
    def _decorated_as_static_field(cls, field_name):
        """
        Set this class as a static field
        """
        Log.debug(f"Registering static field: {field_name}")
        field_instance = FieldInstance()
        field_instance.name = field_name
        cls._instance = cls(field_instance=field_instance)
        field_instance.definition = cls._instance

    @classmethod
    def __iter_class_attributes(cls):
        """
        Iterate through all class attributes

        :return: generator of (attr_name, default_value, annotated_type)
        :rtype: Generator[Tuple[str, Any, Any]]
        """
        # set to store already returned fields
        returned_fields = set()

        # iterate through annotations
        if hasattr(cls, "__annotations__") and cls.__annotations__:
            for attr_name, annotated_type in cls.__annotations__.items():
                default_value = getattr(cls, attr_name, None)

                assert attr_name not in returned_fields, "Field name is already initialized. This is a bug in ConfigModel library, please report it."

                returned_fields.add(attr_name)
                yield attr_name, default_value, annotated_type
        # iterate through all attributes
        for attr_name in dir(cls):
            if attr_name.startswith("_"):
                continue
            if attr_name in returned_fields:
                continue
            default_value = getattr(cls, attr_name, None)
            # annotated_type = None
            # if hasattr(cls, "__annotations__"):
            #     annotated_type = cls.__annotations__.get(attr_name, None)
            returned_fields.add(attr_name)
            yield attr_name, default_value, None

    def _get_all_fields_recursive(self) -> List[FieldInstance]:
        """
        Get all fields recursively
        """
        assert self._fields is not None, "Fields are not initialized. This is a bug in ConfigModel library, please report it."

        all_fields = []
        for field_name, field in self._fields.items():
            if isinstance(field.definition, ConfigModel):
                nested_fields = field.definition._get_all_fields_recursive()
                assert nested_fields is not None, "Nested fields are None. This is a bug in ConfigModel library, please report it."
                all_fields += nested_fields
            else:
                assert isinstance(field.definition, FieldBase), "Unknown type of field definition. This is a bug in ConfigModel library, please report it."
                all_fields.append(field)
        return all_fields

    def _initialize_fields(self, this_field: FieldInstance):
        """
        Initialize fields
        """
        assert self._fields is None, "Attempt to initialize fields twice. This is a bug in ConfigModel library, please report it."
        self._fields = {}

        # set this field instance
        self._field_instance = this_field
        # get all static fields from class
        for attr_name, default_value, annotated_type in self.__iter_class_attributes():
            # Log.debug(f"attr_name: {attr_name}")

            assert attr_name not in self._fields, "Field name is already initialized. This is a bug in ConfigModel library, please report it."

            new_field_instance = FieldInstance()
            new_field_instance.parent_field = this_field
            new_field_instance.name = attr_name
            new_field_instance.serializer = this_field.serializer

            # deduce field definition
            if isinstance(default_value, FieldBase):
                # just use the field definition
                # create a copy of the field definition, because the one in the class is static
                new_field_instance.definition = copy.deepcopy(default_value)
                new_field_instance.name = default_value.name
            elif isinstance(default_value, type) and issubclass(default_value, ConfigModel):
                # this is a nested class definition (not an instance)
                nested_class_definition = default_value
                # first, check if it has decorator to define the field name
                decorated_field_name = None
                decorated_instance = nested_class_definition._get_instance()
                if decorated_instance is not None:
                    decorated_field_name = decorated_instance._field_instance.name
                # second, check if an instance of this class was created by user (not allowed if a decorator was used)
                user_created_instance = None
                user_created_instance_field_name = None
                for chk_attr_name, chk_attr_default_value, _ in self.__iter_class_attributes():
                    if isinstance(chk_attr_default_value, nested_class_definition):
                        user_created_instance = chk_attr_default_value
                        user_created_instance_field_name = chk_attr_name
                        break
                # it is not allowed to use both decorator and nested instance
                # (checked in constructor, so using assert here)
                assert decorated_field_name is None or user_created_instance is None, \
                    "{parent_class_name} has both '@nested_field' decorator and nested instance of {nested_class_name} (named '{field_name}'). " \
                    "Either remove decorator or '{field_name}' definition".format(
                        parent_class_name=self.__name__,
                        nested_class_name=nested_class_definition.__name__,
                        field_name=user_created_instance_field_name
                    )

                if decorated_field_name is not None:
                    # use the field name from the decorator
                    new_field_instance.name = decorated_field_name
                    # update field definition in class instance, because parent class was not set in decorator
                    decorated_instance._field_instance = new_field_instance
                elif user_created_instance is not None:
                    # skip this field, it will be initialized by the nested class instance
                    continue
                else:
                    # field name is not defined, use the class name (converted to snake case)
                    snake_case_class_name = pascal_case_to_snake_case(nested_class_definition.__name__)
                    new_field_instance.name = snake_case_class_name
                    nested_class_definition._decorated_as_static_field(field_name=snake_case_class_name)
                    decorated_instance = nested_class_definition._get_instance()
                    # update field definition in class instance, because parent class was not set in decorator
                    decorated_instance._field_instance = new_field_instance
                # set the field definition
                new_field_instance.definition = decorated_instance
                # initialize nested class fields
                decorated_instance._initialize_fields(new_field_instance)
            elif isinstance(default_value, ConfigModel):
                # this is a nested config instance
                nested_config_static_instance = default_value
                # create a copy of the nested config instance, because the one in the class is static
                nested_config_instance = copy.deepcopy(nested_config_static_instance)
                new_field_instance.definition = nested_config_instance
                # initialize nested class fields
                nested_config_instance._initialize_fields(new_field_instance)
            elif isinstance(default_value, (str, int, float, bool)):
                # create a field definition
                new_field_instance.definition = FieldBase(name=attr_name, default_value=default_value)
            elif default_value is None:
                # default type is string
                new_field_instance.definition = FieldBase(name=attr_name, default_value="")
            else:
                # currently not supported
                raise Exception("Unsupported type of field definition in class {class_name}. Field '{field_name}' has unsupported type: {field_type}".format(
                    class_name=self.__class__.__name__,
                    field_name=attr_name,
                    field_type=type(default_value)
                ))
                pass
            # finished deducing field definition
            # check if field definition was set
            assert new_field_instance.definition is not None, "Field definition is not set. This is a bug in ConfigModel library, please report it."
            # add field to the list
            self._fields[attr_name] = new_field_instance
        serializer = self._serializer
        if serializer is not None:
            default_values = []
            for field_instance in self._get_all_fields_recursive():
                default_value = SerializerBase.FieldDefaultValue(field_instance.get_path(), field_instance.definition.default_value)
                default_values.append(default_value)
            serializer.write_default_values_from_model(default_values)
