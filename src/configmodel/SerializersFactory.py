# -*- coding: utf-8 -*-
from typing import List, Type

from configmodel.SerializerIni import SerializerIni


class SerializersFactory:

    SUPPORTED_SERIALIZERS: list[list[Type[SerializerIni] | list[str]]] = [
        [SerializerIni, [".ini"]]
    ]

    @classmethod
    def get_all_supported_extensions(cls):
        """
        Get all supported extensions
        """
        extensions = []
        for serializer in cls.SUPPORTED_SERIALIZERS:
            extensions += serializer[1]
        return extensions

    @classmethod
    def get_serializer_by_filename(cls, filename):
        """
        Get serializer by filename
        """
        for serializer in cls.SUPPORTED_SERIALIZERS:
            for extension in serializer[1]:
                if filename.endswith(extension):
                    return serializer[0](filename)
        else:
            raise Exception("Unknown file extension for filename: %s. Supported extensions: %s" % (
                filename,
                ", ".join(["'%s'" % extension for extension in cls.get_all_supported_extensions()])
            ))
