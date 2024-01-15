# -*- coding: utf-8 -*-


class MixinCachedValues:
    """
    Mixin for caching values
    """
    class CachedValue:
        """
        Cached value
        """
        def __init__(self, path, value, is_dirty=False):
            self.path = path
            self.value = value
            self.is_dirty = is_dirty

    def __init__(self):
        self._cached_values = None
        self._is_dirty = False

    @staticmethod
    def _path_to_str(path):
        """
        Convert path to string
        """
        return ".".join(path)

    def _set_not_dirty(self):
        """
        Set all cached values to not dirty
        """
        self._is_dirty = False
        if self._cached_values is None:
            return
        for cached_value in self._cached_values.values():
            cached_value.is_dirty = False

    def get_cached_value(self, path):
        """
        Get cached value
        """
        if self._cached_values is None:
            return None
        full_name = self._path_to_str(path)
        cached_value = self._cached_values.get(full_name)
        if cached_value is None:
            return None
        return cached_value.value

    def set_cached_value(self, path, value):
        """
        Set cached value
        """
        self._is_dirty = True
        if self._cached_values is None:
            self._cached_values = {}
        full_name = self._path_to_str(path)
        if full_name not in self._cached_values:
            self._cached_values[full_name] = self.CachedValue(path, value, True)
        else:
            self._cached_values[full_name].value = value
            self._cached_values[full_name].is_dirty = True

    def assign_cached_values(self, cached_values):
        """
        Assign cached values
        """
        self._cached_values = cached_values
        self._is_dirty = False
