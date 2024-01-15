# -*- coding: utf-8 -*-
import copy
from typing import Dict, Any, Union

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
        if self.serializer is None:
            raise Exception("Serializer is not set")
        if self.name is None:
            raise Exception("Field name is not set")
        return self.serializer.get_value(self.get_path())

    def set_value(self, value):
        if self.serializer is None:
            raise Exception("Serializer is not set")
        if self.name is None:
            raise Exception("Field name is not set")
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
        Log.debug(f"Getting CLASS STATIC attribute: {name}")
        if name.startswith("_"):
            return super().__getattribute__(name)
        # check if class is registered as static config
        instance = cls._get_instance()
        if instance is None:
            # class is not registered as static config
            return super().__getattribute__(name)
        if not isinstance(instance, ConfigModel):
            return super().__getattribute__(name)
        # noinspection PyProtectedMember
        if instance._fields is None or name not in instance._fields:
            return super().__getattribute__(name)
        return instance.__getattribute__(name)

    def __setattr__(cls, name, value):
        Log.debug(f"Setting CLASS STATIC attribute: {name}")
        if name.startswith("_"):
            super().__setattr__(name, value)
            return
        # check if class is registered as static config
        instance = cls._get_instance()
        if instance is None:
            # class is not registered as static config
            super().__setattr__(name, value)
            return
        if not isinstance(instance, ConfigModel):
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
                            f"Creating instances is not allowed. Use static attributes instead.")
        self._serializer = None
        self._fields = None
        self._field_instance = None

        # check if "field_instance" attribute is in kwargs
        if "field_instance" in kwargs:
            self._field_instance = kwargs["field_instance"]

        if filename is not None:
            self._initialize_config(filename)

    def __getattribute__(self, name):
        Log.debug(f"Getting INSTANCE attribute: {name}")
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
            elif isinstance(field.definition, FieldBase):
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
            elif isinstance(field.definition, FieldBase):
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
        """
        for attr_name in cls.__dict__:
            if attr_name.startswith("_"):
                continue
            yield attr_name, getattr(cls, attr_name)

    def _get_field(self, field_name) -> Union[FieldInstance, None]:
        """
        Get field by name
        """
        if self._fields is None:
            Log.debug("Fields are not initialized")
            return None
        return self._fields[field_name]

    def _get_all_fields_recursive(self) -> list[FieldInstance]:
        """
        Get all fields recursively
        """
        if self._fields is None:
            return []
        all_fields = []
        for field_name, field in self._fields.items():
            if isinstance(field.definition, type) and issubclass(field.definition, ConfigModel):
                # todo: is this code reachable (there should be no nested class definitions)
                nested_instance = field.definition._get_instance()
                if nested_instance is None:
                    continue
                nested_fields = nested_instance._get_all_fields_recursive()
                if nested_fields is not None:
                    all_fields += nested_fields
            elif isinstance(field.definition, ConfigModel):
                nested_fields = field.definition._get_all_fields_recursive()
                if nested_fields is not None:
                    all_fields += nested_fields
            elif isinstance(field.definition, FieldBase):
                all_fields.append(field)
        return all_fields

    def _initialize_fields(self, this_field: FieldInstance):
        """
        Initialize fields
        """
        if self._fields is None:
            self._fields = {}
        assert self._fields is not None
        # set this field instance
        self._field_instance = this_field
        # get all static fields from class
        for attr_name, attr in self.__iter_class_attributes():
            # Log.debug(f"attr_name: {attr_name}")

            # check if this field was already initialized (e.g. nested class)
            if attr_name in self._fields:
                continue

            new_field_instance = FieldInstance()
            new_field_instance.parent_field = this_field
            new_field_instance.name = attr_name
            new_field_instance.serializer = this_field.serializer

            # deduce field definition
            if isinstance(attr, FieldBase):
                # just use the field definition
                # create a copy of the field definition, because the one in the class is static
                self._fields[attr.name] = copy.deepcopy(attr)
            elif isinstance(attr, type) and issubclass(attr, ConfigModel):
                # this is a nested class definition (not an instance)
                nested_class_definition = attr
                # first, check if it has decorator to define the field name
                decorated_field_name = None
                decorated_instance = nested_class_definition._get_instance()
                if decorated_instance is not None:
                    decorated_field_name = decorated_instance._field_instance.name
                # second, check if an instance of this class was created by user (not allowed if a decorator was used)
                user_created_instance = None
                user_created_instance_field_name = None
                for chk_attr_name, chk_attr in self.__iter_class_attributes():
                    if isinstance(chk_attr, nested_class_definition):
                        user_created_instance = chk_attr
                        user_created_instance_field_name = chk_attr_name
                        break
                # it is not allowed to use both decorator and nested instance
                if decorated_field_name is not None and user_created_instance is not None:
                    raise Exception(
                        "{parent_class_name} has both '@nested_field' decorator and nested instance of {nested_class_name} (named '{field_name}'). "
                        "Either remove decorator or '{field_name}' definition".format(
                            parent_class_name=self.__name__,
                            nested_class_name=nested_class_definition.__name__,
                            field_name=user_created_instance_field_name
                        )
                    )
                elif decorated_field_name is not None:
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
            elif isinstance(attr, ConfigModel):
                # this is a nested config instance
                nested_config_static_instance = attr
                # create a copy of the nested config instance, because the one in the class is static
                nested_config_instance = copy.deepcopy(nested_config_static_instance)
                new_field_instance.definition = nested_config_instance
                # initialize nested class fields
                nested_config_instance._initialize_fields(new_field_instance)
            elif isinstance(attr, dict):
                # currently not supported
                raise Exception("Dictionary is not supported as a field definition")
                pass
            elif isinstance(attr, list):
                # currently not supported
                raise Exception("List is not supported as a field definition")
                pass
            elif isinstance(attr, (str, int, float, bool)):
                # create a field definition
                new_field_instance.definition = FieldBase(name=attr_name, default_value=attr)
            # finished deducing field definition
            # check if field definition was set
            if new_field_instance.definition is None:
                raise Exception("Field definition is not set")
            # add field to the list
            self._fields[new_field_instance.name] = new_field_instance
        serializer = self._serializer
        if serializer is not None:
            default_values = []
            for field_instance in self._get_all_fields_recursive():
                default_value = SerializerBase.FieldDefaultValue(field_instance.get_path(), field_instance.definition.default_value)
                default_values.append(default_value)
            serializer.write_default_values_from_model(default_values)
