# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2025-11-26 12:54:27 UTC+08:00
"""

import datetime
import hashlib
import json
import typing as t
import uuid

from pydantic import BaseModel, ConfigDict, Field, field_serializer
from pydantic.alias_generators import to_camel

from fairylandfuture import logger
from fairylandfuture.enums import DateTimeEnum
from fairylandfuture.utils import DateTimeUtils


class PrimitiveSchema(BaseModel):
    """
    Represents a schema with support for data serialization and configuration.

    The PrimitiveSchema class is built on top of the BaseModel and provides methods
    to serialize model instances into different representations such as dictionaries
    and JSON strings. It includes configurations that influence serialization behavior,
    such as attribute naming conventions and whitespace handling.

    :ivar model_config: Configuration dictionary that defines the behavior of the schema,
        including attribute aliasing, model population strategies, whitespace stripping,
        extra field handling, and assignment validation.
    :type model_config: ConfigDict
    """

    model_config: t.ClassVar[ConfigDict] = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        str_strip_whitespace=True,
        extra="ignore",
        validate_assignment=True,
    )

    def to_dict(self, /, *, exclude_fields: t.Optional[t.Iterable[str]] = None, exclude_none: bool = False, to_camel: bool = False) -> t.Dict[str, t.Any]:
        """
        Converts the object into a dictionary representation. Allows customization of
        the dictionary transformation by excluding specific fields, omitting keys with
        `None` values, or using camelCase for keys.

        :param exclude_fields: Specifies which fields to exclude from the resulting
            dictionary. If None, no fields are excluded.
        :type exclude_fields: Optional[Iterable[str]]
        :param exclude_none: If True, keys with `None` values are omitted from the
            resulting dictionary. Defaults to False.
        :type exclude_none: bool
        :param to_camel: If True, keys are transformed into camelCase format in the
            resulting dictionary. Defaults to False.
        :type to_camel: bool
        :return: A dictionary representation of the object based on the provided
            customization options.
        :rtype: Dict[str, Any]
        """
        logger.debug(f"Serializing {self.__class__.__name__!r} to dict(mode=python)...")
        return self.model_dump(mode="python", exclude=set(exclude_fields) if exclude_fields else None, exclude_none=exclude_none, by_alias=to_camel)

    def to_serializable_dict(self, /, *, exclude_fields: t.Optional[t.Iterable[str]] = None, exclude_none: bool = False, to_camel: bool = False) -> t.Dict[str, t.Any]:
        """
        Converts the object to a dictionary representation, suitable for JSON serialization. Provides options
        to exclude specific fields, omit fields with `None` values, and convert keys to camelCase format. This
        method utilizes the model's internal serialization functionality to produce the dictionary.

        :param exclude_fields: An optional iterable of field names to be excluded from the serialized dictionary.
        :type exclude_fields: Optional[Iterable[str]]
        :param exclude_none: A boolean indicating whether fields with `None` values should be excluded.
        :type exclude_none: bool
        :param to_camel: A boolean indicating whether the dictionary keys should be converted to camelCase.
        :type to_camel: bool
        :return: A dictionary representation of the object, optionally filtered and formatted based on the
            specified parameters.
        :rtype: Dict[str, Any]
        """
        logger.debug(f"Serializing {self.__class__.__name__!r} to dict(mode=json)...")
        return self.model_dump(mode="json", exclude=set(exclude_fields) if exclude_fields else None, exclude_none=exclude_none, by_alias=to_camel)

    def to_json_string(self, indent: int = 2) -> str:
        """
        Serializes the current object instance into a JSON string.

        This method uses the ``model_dump_json`` function to generate
        a JSON string representation of the object, ensuring the specified
        indentation and disabling ASCII encoding for Unicode characters.

        :param indent: The number of spaces to use for indentation in the
            JSON string. Defaults to 2.
        :type indent: int
        :return: A JSON string representation of the object.
        :rtype: str
        """
        logger.debug(f"Serializing {self.__class__.__name__!r} to JSON string...")
        return self.model_dump_json(indent=indent, ensure_ascii=False)


class EntitySchema(PrimitiveSchema):
    """
    Represents a schema for an entity with attributes commonly used for
    tracking its state and identification.

    This schema is designed to manage various primary details such as
    unique identification, timestamps for creation and updates, and
    existence status. It also includes serialization functionality for
    datetime fields.

    :ivar id: The unique identifier for the entity, which is optional.
    :type id: Optional[int]
    :ivar uuid: The universally unique identifier for the entity, automatically
        generated if not provided. This attribute is immutable once set.
    :type uuid: str
    :ivar created_at: The timestamp indicating when the entity was created.
        Defaults to the current timestamp in CST timezone. This attribute
        is immutable once set.
    :type created_at: datetime.datetime
    :ivar updated_at: The timestamp indicating when the entity was last updated.
        Defaults to the current timestamp in CST timezone.
    :type updated_at: datetime.datetime
    :ivar existed: A flag indicating whether the entity is considered existent.
        Defaults to True.
    :type existed: bool
    """

    id: t.Optional[int] = Field(description="ID")
    uuid: str = Field(default_factory=lambda: uuid.uuid4().hex, description="UUID", frozen=True)
    created_at: datetime.datetime = Field(default_factory=lambda: DateTimeUtils.unzone_cst(), description="Create Time", frozen=True)
    updated_at: datetime.datetime = Field(default_factory=lambda: DateTimeUtils.unzone_cst(), description="Update Time")
    existed: bool = Field(default=True, description="Is Existed Flag")

    @field_serializer("created_at", "updated_at", when_used="json")
    def __serialize_datetime(self, dt: datetime.datetime) -> str:
        return dt.strftime(DateTimeEnum.DATETIME.value)


class BaseSchema(EntitySchema):
    """
    Represents a base schema for data models, providing utility methods for hashing and updating
    attributes dynamically. Designed for models that require a structured schema with update
    capabilities while maintaining immutability for certain fields.

    This class is intended to serve as a base schema for more specialized schemas, enabling
    common functionality and easing development of derived classes.

    :ivar id: The unique identifier for an entity (immutable).
    :type id: Any
    :ivar uuid: The universally unique identifier for an entity (immutable).
    :type uuid: Any
    :ivar created_at: The creation timestamp of the entity (immutable).
    :type created_at: datetime
    :ivar updated_at: The timestamp of the last update to the entity.
    :type updated_at: datetime
    """

    @property
    def hashcode(self) -> str:
        """
        Calculates and returns the unique hashcode for the current object instance. The hashcode
        is generated by serializing the instance's data excluding specific attributes to a JSON
        string, sorting its keys, and producing an MD5 hash of the resulting string. This is useful
        for ensuring the integrity of the instance's data and tracking changes.

        :returns: MD5 hash representation of the object's data.
        :rtype: str
        """
        data = self.model_dump(mode="json", exclude={"id", "uuid", "created_at", "updated_at"})
        result = hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
        logger.debug(f"Calculating hashcode for {self.__class__.__name__!r} with result: {result!r}")
        return result

    def update(self, **kwargs) -> t.Self:
        """
        Updates the attributes of the object with the provided keyword arguments, while preventing modifications
        to certain protected fields. Only attributes that have a different value than the one provided in the
        arguments will be updated, and the `updated_at` attribute will be set to the current unzoned CST time
        if any updates occur.

        :param kwargs: Keyword arguments containing the field names and values for updates. Only fields that exist on the object,
            are not protected, and have a different value will be modified.
        :type kwargs: dict
        :return: The instance of the object after potential modifications.
        :rtype: t.Self
        """
        flag = False
        frozen_fields = ("id", "uuid", "created_at")
        for field, value in kwargs.items():
            if field not in frozen_fields and hasattr(self, field) and getattr(self, field) != value:
                logger.debug(f"Updating field {field!r} of {self.__class__.__name__!r} from {getattr(self, field)!r} to {value!r}")
                setattr(self, field, value)
                flag = True

        if flag:
            self.updated_at = DateTimeUtils.unzone_cst()

        return self
