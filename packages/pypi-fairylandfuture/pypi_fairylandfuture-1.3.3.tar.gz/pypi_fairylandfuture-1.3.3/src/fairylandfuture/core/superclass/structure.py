# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2024-06-04 10:38:31 UTC+08:00
"""

import json
import typing as t
from dataclasses import dataclass, asdict, astuple, field, fields

from fairylandfuture import logger
from fairylandfuture.models import BaseModel


@dataclass(frozen=False)
class BaseStructure:
    """
    Represents a base structure with functionality for conversion to dictionary, tuple, and JSON string.

    This class provides common methods for data serialization, enabling derived classes to be
    easily represented in various formats such as dictionaries, tuples, or JSON strings.
    It is designed to be extended and should form the foundation of more specialized structures.
    """

    @property
    def asdict(self) -> t.Dict[str, t.Any]:
        return asdict(self)

    @property
    def astuple(self) -> t.Tuple[t.Any, ...]:
        return astuple(self)

    @property
    def string(self) -> str:
        return json.dumps(self.asdict, separators=(",", ":"), ensure_ascii=False)

    def to_dict(self, /, *, ignorenone: bool = False) -> t.Dict[str, t.Any]:
        return {k: v for k, v in self.asdict.items() if v is not None} if ignorenone else self.asdict


@dataclass(frozen=True)
class BaseFrozenStructure:
    """
    Base class for creating immutable data structures.

    This frozen data class serves as a base structure providing utility methods for
    serialization and model conversion. It ensures that instances are immutable and
    can be easily converted to dictionaries, tuples, or JSON strings. It can also
    be constructed from a Pydantic BaseModel.
    """

    @property
    def asdict(self) -> t.Dict[str, t.Any]:
        return asdict(self)

    @property
    def astuple(self) -> t.Tuple[t.Any, ...]:
        return astuple(self)

    @property
    def string(self) -> str:
        return json.dumps(self.asdict, separators=(",", ":"), ensure_ascii=False)

    def to_dict(self, /, *, ignorenone: bool = False) -> t.Dict[str, t.Any]:
        return {k: v for k, v in self.asdict.items() if v is not None} if ignorenone else self.asdict

    @classmethod
    def from_model(cls, model: BaseModel):
        """
        Creates an instance of the class by mapping fields from the given model.

        Uses the provided BaseModel instance to construct a dictionary of
        attributes that correspond to the fields of the class. Any matching
        fields between the model and the class are included in the constructed
        instance.

        :param model: The BaseModel instance containing data to populate the
            class attributes.
        :type model: BaseModel
        :return: An instance of the class, populated with data from the model.
        :rtype: cls
        """
        logger.debug(f"Converting model {model.__class__.__name__!r} to structure {cls.__name__!r}...")
        kwargs = {}
        model_dict = model.to_dict()
        for field in fields(cls):
            if field.name in model_dict:
                kwargs.update({field.name: model_dict.get(field.name)})

        return cls(**kwargs)


@dataclass
class BaseStructureTreeNode:
    """
    Represents a node in a hierarchical structure tree.

    This class is designed to facilitate the representation of hierarchical relationships within a tree-like
    structure. Each node contains an identifier, a reference to its parent node, associated data, and a list
    of its children nodes. The primary usage of this class is for creating hierarchical models that can be
    easily traversed or exported to dictionary forms.

    :ivar id: The unique identifier of the current node.
    :ivar parent_id: The unique identifier of the parent node of the current node.
    :ivar data: A dictionary containing the metadata or associated data of the current node.
    :ivar children: A list of child nodes that belong to the current node. Defaults to an empty list.
    """

    id: t.Any
    parent_id: t.Any
    data: t.Dict[str, t.Any]
    children: t.List["BaseStructureTreeNode"] = field(default=None)

    def __post_init__(self):
        self.children = []

    def get_id(self) -> t.Any:
        return self.id

    def get_parent_id(self) -> t.Any:
        return self.parent_id

    def add_child(self, child: "BaseStructureTreeNode"):
        self.children.append(child)

    def get_children(self) -> t.List["BaseStructureTreeNode"]:
        return self.children

    def to_dict(self) -> t.Dict[str, t.Any]:
        result = {"id": self.id, "parent_id": self.parent_id, "data": self.data, "children": [child.to_dict() for child in self.children]}
        return result
