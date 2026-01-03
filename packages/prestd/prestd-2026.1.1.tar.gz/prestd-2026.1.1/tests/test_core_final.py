from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

import httpx
import pytest

from prestd.core import (
    AsyncPrestd,
    MultipleResults,
    NoResults,
    Prestd,
    PrestdHTTPError,
    PrestdTimeoutError,
    PrestdConnectionError,
    PrestdUsageError,
    RetryConfig,
    enable_default_console_logging,
    get_logger,
    _encode_scalar,
    _merge_headers,
)


def test_enable_default_console_logging_handler_exists_branch():
    # First call adds a StreamHandler
    enable_default_console_logging(level=logging.INFO)
    # Second call should take the "handler already exists" branch
    enable_default_console_logging(level=logging.INFO)


def test_prestdhttperror_str_without_message_branch():
    e = PrestdHTTPError(status_code=400, method="GET", url="http://x", message="")
    s = str(e)
    assert "400" in s and "GET" in s


def test_encode_scalar_missing_branches():
    assert _encode_scalar(None) == ""
    assert _encode_scalar(True) == "true"
    dt = datetime(2020, 1, 1, tzinfo=timezone.utc)
    assert _encode_scalar(dt).startswith("2020-01-01")

    class BadIso:
        def isoformat(self):
            raise RuntimeError("no")

        def __str__(self):
            return "bad"

    assert _encode_scalar(BadIso()) == "bad"


def test_merge_headers_branch_a_none_b_present():
    assert _merge_headers(None, {"x": "1"}) == {"x": "1"}


def test_querybase_helpers_with_headers_unsafe_where_raw_explain_and_iter_nonempty():
    # Mock endpoint returns 2 pages: first has data, second empty
    calls = {"n": 0}

    def handler(req: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(200, json=[{"id": 1}])
        return httpx.Response(200, json=[])

    c = Prestd(
        "http://mock",
        database="prest",
        schema="public",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    q = (
        c.table("users")
        .query()
        .with_headers({"X-Test": "1"})  # covers QueryBase.with_headers
        .unsafe_writes(True)  # covers QueryBase.unsafe_writes
        .where_raw("id", "$eq.1")  # covers where_raw
    )

    ex = q.explain(method="GET")  # covers explain
    assert ex.method == "GET"
    assert "http://mock" in ex.url

    items = list(q.iter(page_size=1))  # covers non-empty iter path + exit
    assert items == [{"id": 1}]


def test_table_get_and_select_wrappers():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[{"id": 1}])

    c = Prestd(
        "http://mock",
        database="prest",
        schema="public",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    t = c.table("users")
    assert t.get() == [{"id": 1}]  # covers Table.get
    assert t.select("id").get() == [{"id": 1}]  # covers Table.select


def test_asynctable_get_select_and_insert_many_list_parse_branch():
    # Return a LIST for batch insert_many so it takes the parse_list path (line 667)
    async def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path.startswith("/batch/"):
            return httpx.Response(200, json=[{"id": 1}, {"id": 2}])
        return httpx.Response(200, json=[{"id": 1}])

    ahc = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    c = AsyncPrestd("http://mock", database="prest", schema="public", client=ahc)

    async def run():
        t = c.table("users")
        assert await t.get() == [{"id": 1}]  # AsyncTable.get
        assert await t.select("id").get() == [{"id": 1}]  # AsyncTable.select

        # method != "copy" so header branch (658->660) is taken
        r = await t.insert_many([{"a": 1}, {"a": 2}], method="tuple")
        assert r == [{"id": 1}, {"id": 2}]

        await ahc.aclose()

    asyncio.run(run())


def test_asyncquery_first_one_branches_and_iter():
    # first(): list path; one(): triggers 0 results and >1 results; iter(): yields items
    page = {"n": 0}

    async def handler(req: httpx.Request) -> httpx.Response:
        # Only apply paging behavior for the iter table
        if req.url.path.endswith("/users_iter"):
            if req.url.params.get("_page") == "1":
                return httpx.Response(200, json=[{"id": 1}])
            if req.url.params.get("_page") == "2":
                return httpx.Response(200, json=[])

        # For first/one checks, route by path (no paging interference)
        if req.url.path.endswith("/zero"):
            return httpx.Response(200, json=[])
        if req.url.path.endswith("/many"):
            return httpx.Response(200, json=[{"id": 1}, {"id": 2}])

        if req.url.path.endswith("/users_first"):
            return httpx.Response(200, json=[{"id": 9}])

        return httpx.Response(200, json=[{"id": 9}])

    ahc = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    c = AsyncPrestd("http://mock", database="prest", schema="public", client=ahc)

    async def run():
        # AsyncQuery.first (463-464)
        q_first = c.table("users_first").query()
        assert await q_first.first() == {"id": 9}

        # AsyncQuery.one: 0 results (472) and >1 results (474)
        q0 = c.table("zero").query()
        with pytest.raises(NoResults):
            await q0.one()

        qmany = c.table("many").query()
        with pytest.raises(MultipleResults):
            await qmany.one()

        # AsyncQuery.iter (505-512)
        got = []
        async for item in c.table("users_iter").query().iter(page_size=1, start_page=1):
            got.append(item)
        assert got == [{"id": 1}]

        await ahc.aclose()

    asyncio.run(run())


def test_log_response_early_returns_and_text_logging_branch():
    # We want:
    # - _log_response returns early when logs disabled
    # - _log_response returns early when logger level blocks
    # - branch where body is appended (log_response_body + DEBUG enabled + text)
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ok": True})

    logger = logging.getLogger("prestd.testlogger.levels")
    logger.handlers.clear()
    logger.propagate = False
    logger.setLevel(logging.INFO)  # blocks DEBUG

    hc = httpx.Client(transport=httpx.MockTransport(handler))

    # logs enabled False -> early return
    c1 = Prestd(
        "http://mock",
        database="prest",
        schema="public",
        client=hc,
        enable_logs=False,
        logger=logger,
    )
    c1.request("GET", "/x")

    # logs enabled True but logger INFO -> early return from debug-level log
    c2 = Prestd(
        "http://mock",
        database="prest",
        schema="public",
        client=hc,
        enable_logs=True,
        log_level=logging.INFO,
        logger=logger,
    )
    c2.request("GET", "/x")

    # logs enabled True + DEBUG + response body logging
    handler_cap = logging.StreamHandler()
    logger2 = logging.getLogger("prestd.testlogger.debugbody")
    logger2.handlers.clear()
    logger2.propagate = False
    logger2.addHandler(handler_cap)
    logger2.setLevel(logging.DEBUG)

    c3 = Prestd(
        "http://mock",
        database="prest",
        schema="public",
        client=hc,
        enable_logs=True,
        log_level=logging.DEBUG,
        log_response_body=True,
        logger=logger2,
        max_log_body_chars=64,
    )
    c3.request("GET", "/x")


def test_raise_for_status_text_and_json_exceptions_branches():
    # Force response.text to raise, response.json to raise (for _raise_for_status 822-823, 826-827)
    class R:
        status_code = 500
        headers = {}
        content = b"x"

        @property
        def text(self):
            raise RuntimeError("no text")

        def json(self):
            raise RuntimeError("no json")

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
    with pytest.raises(PrestdHTTPError):
        c._raise_for_status("GET", "http://x", R())  # type: ignore[arg-type]


def test_prestd_init_limits_branch_and_context_manager():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ok": True})

    limits = httpx.Limits(max_connections=10)
    with Prestd(
        "http://mock",
        database="prest",
        schema="public",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        limits=limits,
    ) as c:
        assert c.request("GET", "/x").status_code == 200


def test_prestd_request_timeout_requesterror_and_retry_status_branches():
    # timeout path
    def handler_timeout(req: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("boom", request=req)

    c_timeout = Prestd(
        "http://mock",
        database="prest",
        schema="public",
        client=httpx.Client(transport=httpx.MockTransport(handler_timeout)),
        retry=RetryConfig(retries=0, backoff=0.0),
    )
    with pytest.raises(PrestdTimeoutError):
        c_timeout.request("GET", "/x")

    # request error path
    def handler_err(req: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("nope", request=req)

    c_err = Prestd(
        "http://mock",
        database="prest",
        schema="public",
        client=httpx.Client(transport=httpx.MockTransport(handler_err)),
        retry=RetryConfig(retries=0, backoff=0.0),
    )
    with pytest.raises(PrestdConnectionError):
        c_err.request("GET", "/x")

    # retry-status path (925->966): first 503 then 200
    calls = {"n": 0}

    def handler_retry(req: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(503, json={"error": "retry"})
        return httpx.Response(200, json={"ok": True})

    c_retry = Prestd(
        "http://mock",
        database="prest",
        schema="public",
        client=httpx.Client(transport=httpx.MockTransport(handler_retry)),
        retry=RetryConfig(retries=1, backoff=0.0, retry_statuses=(503,)),
    )
    assert c_retry.request("GET", "/x").status_code == 200


def test_prestd_table_missing_db_and_schema_branches():
    c = Prestd("http://mock")  # no db/schema
    with pytest.raises(PrestdUsageError):
        _ = c.table("users")  # missing db

    c2 = Prestd("http://mock", database="prest")  # missing schema
    with pytest.raises(PrestdUsageError):
        _ = c2.table("users")


def test_prestd_show_and_list_schema_tables_wrappers():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ok": True})

    c = Prestd(
        "http://mock",
        database="prest",
        schema="public",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    assert c.show("prest", "public", "users") == {"ok": True}
    assert c.list_schema_tables("prest", "public") == {"ok": True}


def test_asyncprestd_limits_branch_request_error_timeout_retry_and_wrappers():
    async def handler(req: httpx.Request) -> httpx.Response:
        # wrappers
        if req.url.path in ("/_health", "/databases", "/schemas", "/tables"):
            return httpx.Response(200, json={"ok": True})
        if req.url.path.startswith("/show/"):
            return httpx.Response(200, json={"ok": True})
        return httpx.Response(200, json={"ok": True})

    limits = httpx.Limits(max_connections=10)
    ahc = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    c = AsyncPrestd(
        "http://mock", database="prest", schema="public", client=ahc, limits=limits
    )

    async def run():
        assert await c.health() in (None, {"ok": True})
        assert await c.databases() == {"ok": True}
        assert await c.schemas() == {"ok": True}
        assert await c.tables() == {"ok": True}
        assert await c.show("prest", "public", "users") == {"ok": True}
        assert await c.list_schema_tables("prest", "public") == {"ok": True}
        await ahc.aclose()

    asyncio.run(run())

    # timeout branch
    async def handler_timeout(req: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("boom", request=req)

    ahc2 = httpx.AsyncClient(transport=httpx.MockTransport(handler_timeout))
    c_timeout = AsyncPrestd(
        "http://mock",
        database="prest",
        schema="public",
        client=ahc2,
        retry=RetryConfig(retries=0, backoff=0.0),
    )

    async def run_timeout():
        with pytest.raises(PrestdTimeoutError):
            await c_timeout.request("GET", "/x")
        await ahc2.aclose()

    asyncio.run(run_timeout())

    # request error branch
    async def handler_err(req: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("nope", request=req)

    ahc3 = httpx.AsyncClient(transport=httpx.MockTransport(handler_err))
    c_err = AsyncPrestd(
        "http://mock",
        database="prest",
        schema="public",
        client=ahc3,
        retry=RetryConfig(retries=0, backoff=0.0),
    )

    async def run_err():
        with pytest.raises(PrestdConnectionError):
            await c_err.request("GET", "/x")
        await ahc3.aclose()

    asyncio.run(run_err())

    # retry-status branch (1124->1165): first 503 then 200
    calls = {"n": 0}

    async def handler_retry(req: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(503, json={"error": "retry"})
        return httpx.Response(200, json={"ok": True})

    ahc4 = httpx.AsyncClient(transport=httpx.MockTransport(handler_retry))
    c_retry = AsyncPrestd(
        "http://mock",
        database="prest",
        schema="public",
        client=ahc4,
        retry=RetryConfig(retries=1, backoff=0.0, retry_statuses=(503,)),
    )

    async def run_retry():
        r = await c_retry.request("GET", "/x")
        assert r.status_code == 200
        await ahc4.aclose()

    asyncio.run(run_retry())


def test_asyncprestd_table_missing_db_schema_and_parse_name_branches():
    ac = AsyncPrestd("http://mock")  # no db/schema
    with pytest.raises(PrestdUsageError):
        _ = ac.table("users")

    ac2 = AsyncPrestd("http://mock", database="prest")  # missing schema
    with pytest.raises(PrestdUsageError):
        _ = ac2.table("users")

    # name parsing branches: schema.table and db.schema.table
    ac3 = AsyncPrestd("http://mock", database="prest", schema="public")
    t = ac3.table("public.users")
    assert t.schema == "public"
    t2 = ac3.table("prest.public.users")
    assert t2.database == "prest"
