from __future__ import annotations

import logging
import time
from typing import Any

import httpx
import pytest

from prestd.core import (
    AsyncPrestd,
    LogConfig,
    Prestd,
    PrestdHTTPError,
    RetryConfig,
    get_logger,
)


class _CapturingHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def _make_sync_client(
    transport: httpx.BaseTransport, *, enable_logs: bool, level: int
) -> Prestd:
    # Inject a logger we control
    logger = logging.getLogger("prestd.testlogger.sync")
    logger.handlers.clear()
    logger.propagate = False
    handler = _CapturingHandler()
    logger.addHandler(handler)
    logger.setLevel(level)

    hc = httpx.Client(transport=transport)
    c = Prestd(
        "http://mock",
        database="prest",
        schema="public",
        client=hc,
        enable_logs=enable_logs,
        log_level=level,
        log_request_body=True,
        log_response_body=True,
        max_log_body_chars=8,
        retry=RetryConfig(retries=0),
        logger=logger,
    )
    return c


def test_raise_for_status_includes_request_id_and_json_text():
    # Force error with request id header, JSON body, and text
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            418,
            json={"error": "teapot"},
            headers={"X-Request-Id": "req-123"},
        )

    c = _make_sync_client(
        httpx.MockTransport(handler), enable_logs=False, level=logging.INFO
    )
    with pytest.raises(PrestdHTTPError) as ei:
        c.request("GET", "/x")

    err = ei.value
    assert err.status_code == 418
    assert err.request_id == "req-123"
    assert isinstance(err.response_json, dict)
    assert "GET" in str(err)


def test_logging_branches_request_and_response_levels():
    # 200 then 500 to hit DEBUG vs WARNING response log levels
    calls = {"n": 0}

    def handler(req: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(200, json={"ok": True})
        return httpx.Response(500, json={"error": "boom"})

    # enable logs + DEBUG => should log request+response
    c = _make_sync_client(
        httpx.MockTransport(handler), enable_logs=True, level=logging.DEBUG
    )
    logger = c._logger  # type: ignore[attr-defined]
    handler_obj = next(h for h in logger.handlers if isinstance(h, _CapturingHandler))

    _ = c.request("GET", "/ok", params={"a": "1"}, json={"x": "y"})
    with pytest.raises(PrestdHTTPError):
        _ = c.request("GET", "/fail")

    # Ensure we emitted both DEBUG and WARNING records
    levels = {r.levelno for r in handler_obj.records}
    assert logging.DEBUG in levels
    assert logging.WARNING in levels

    # Now disable logs => should not emit anything new
    def handler2(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ok": True})

    c2 = _make_sync_client(
        httpx.MockTransport(handler2), enable_logs=False, level=logging.DEBUG
    )
    logger2 = c2._logger  # type: ignore[attr-defined]
    handler_obj2 = next(h for h in logger2.handlers if isinstance(h, _CapturingHandler))
    _ = c2.request("GET", "/ok2")
    assert handler_obj2.records == []


def test_decode_response_json_and_text_paths():
    # json success
    def handler_json(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"a": 1})

    c = _make_sync_client(
        httpx.MockTransport(handler_json), enable_logs=False, level=logging.INFO
    )
    r = c.request("GET", "/j")
    assert c._decode_response(r) == {"a": 1}  # type: ignore[attr-defined]

    # non-json -> text path
    def handler_text(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, content=b"<xml/>", headers={"Content-Type": "text/xml"}
        )

    c2 = _make_sync_client(
        httpx.MockTransport(handler_text), enable_logs=False, level=logging.INFO
    )
    r2 = c2.request("GET", "/t")
    out = c2._decode_response(r2)  # type: ignore[attr-defined]
    assert isinstance(out, str)
    assert "<xml" in out

    # empty body -> None path
    def handler_empty(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"")

    c3 = _make_sync_client(
        httpx.MockTransport(handler_empty), enable_logs=False, level=logging.INFO
    )
    r3 = c3.request("GET", "/e")
    assert c3._decode_response(r3) is None  # type: ignore[attr-defined]


def test_build_url_strips_slashes():
    # Ensure base_url + path normalization
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ok": True})

    hc = httpx.Client(transport=httpx.MockTransport(handler))
    c = Prestd("http://mock/", database="prest", schema="public", client=hc)
    # internal helper should normalize correctly
    assert c._build_url("/x") == "http://mock/x"  # type: ignore[attr-defined]
    assert c._build_url("x") == "http://mock/x"  # type: ignore[attr-defined]


def test_retry_status_no_retry_when_attempts_exhausted():
    # retries=0 => should return the 503 and raise without retrying
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"error": "nope"})

    transport = httpx.MockTransport(handler)
    hc = httpx.Client(transport=transport)

    c = Prestd(
        "http://mock",
        database="prest",
        schema="public",
        client=hc,
        retry=RetryConfig(retries=0, backoff=0.0, retry_statuses=(503,)),
    )
    with pytest.raises(PrestdHTTPError) as ei:
        c.request("GET", "/x")
    assert ei.value.status_code == 503


def test_async_client_close_paths(settings):
    # Exercise __aenter__/__aexit__ and aclose branches quickly using MockTransport.
    async def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ok": True})

    hc = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    c = AsyncPrestd(
        "http://mock",
        database="prest",
        schema="public",
        client=hc,
        retry=RetryConfig(retries=0),
    )

    async def run():
        async with c as cc:
            r = await cc.request("GET", "/x")
