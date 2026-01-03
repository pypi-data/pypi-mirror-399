from __future__ import annotations

import asyncio
import uuid

import pytest
from prestd import AsyncPrestd

pytestmark = pytest.mark.integration


def _unique_email() -> str:
    return f"test-{uuid.uuid4().hex[:12]}@example.com"


def test_async_crud(require_integration, settings, aclient):
    async def _run():
        async with aclient as c:
            users = c.table(settings.users_table)

            email = _unique_email()
            _ = await users.insert({"email": email, "active": True, "role": "async"})

            row = await users.where(email=email).one()
            uid = int(row["id"])

            _ = await users.where(id=uid).update({"role": "async-updated"})
            row2 = await users.where(id=uid).one()
            assert row2["role"] == "async-updated"

            _ = await users.where(id=uid).delete()
            gone = await users.where(id=uid).maybe_one()
            assert gone is None

    asyncio.run(_run())
