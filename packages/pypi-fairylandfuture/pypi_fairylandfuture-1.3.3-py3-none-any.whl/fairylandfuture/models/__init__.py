# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2024-05-18 18:44:08 UTC+08:00
"""

from ._base import BaseModel
from ._base.postgresql import BaseModelPostgreSQL

__all__ = [
    "BaseModel",
    "BaseModelPostgreSQL",
]
