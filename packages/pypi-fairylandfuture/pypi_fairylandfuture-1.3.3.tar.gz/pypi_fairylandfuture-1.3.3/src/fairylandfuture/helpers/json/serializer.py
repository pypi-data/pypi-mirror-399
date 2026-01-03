# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2025-05-14 10:48:20 UTC+08:00
"""

import json
import typing as t

from fairylandfuture import logger
from fairylandfuture.helpers.json.encoder import JsonEncoder

ClazzType = t.TypeVar("ClazzType")
StrAny = t.TypeVar("StrAny", str, bytes, bytearray)


class JsonSerializerHelper:
    """
    Helper class for JSON serialization and deserialization.

    This class provides utility methods for serializing objects to JSON strings and
    deserializing JSON strings or dictionaries into Python objects. It leverages the
    `json` module for processing JSON data and supports custom class deserialization.
    """

    @classmethod
    def serialize(cls, value):
        """
        Serializes a given Python object into a JSON-formatted string. The method ensures that
        the serialization process adheres to specific formatting rules, including sorting keys,
        disabling ASCII-only encoding, and using a custom JSON encoder. This is particularly useful
        for maintaining consistent JSON output across various operations.

        :param value: The Python object to serialize. Can include data types such as dictionaries,
            lists, strings, integers, and custom objects supported by the specified JSON encoder.
        :type value: Any
        :return: A JSON-formatted string representation of the input value.
        :rtype: str
        """
        logger.debug(f"Serializing value of type {type(value)}")
        return json.dumps(value, cls=JsonEncoder, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    @classmethod
    def deserialize(cls, value: t.Union[StrAny, t.Dict[str, t.Any]], clazz: t.Optional[t.Callable[..., ClazzType]] = None) -> ClazzType:
        """
        Deserialize a value into a Python object, optionally using a provided class type.

        This method allows for the deserialization of either JSON strings or dictionaries
        into Python objects. If a specific class is provided, the data will be used to create
        an instance of that class. If no class is provided, the method defaults to returning
        a dictionary when deserializing JSON strings.

        :param value: The input data to deserialize. Can be either a dictionary or a JSON string.
        :type value: Union[Dict[str, Any], str]
        :param clazz: An optional callable that specifies the class to which the value should
            be deserialized. If provided, value will be converted to an instance of this class.
        :type clazz: Optional[Callable[..., ClazzType]]
        :return: The deserialized object, which may be either a dictionary or an instance of the specified class.
        :rtype: ClazzType
        """
        logger.debug(f"Deserializing value of type {type(value)} to class {clazz}")
        if isinstance(value, t.Dict):
            if not clazz:
                return value
            logger.debug(f"Deserializing dict to class {clazz}")
            return clazz(**value)

        if not clazz:
            logger.debug("No class provided, deserializing to dict")
            return json.loads(value)

        logger.debug(f"Deserializing to class {clazz} using object_hook")
        return json.loads(value, object_hook=lambda x: clazz(**x))
