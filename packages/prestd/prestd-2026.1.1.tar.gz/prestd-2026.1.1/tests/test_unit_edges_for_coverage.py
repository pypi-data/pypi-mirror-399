from __future__ import annotations

import asyncio
from dataclasses import dataclass

import httpx
import pytest

from prestd.core import (
    AsyncPrestd,
    Prestd,
    PrestdConnectionError,
    PrestdDecodeError,
    PrestdTimeoutError,
    PrestdUsageError,
    RetryConfig,
    default_encode,
)


@dataclass
class D:
    x: int


def test_default_encode_dataclass():
    assert default_encode(D(1)) == {"x": 1}
    assert default_encode({"a": 1}) == {"a": 1}


def test_page_and_page_size_validation():
    # Use a mock client; no real network.
    c = Prestd(
        "http://mock",
        database="prest",
        schema="public",
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda r: httpx.Response(200, json={"ok": True})
            )
        ),
    )
    q = c.table("users").query()
    with pytest.raises(PrestdUsageError):
        _ = q.page(0)
    with pytest.raises(PrestdUsageError):
        _ = q.page_size(0)


def test_schema_ref_requires_database():
    c = Prestd("http://mock")
    with pytest.raises(PrestdUsageError):
        _ = c.schema_ref("public")


def test_retry_on_503_sync():
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(503, json={"error": "try again"})
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    hc = httpx.Client(transport=transport)

    c = Prestd(
        "http://mock",
        database="prest",
        schema="public",
        client=hc,
        retry=RetryConfig(retries=1, backoff=0.0, retry_statuses=(503,)),
    )
    resp = c._request_json("GET", "/_health")
    assert resp == {"ok": True}


def test_timeout_exception_sync():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("boom", request=request)

    hc = httpx.Client(transport=httpx.MockTransport(handler))
    c = Prestd("http://mock", database="prest", schema="public", client=hc)

    with pytest.raises(PrestdTimeoutError):
        _ = c._request_json("GET", "/_health")


def test_request_error_sync():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("nope", request=request)

    hc = httpx.Client(transport=httpx.MockTransport(handler))
    c = Prestd("http://mock", database="prest", schema="public", client=hc)

    with pytest.raises(PrestdConnectionError):
        _ = c._request_json("GET", "/_health")


def test_decode_response_text_raises_to_cover_prestddecodeerror():
    class BadResponse:
        content = b"x"

        def json(self):
            raise ValueError("no json")

        @property
        def text(self):
            raise RuntimeError("no text")

    c = Prestd(
        "http://mock",
        database="prest",
        schema="public",
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda r: httpx.Response(200, json={"ok": True})
            )
        ),
    )
    with pytest.raises(PrestdDecodeError):
        _ = c._decode_response(BadResponse())  # type: ignore[arg-type]


def test_retry_timeout_and_request_error_async():
    async def run():
        calls = {"n": 0}

        async def handler(request: httpx.Request) -> httpx.Response:
            calls["n"] += 1
            if calls["n"] == 1:
                return httpx.Response(503, json={"error": "try again"})
            return httpx.Response(200, json={"ok": True})

        hc = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        c = AsyncPrestd(
            "http://mock",
            database="prest",
            schema="public",
            client=hc,
            retry=RetryConfig(retries=1, backoff=0.0, retry_statuses=(503,)),
        )
        ok = await c._arequest_json("GET", "/_health")
        assert ok == {"ok": True}
        await hc.aclose()

        async def handler_timeout(request: httpx.Request) -> httpx.Response:
            raise httpx.ReadTimeout("boom", request=request)

        hc2 = httpx.AsyncClient(transport=httpx.MockTransport(handler_timeout))
        c2 = AsyncPrestd("http://mock", database="prest", schema="public", client=hc2)
        with pytest.raises(PrestdTimeoutError):
            _ = await c2._arequest_json("GET", "/_health")
        await hc2.aclose()

        async def handler_err(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("nope", request=request)

        hc3 = httpx.AsyncClient(transport=httpx.MockTransport(handler_err))
        c3 = AsyncPrestd("http://mock", database="prest", schema="public", client=hc3)
        with pytest.raises(PrestdConnectionError):
            _ = await c3._arequest_json("GET", "/_health")
        await hc3.aclose()

    asyncio.run(run())
