from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

import pytest

pytestmark = pytest.mark.integration


from prestd import (
    MultipleResults,
    NoResults,
    Prestd,
    PrestdHTTPError,
    PrestdUsageError,
    UnsafeQueryError,
    enable_default_console_logging,
)


def _unique_email() -> str:
    return f"test-{uuid.uuid4().hex[:12]}@example.com"


def _extract_id(row) -> int:
    # row is usually dict-like
    return int(row["id"])


def test_basic_endpoints(client, require_integration):

    assert client.request("GET", "/_health").status_code == 200

    dbs = client.databases()
    assert dbs is not None

    schemas = client.schemas()
    assert schemas is not None

    tables = client.tables()
    assert tables is not None


def test_refs_and_table_name_parsing(client, require_integration, settings):
    # DatabaseRef + SchemaRef path
    t1 = (
        client.db(settings.database).schema(settings.schema).table(settings.users_table)
    )
    assert t1.name == settings.users_table

    # schema_ref uses client's default database
    t2 = client.schema_ref(settings.schema).table(settings.users_table)
    assert t2.schema == settings.schema

    # parse "schema.table"
    t3 = client.table(f"{settings.schema}.{settings.users_table}")
    assert t3.schema == settings.schema

    # parse "db.schema.table"
    t4 = client.table(f"{settings.database}.{settings.schema}.{settings.users_table}")
    assert t4.database == settings.database


def test_query_select_where_order_limit(client, require_integration, settings):
    users = client.table(settings.users_table)

    rows = (
        users.query()
        .select("id", "email", "active")
        .where(active=True)
        .order_by("-id")
        .limit(2)
        .get()
    )
    assert isinstance(rows, list)
    assert len(rows) <= 2
    if rows:
        assert "id" in rows[0]
        assert "email" in rows[0]


def test_where_operators_and_validation(client, require_integration, settings):
    users = client.table(settings.users_table)

    # __in operator
    rows = users.where(id__in=[1, 2]).get()
    assert isinstance(rows, list)

    # __ilike operator
    rows = users.where(email__ilike="%@example.com").get()
    assert isinstance(rows, list)
    assert any(r.get("email") == "alice@example.com" for r in rows)

    # $null operator (value ignored)
    rows = users.where(profile__null=True).get()
    assert isinstance(rows, list)
    assert any(r.get("email") == "carl@test.com" for r in rows)

    # invalid __in usage
    with pytest.raises(PrestdUsageError):
        _ = users.where(id__in=123).get()


def test_count_distinct_groupby_renderer_xml(client, require_integration, settings):
    users = client.table(settings.users_table)

    # _count returns list by default
    count_list = users.query().count("*").get()
    assert isinstance(count_list, list)

    # _count_first returns object
    count_obj = users.query().count("*", first=True).get()
    assert not isinstance(count_obj, list)

    # distinct
    roles = users.query().select("role").distinct(True).get()
    assert isinstance(roles, list)

    # group_by
    grouped = users.query().select("role").group_by("role").get()
    assert isinstance(grouped, list)

    # renderer=xml triggers non-JSON decode branch (returns text)
    xml = users.query().select("id").renderer("xml").limit(1).get()
    assert isinstance(xml, str)
    assert len(xml) > 0
    assert "<" in xml  # basic sanity for xml-ish


def test_jsonb_tsquery_and_join(client, require_integration, settings):
    users = client.table(settings.users_table)
    posts = client.table(settings.posts_table)
    friends = client.table(settings.friends_table)

    # JSONb support: ?profile->>name:jsonb=Alice
    jrows = users.query().jsonb("profile", "name", "Alice").get()
    assert isinstance(jrows, list)
    assert any(r.get("email") == "alice@example.com" for r in jrows)

    # tsquery: ?search:tsquery=python
    prow = posts.query().tsquery("search", "python").get()
    assert isinstance(prow, list)
    assert any("Python" in r.get("title", "") for r in prow)

    # tsquery with language: search$english:tsquery=python
    prow2 = posts.query().tsquery("search", "python", language="english").get()
    assert isinstance(prow2, list)

    # join: /prest/public/friends?_join=inner:users:friends.userid:$eq:users.id
    joined = (
        friends.query()
        .join("inner", "users", "friends.userid", "$eq", "users.id")
        .limit(1)
        .get()
    )
    assert isinstance(joined, list)


def test_insert_update_delete_and_safe_writes(client, require_integration, settings):
    users = client.table(settings.users_table)
    email = _unique_email()

    inserted = users.insert(
        {
            "email": email,
            "active": True,
            "role": "tester",
            "profile": {"name": "Temp"},
        }
    )
    # insert may return dict or list; we rely on querying back
    row = users.where(email=email).one()
    uid = _extract_id(row)

    # unsafe write protections
    with pytest.raises(UnsafeQueryError):
        _ = users.query().update({"role": "oops"})

    with pytest.raises(UnsafeQueryError):
        _ = users.query().delete()

    # update with filter
    _ = users.where(id=uid).update({"role": "updated"})
    row2 = users.where(id=uid).one()
    assert row2["role"] == "updated"

    # .one() errors
    with pytest.raises(NoResults):
        _ = users.where(email="does-not-exist@example.com").one()

    with pytest.raises(MultipleResults):
        _ = users.where(active=True).one()

    # delete with filter
    _ = users.where(id=uid).delete()
    assert users.where(id=uid).maybe_one() is None


def test_insert_many_tuple_and_copy_returns_empty(
    client, require_integration, settings
):
    users = client.table(settings.users_table)

    email1 = _unique_email()
    email2 = _unique_email()

    resp = users.insert_many(
        [
            {"email": email1, "active": True, "role": "batch"},
            {"email": email2, "active": False, "role": "batch"},
        ],
        method="tuple",
    )
    assert isinstance(resp, list)

    # Cleanup tuple inserts
    for e in (email1, email2):
        r = users.where(email=e).one()
        _ = users.where(id=int(r["id"])).delete()

    # COPY method returns empty response body (None) per docs
    email3 = _unique_email()
    copy_resp = users.insert_many(
        [{"email": email3, "active": True, "role": "copy"}],
        method="copy",
    )
    assert copy_resp is None

    # Cleanup: fetch inserted row via query and delete it
    r3 = users.where(email=email3).one()
    _ = users.where(id=int(r3["id"])).delete()


def test_logging_paths_execute_without_errors(require_integration, settings):
    # We just want to execute logging branches; not asserting output.
    enable_default_console_logging(level=logging.DEBUG)

    c = Prestd(
        settings.base_url,
        database=settings.database,
        schema=settings.schema,
        jwt=settings.jwt,
        enable_logs=True,
        log_level=logging.DEBUG,
        log_request_body=True,
        log_response_body=True,
        max_log_body_chars=64,
    )
    try:
        email = _unique_email()
        users = c.table(settings.users_table)
        _ = users.insert({"email": email, "active": True, "role": "log"})
        r = users.where(email=email).one()
        _ = users.where(id=int(r["id"])).delete()
    finally:
        c.close()


def test_http_error_to_cover_prestdhttperror_str(client, require_integration):
    # Request a path that should 404 on prestd itself
    with pytest.raises(PrestdHTTPError) as ei:
        _ = client.request("GET", "/__this_does_not_exist__")

    s = str(ei.value)
    assert "GET" in s
