# -*- coding: utf-8 -*-
from configmodel import ConfigModel


def config_file(filename):
    """
    Decorator for ConfigModel classes to set the config file
    """
    print("config_file decorator called, filename: %s" % filename)

    def decorator(cls):
        """
        :type cls: ConfigModel
        """
        cls._register_as_static_config(filename=filename)
        return cls

    return decorator


def nested_field(field_name):
    """
    Decorator for nested ConfigModel classes to define the field name in the parent class
    """
    def decorator(cls):
        """
        :type cls: ConfigModel
        """
        cls._decorated_as_static_field(field_name=field_name)
        return cls
    return decorator
