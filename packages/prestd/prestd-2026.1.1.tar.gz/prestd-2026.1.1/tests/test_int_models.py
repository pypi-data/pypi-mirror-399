from __future__ import annotations

import asyncio
import uuid

import pytest
from pydantic import BaseModel

from prestd.models import as_model

pytestmark = pytest.mark.integration


def _unique_email() -> str:
    return f"test-{uuid.uuid4().hex[:12]}@example.com"


class User(BaseModel):
    id: int
    email: str
    active: bool
    role: str
    profile: dict | None = None


def test_models_sync(settings, client, require_integration):
    users = as_model(client.table(settings.users_table), User)

    email = _unique_email()
    _ = users.insert(
        {"email": email, "active": True, "role": "typed", "profile": {"name": "Typed"}}
    )

    u = users.where(email=email).one()
    assert isinstance(u, User)
    assert u.email == email

    _ = users.where(id=u.id).delete()
    assert users.where(id=u.id).maybe_one() is None


def test_models_async(settings, aclient, require_integration):
    async def _run():
        async with aclient as c:
            users = as_model(c.table(settings.users_table), User)

            email = _unique_email()
            _ = await users.insert(
                {"email": email, "active": True, "role": "typed-async"}
            )

            u = await users.where(email=email).one()
            assert isinstance(u, User)
            assert u.email == email

            _ = await users.where(id=u.id).delete()
            gone = await users.where(id=u.id).maybe_one()
            assert gone is None

    asyncio.run(_run())
