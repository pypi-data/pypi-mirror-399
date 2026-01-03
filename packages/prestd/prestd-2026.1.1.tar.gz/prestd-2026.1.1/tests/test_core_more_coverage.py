from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

import httpx
import pytest

from prestd.core import (
    AsyncPrestd,
    AsyncTable,
    Prestd,
    Table,
    PrestdUsageError,
    _build_filter_value,  # yes, test private helpers for coverage
    _coerce_nested_json_values,  # same
    _parse_where_kwargs,
    _truncate,
)


def test_truncate_branches():
    assert _truncate("abc", 0) == ""
    assert _truncate("abc", -1) == ""
    assert _truncate("abc", 10) == "abc"
    assert _truncate("abcdef", 4).endswith("…")


def test_coerce_nested_json_values_branches():
    # scalar passthrough
    assert _coerce_nested_json_values(123) == 123

    # list recursion: list elements are preserved (dict element stays a dict)
    assert _coerce_nested_json_values([{"a": 1}, 2]) == [{"a": 1}, 2]

    # dict: nested dict/list values -> JSON strings
    out = _coerce_nested_json_values({"x": {"a": 1}, "y": [1, 2], "z": "ok"})
    assert out["x"] == '{"a":1}'
    assert out["y"] == "[1,2]"
    assert out["z"] == "ok"

    # list of rows: rows preserved, but nested values encoded inside each row
    rows = _coerce_nested_json_values(
        [{"profile": {"name": "A"}}, {"tags": ["x", "y"]}]
    )
    assert rows[0]["profile"] == '{"name":"A"}'
    assert rows[1]["tags"] == '["x","y"]'


def test_filter_operator_branches():
    assert _build_filter_value("true", True) == "$true"
    assert _build_filter_value("false", True) == "$false"
    assert _build_filter_value("notnull", True) == "$notnull"
    assert _build_filter_value("nin", [1, 2]) == "$nin.1,2"

    with pytest.raises(PrestdUsageError):
        _ = _build_filter_value("nin", 123)


def test_parse_where_kwargs_branches():
    out = _parse_where_kwargs({"id__gte": 5, "name": "x"})
    assert ("id", "$gte.5") in out
    assert ("name", "x") in out


def test_query_first_one_on_object_response():
    # For .first() and .one() when server returns an object (not list)
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"id": 1, "email": "a@b.com"})

    hc = httpx.Client(transport=httpx.MockTransport(handler))
    c = Prestd("http://mock", database="prest", schema="public", client=hc)

    q = c.table("users").query()
    assert q.first() == {"id": 1, "email": "a@b.com"}
    assert q.one() == {"id": 1, "email": "a@b.com"}


def test_iter_exits_on_empty_batch():
    # Ensure Query.iter stops on empty list
    calls = {"n": 0}

    def handler(req: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(200, json=[])

    hc = httpx.Client(transport=httpx.MockTransport(handler))
    c = Prestd("http://mock", database="prest", schema="public", client=hc)

    items = list(c.table("users").query().iter(page_size=10))
    assert items == []
    assert calls["n"] == 1


def test_table_with_codec_and_insert_many_non_list_response():
    # insert_many(copy) may return None or object; ensure branch coverage
    def handler(req: httpx.Request) -> httpx.Response:
        # simulate prestd returning {"rows_affected": 2} for batch
        return httpx.Response(200, json={"rows_affected": 2})

    hc = httpx.Client(transport=httpx.MockTransport(handler))
    c = Prestd("http://mock", database="prest", schema="public", client=hc)

    t = c.table("users")
    t2 = t.with_codec(encode=lambda x: x, parse_one=lambda x: x, parse_list=lambda x: x)
    assert isinstance(t2, Table)

    resp = t2.insert_many([{"a": 1}], method="copy")
    assert resp == {"rows_affected": 2}


def test_async_table_with_codec_branches():
    async def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"rows_affected": 1})

    hc = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    c = AsyncPrestd("http://mock", database="prest", schema="public", client=hc)

    at = c.table("users")
    at2 = at.with_codec(
        encode=lambda x: x, parse_one=lambda x: x, parse_list=lambda x: x
    )
    assert isinstance(at2, AsyncTable)

    async def run():
        r = await at2.insert_many([{"a": 1}], method="copy")
        assert r == {"rows_affected": 1}
        await hc.aclose()

    asyncio.run(run())


def test_auth_wrappers_sync_and_async():
    # Cover auth_bearer/auth_basic paths
    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path == "/auth":
            return httpx.Response(200, json={"token": "t"})
        return httpx.Response(200, json={"ok": True})

    # sync
    hc = httpx.Client(transport=httpx.MockTransport(handler))
    c = Prestd("http://mock", database="prest", schema="public", client=hc)
    assert c.auth_bearer("u", "p") == {"token": "t"}
    assert c.auth_basic("u", "p") == {"token": "t"}

    # async
    async def handler_a(req: httpx.Request) -> httpx.Response:
        if req.url.path == "/auth":
            return httpx.Response(200, json={"token": "t"})
        return httpx.Response(200, json={"ok": True})

    ahc = httpx.AsyncClient(transport=httpx.MockTransport(handler_a))
    ac = AsyncPrestd("http://mock", database="prest", schema="public", client=ahc)

    async def run():
        assert await ac.auth_bearer("u", "p") == {"token": "t"}
        assert await ac.auth_basic("u", "p") == {"token": "t"}
        await ahc.aclose()

    asyncio.run(run())


def test_close_paths_when_client_injected():
    # owns_client=False branches: close() should not close injected client
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    injected = httpx.Client(transport=transport)
    c = Prestd("http://mock", database="prest", schema="public", client=injected)
    c.close()

    # injected client should still work (if prestd tried to close it, this may error)
    r = injected.get("http://mock/_health")
    assert r.status_code == 200

    async def handler_a(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ok": True})

    a_injected = httpx.AsyncClient(transport=httpx.MockTransport(handler_a))
    ac = AsyncPrestd(
        "http://mock", database="prest", schema="public", client=a_injected
    )

    async def run():
        await ac.aclose()
        # async injected still usable
        resp = await a_injected.get("http://mock/_health")
        assert resp.status_code == 200
        await a_injected.aclose()

    asyncio.run(run())
