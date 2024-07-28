# -*- coding: utf-8 -*-
import inspect
import os

from configmodel.Logger import Log

from configmodel import ConfigModel


def config_file(filename):
    """
    Decorator for ConfigModel classes to set the config file
    """
    Log.debug("config_file decorator called, filename: %s" % filename)

    def decorator(cls):
        """
        :type cls: ConfigModel
        """
        # check if file path is relative
        if not os.path.isabs(filename):
            # file must be relative to the same directory as the script using the decorator
            client_script_path = inspect.getfile(cls)
            client_script_dir = os.path.dirname(client_script_path)
            abs_file_path = os.path.join(client_script_dir, filename)
        else:
            abs_file_path = filename

        cls._register_as_static_config(filename=abs_file_path)
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
