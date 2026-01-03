# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2025-12-31 01:26:01 UTC+08:00
"""

import datetime
import typing as t

from sqlalchemy import Integer, DateTime, Boolean
from sqlalchemy import inspect
from sqlalchemy.orm import Mapped, DeclarativeBase, Session, mapped_column

from fairylandfuture import logger
from fairylandfuture.core.superclass.schema import BaseSchema
from fairylandfuture.utils import DateTimeUtils

BaseModelType = t.TypeVar("BaseModelType", bound="BaseModel")


class BaseModel(DeclarativeBase):
    """
    Base class for SQLAlchemy models.

    Serves as an abstract base class for database models, providing common attributes
    such as `id`, `created_at`, `updated_at`, and `deleted`. Includes utility methods
    like record retrieval, dictionary conversion, and schema-based object creation.

    :ivar id: Unique identifier for the model instance.
    :type id: int
    :ivar created_at: Timestamp indicating when the record was created.
    :type created_at: datetime.datetime
    :ivar updated_at: Timestamp indicating when the record was last updated.
    :type updated_at: datetime.datetime
    :ivar deleted: Mark for soft deletion. A value of `False` indicates the record
        is active, while `True` means the record is marked as deleted.
    :type deleted: bool
    """

    __abstract__: bool = True

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="ID",
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=DateTimeUtils.unzone_cst,
        nullable=False,
        comment="Create time",
    )

    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=DateTimeUtils.unzone_cst,
        onupdate=DateTimeUtils.unzone_cst,
        nullable=False,
        comment="Update time",
    )

    deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Soft erase marker: false=normal, ture=delete",
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted

    @classmethod
    def from_schema(cls, schema: BaseSchema) -> "BaseModelType":
        ins = cls()
        for field, value in schema.to_dict().items():
            if hasattr(ins, field):
                setattr(ins, field, value)
        return ins

    def to_dict(self, exclude: t.Optional[t.Iterable[str]] = None) -> t.Dict[str, t.Any]:
        if exclude is None:
            exclude = set()

        return {column.name: getattr(self, column.name) for column in inspect(self.__class__).columns if column.name not in exclude}

    @classmethod
    def get_by_id(cls, session: Session, record_id: int) -> t.Optional["BaseModel"]:
        try:
            return session.query(cls).filter(cls.id == record_id, cls.deleted == False).first()
        except Exception as err:
            logger.error(f"Failed to query {cls.__name__}, ID: {record_id}, error: {err}")
            return None

    @classmethod
    def get_all(cls, session: Session, limit: int = None, offset: int = None) -> t.List[t.Type["BaseModelType"]]:
        try:
            query = session.query(cls).filter(cls.deleted == False)

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            return query.all()
        except Exception as err:
            logger.error(f"Failed to query {cls.__name__} list, error: {err}")
            return list()

    def refresh(self, session: Session) -> None:
        try:
            session.refresh(self)
        except Exception as err:
            logger.error(f"Failed to refresh {self.__class__.__name__} instance, error: {err}")
