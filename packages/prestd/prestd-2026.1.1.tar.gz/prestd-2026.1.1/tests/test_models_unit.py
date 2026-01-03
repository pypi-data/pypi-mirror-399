from __future__ import annotations

from dataclasses import dataclass
from pydantic import BaseModel

from prestd.models import pydantic_encode


class User(BaseModel):
    id: int


@dataclass
class D:
    x: int


def test_pydantic_encode_branches():
    assert pydantic_encode(User(id=1)) == {"id": 1}
    assert pydantic_encode(D(2)) == {"x": 2}
    assert pydantic_encode({"a": 1}) == {"a": 1}
