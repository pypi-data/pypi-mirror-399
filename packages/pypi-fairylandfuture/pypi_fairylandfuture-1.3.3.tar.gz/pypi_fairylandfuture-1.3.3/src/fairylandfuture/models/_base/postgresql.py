# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2025-12-31 01:27:05 UTC+08:00
"""

import typing as t

from sqlalchemy.orm import declared_attr

from . import BaseModel


class BaseModelPostgreSQL(BaseModel):
    """
    Provides an abstract base model for defining PostgreSQL database tables.

    This class is intended to be used as a base for creating table definitions
    in a PostgreSQL database. The class leverages SQLAlchemy's BaseModel and
    adds functionality for specifying a schema for the table. All child classes
    must define their specific table attributes and will automatically inherit
    the schema specified in this base class.

    :ivar __table_schema__: The default schema name for the table in the PostgreSQL database.
    :type __table_schema__: str
    """

    __abstract__ = True
    __table_schema__ = "public"

    @classmethod
    @declared_attr
    def __table_args__(cls) -> t.Dict[str, str]:
        return {"schema": cls.__table_schema__}
