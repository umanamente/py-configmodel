# -*- coding: utf-8 -*-
import configparser
import os

from configmodel.Logger import Log
from configmodel.MixinCachedValues import MixinCachedValues
from configmodel.MixinDelayedWrite import MixinDelayedWrite
from configmodel.SerializerBase import SerializerBase


class SerializerIni(SerializerBase, MixinCachedValues, MixinDelayedWrite):
    DEFAULT_SECTION = "Global"

    class ParameterLocation:

        def __init__(self):
            self.section = None
            self.parameter = None

        @property
        def full_name(self):
            return f"[{self.section}] {self.parameter}"

        def __repr__(self):
            return self.full_name

    def __init__(self, filename):
        SerializerBase.__init__(self, filename)
        MixinCachedValues.__init__(self)
        MixinDelayedWrite.__init__(self, delayed_write_enabled=False)

    @staticmethod
    def _get_parameter_location(path):
        """
        Get section and parameter name from path
        """
        location = SerializerIni.ParameterLocation()
        if len(path) == 1:
            # place parameter in default section
            location.section = SerializerIni.DEFAULT_SECTION
            location.parameter = path[0]
        else:
            assert len(path) > 1
            # place parameter in section
            location.section = path[0]
            location.parameter = ".".join(path[1:])
        return location

    def _commit_delayed_write(self):
        """
        Write cached values to INI file
        """
        Log.debug(f"Writing cached values to INI file: {self.filename}")
        ini = configparser.ConfigParser()
        ini.read(self.filename)
        for full_name, cached_value in self._cached_values.items():
            location = self._get_parameter_location(cached_value.path)
            if not ini.has_section(location.section):
                ini.add_section(location.section)
            do_write = False
            # write value if it is dirty
            if cached_value.is_dirty:
                do_write = True
            # also write value if it is not in INI file
            if not ini.has_option(location.section, location.parameter):
                do_write = True
            # write value
            if do_write:
                ini.set(location.section, location.parameter, str(cached_value.value))
        with open(self.filename, "w") as config_file:
            ini.write(config_file)
        self._set_not_dirty()

    def set_value(self, path, value):
        if not path:
            raise ValueError("Parameter path is empty. This is likely a bug in ConfigModel. Please report it.")
        # set cached value
        self.set_cached_value(path, value, is_dirty=True)
        # initiate delayed write
        self._restart_delayed_timer()

    def get_value(self, path):
        if not path:
            raise ValueError("Parameter path is empty. This is likely a bug in ConfigModel. Please report it.")
        Log.debug(f"Getting value of field '{path}'")
        # get cached value
        cached_value = self.get_cached_value(path)
        return cached_value

    def write_default_values_from_model(self, default_values):
        """
        Write default values to configuration file, if they are not already set
        """
        if not os.path.exists(self.filename):
            Log.debug(f"Creating new configuration file: {self.filename}")
            open(self.filename, "w").close()
        ini = configparser.ConfigParser()
        ini.read(self.filename)

        # read all values from INI file to cache
        cached_values = {}
        for section in ini.sections():
            section_path = []
            if section != SerializerIni.DEFAULT_SECTION:
                section_path = [section]
            for parameter in ini[section]:
                parameter_path = section_path + parameter.split(".")
                value = ini[section][parameter]
                full_name = self._path_to_str(parameter_path)
                cached_values[full_name] = self.CachedValue(parameter_path, value, False)

        # write default values, if not already set in INI file
        for field in default_values:
            location = self._get_parameter_location(field.path)
            if not ini.has_section(location.section):
                ini.add_section(location.section)
            if not ini.has_option(location.section, location.parameter):
                Log.debug(f"Writing default value of field '{field.path}' to '{field.value}', location: {location}")
                ini.set(location.section, location.parameter, str(field.value))
            # add to cached values (if not already there)
            full_name = self._path_to_str(field.path)
            if full_name not in cached_values:
                cached_values[full_name] = self.CachedValue(field.path, field.value, False)
        # assign cached values
        self.assign_cached_values(cached_values)
        # write INI file
        with open(self.filename, "w") as config_file:
            ini.write(config_file)


