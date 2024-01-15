# -*- coding: utf-8 -*-
import configparser
import os

from configmodel.Logger import Log
from configmodel.MixinCachedValues import MixinCachedValues
from configmodel.SerializerBase import SerializerBase


class SerializerIni(SerializerBase, MixinCachedValues):

    class ParameterLocation:
        DEFAULT_SECTION = "Global"

        def __init__(self):
            self.section = None
            self.parameter = None

        @property
        def full_name(self):
            return f"[{self.section}] {self.parameter}"

        def __repr__(self):
            return self.full_name

    def __init__(self, filename):
        super().__init__(filename)
        super(MixinCachedValues, self).__init__()

    @staticmethod
    def _get_parameter_location(path):
        """
        Get section and parameter name from path
        """
        location = SerializerIni.ParameterLocation()
        if len(path) == 0:
            return location
        if len(path) == 1:
            # place parameter in default section
            location.section = SerializerIni.ParameterLocation.DEFAULT_SECTION
            location.parameter = path[0]
        else:
            # place parameter in section
            location.section = path[0]
            location.parameter = ".".join(path[1:])
        return location

    def _write_all_values_to_ini(self):
        """
        Write cached values to INI file
        """
        Log.debug(f"Writing cached values to INI file: {self.filename}")
        ini = configparser.ConfigParser()
        ini.read(self.filename)
        for full_name, cached_value in self._cached_values.items():
            if not cached_value.is_dirty:
                # write only dirty values
                continue
            location = self._get_parameter_location(cached_value.path)
            if not ini.has_section(location.section):
                ini.add_section(location.section)
            ini.set(location.section, location.parameter, str(cached_value.value))
        with open(self.filename, "w") as config_file:
            ini.write(config_file)
        self._set_not_dirty()

    def _read_all_values_from_ini(self):
        """
        Read all values from INI file to cache
        """
        Log.debug(f"Reading all values from INI file: {self.filename}")
        ini = configparser.ConfigParser()
        ini.read(self.filename)
        cached_values = {}
        for section in ini.sections():
            section_path = []
            if section != SerializerIni.ParameterLocation.DEFAULT_SECTION:
                section_path = [section]
            for parameter in ini[section]:
                parameter_path = section_path + [parameter.split(".")]
                value = ini[section][parameter]
                full_name = self._path_to_str(parameter_path)
                cached_values[full_name] = self.CachedValue(parameter_path, value, False)
        self.assign_cached_values(cached_values)

    def set_value(self, path, value):
        location = self._get_parameter_location(path)
        Log.debug(f"Setting value of field '{path}' to '{value}', location: {location}")
        ini = configparser.ConfigParser()
        ini.read(self.filename)
        ini.set(location.section, location.parameter, value)
        with open(self.filename, "w") as config_file:
            ini.write(config_file)

    def get_value(self, path):
        location = self._get_parameter_location(path)
        Log.debug(f"Getting value of field '{path}', location: {location}")
        ini = configparser.ConfigParser()
        ini.read(self.filename)
        try:
            return ini.get(location.section, location.parameter)
        except configparser.NoSectionError:
            Log.debug(f"Section '{location.section}' does not exist, returning None")
            return None
        except configparser.NoOptionError:
            Log.debug(f"Option '{location.parameter}' does not exist, returning None")
            return None
        except Exception as e:
            Log.error(f"Unknown error: {e}")
            raise e

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
            if section != SerializerIni.ParameterLocation.DEFAULT_SECTION:
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
        with open(self.filename, "w") as config_file:
            ini.write(config_file)


