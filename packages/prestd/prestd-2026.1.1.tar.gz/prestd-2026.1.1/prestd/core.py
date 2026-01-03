from __future__ import annotations

import asyncio
import logging
import json
import time
from dataclasses import asdict, dataclass, is_dataclass, replace
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterator,
    Mapping,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    TypeVar,
    Union,
)
from urllib.parse import quote

import httpx


# -------------------------
# Logging (library-friendly)
# -------------------------

LOGGER_NAME = "prestd"
_logger = logging.getLogger(LOGGER_NAME)
_logger.addHandler(logging.NullHandler())


@dataclass(frozen=True, slots=True)
class LogConfig:
    enabled: bool = False
    level: int = logging.INFO
    log_request_body: bool = False
    log_response_body: bool = False
    max_body_chars: int = 2048


def get_logger() -> logging.Logger:
    return logging.getLogger(LOGGER_NAME)


def enable_default_console_logging(level: int = logging.INFO) -> None:
    """Optional helper to quickly see prestd logs in scripts."""
    logger = get_logger()
    logger.setLevel(level)
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        h = logging.StreamHandler()
        h.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
        )
        logger.addHandler(h)


def _truncate(s: str, max_chars: int) -> str:
    if max_chars <= 0:
        return ""
    return s if len(s) <= max_chars else s[: max_chars - 1] + "…"


# -------------------------
# Errors
# -------------------------


class PrestdError(Exception):
    """Base exception for the prestd SDK."""


class PrestdUsageError(PrestdError):
    """Raised when the SDK is used incorrectly."""


class UnsafeQueryError(PrestdUsageError):
    """Raised for UPDATE/DELETE without filters when safe_writes is enabled."""


class NoResults(PrestdError):
    """Raised when .one() expects a result but got none."""


class MultipleResults(PrestdError):
    """Raised when .one() expects one result but got multiple."""


class PrestdDecodeError(PrestdError):
    """Raised when the response could not be decoded."""


class PrestdTimeoutError(PrestdError):
    """Raised when the request times out."""


class PrestdConnectionError(PrestdError):
    """Raised for network/transport errors."""


@dataclass(slots=True)
class PrestdHTTPError(PrestdError):
    status_code: int
    method: str
    url: str
    message: str = ""
    response_text: Optional[str] = None
    response_json: Optional[Any] = None
    request_id: Optional[str] = None

    def __str__(self) -> str:
        bits = [f"{self.status_code} {self.method} {self.url}"]
        if self.message:
            bits.append(self.message)
        if self.request_id:
            bits.append(f"request_id={self.request_id}")
        return " | ".join(bits)


# -------------------------
# Optional payload / parsing hooks (no pydantic here)
# -------------------------


class Encoder(Protocol):
    def __call__(self, obj: Any) -> Any: ...


class ParseOne(Protocol):
    def __call__(self, obj: Any) -> Any: ...


class ParseList(Protocol):
    def __call__(self, obj: Any) -> Any: ...


def _coerce_nested_json_values(obj: Any) -> Any:
    """
    pRESTd/go-sql cannot bind nested dict/list values directly (it becomes a map).
    For JSONB-friendly DX, we JSON-encode nested dict/list values *inside* payload dicts.
    """
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                out[k] = json.dumps(v, separators=(",", ":"), ensure_ascii=False)
            else:
                out[k] = v
        return out
    if isinstance(obj, list):
        return [_coerce_nested_json_values(x) for x in obj]
    return obj


def default_encode(obj: Any) -> Any:
    if is_dataclass(obj):
        obj = asdict(obj)
    return _coerce_nested_json_values(obj)


def identity_parse_one(obj: Any) -> Any:
    return obj


def identity_parse_list(obj: Any) -> Any:
    return obj


# -------------------------
# Query builder
# -------------------------

T = TypeVar("T")


def _encode_bool(v: bool) -> str:
    return "true" if v else "false"


def _encode_scalar(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return _encode_bool(v)
    if hasattr(v, "isoformat") and callable(getattr(v, "isoformat")):
        try:
            return v.isoformat()
        except Exception:
            pass
    return str(v)


def _join_csv(values: Sequence[Any]) -> str:
    return ",".join(_encode_scalar(x) for x in values)


_OPERATOR_MAP = {
    "eq": "$eq",
    "ne": "$ne",
    "gt": "$gt",
    "gte": "$gte",
    "lt": "$lt",
    "lte": "$lte",
    "in": "$in",
    "nin": "$nin",
    "null": "$null",
    "notnull": "$notnull",
    "true": "$true",
    "nottrue": "$nottrue",
    "false": "$false",
    "notfalse": "$notfalse",
    "like": "$like",
    "ilike": "$ilike",
    "nlike": "$nlike",
    "nilike": "$nilike",
    "ltreelanc": "$ltreelanc",
    "ltreerdesc": "$ltreerdesc",
    "ltreematch": "$ltreematch",
    "ltreematchtxt": "$ltreematchtxt",
}


def _build_filter_value(op: str, value: Any) -> str:
    op_token = _OPERATOR_MAP.get(op, op)
    if op_token in ("$null", "$notnull", "$true", "$nottrue", "$false", "$notfalse"):
        return op_token
    if op_token in ("$in", "$nin"):
        if not isinstance(value, (list, tuple, set, frozenset)):
            raise PrestdUsageError(f"Operator '{op}' expects a sequence")
        return f"{op_token}.{_join_csv(list(value))}"
    return f"{op_token}.{_encode_scalar(value)}"


def _parse_where_kwargs(kwargs: Mapping[str, Any]) -> Tuple[Tuple[str, str], ...]:
    out: list[tuple[str, str]] = []
    for key, value in kwargs.items():
        if "__" in key:
            field, op = key.split("__", 1)
            out.append((field, _build_filter_value(op, value)))
        else:
            out.append((key, _encode_scalar(value)))
    return tuple(out)


@dataclass(frozen=True, slots=True)
class Explain:
    method: str
    url: str
    params: list[tuple[str, str]]
    headers: dict[str, str]
    json: Any = None


@dataclass(frozen=True, slots=True)
class _QueryState(Generic[T]):
    client: Any
    path: str
    params: Tuple[Tuple[str, str], ...] = ()
    headers: Tuple[Tuple[str, str], ...] = ()
    safe_writes: bool = True

    # Optional hooks
    encode: Encoder = default_encode
    parse_one: ParseOne = identity_parse_one
    parse_list: ParseList = identity_parse_list


QSelf = TypeVar("QSelf", bound="QueryBase[Any]")


class QueryBase(Generic[T]):
    __slots__ = ("_s",)

    def __init__(self, state: _QueryState[T]):
        self._s = state

    # ---- modifiers ----
    def with_headers(self: QSelf, headers: Mapping[str, str]) -> QSelf:
        merged = dict(self._s.headers)
        merged.update(headers)
        return self.__class__(replace(self._s, headers=tuple(merged.items())))  # type: ignore[return-value]

    def unsafe_writes(self: QSelf, enabled: bool = True) -> QSelf:
        return self.__class__(replace(self._s, safe_writes=not enabled))  # type: ignore[return-value]

    def param(self: QSelf, key: str, value: Any) -> QSelf:
        return self.__class__(
            replace(self._s, params=self._s.params + ((key, _encode_scalar(value)),))
        )  # type: ignore[return-value]

    def select(self: QSelf, *fields: str) -> QSelf:
        return self if not fields else self.param("_select", ",".join(fields))

    def count(self: QSelf, field: str = "*", *, first: bool = False) -> QSelf:
        q = self.param("_count", field)
        return q.param("_count_first", "true") if first else q

    def distinct(self: QSelf, enabled: bool = True) -> QSelf:
        return self.param("_distinct", _encode_bool(enabled))

    def renderer(self: QSelf, renderer: str) -> QSelf:
        return self.param("_renderer", renderer)

    def order_by(self: QSelf, *fields: str) -> QSelf:
        return self if not fields else self.param("_order", ",".join(fields))

    def group_by(self: QSelf, *fields: str) -> QSelf:
        return self if not fields else self.param("_groupby", ",".join(fields))

    def join(
        self: QSelf,
        join_type: str,
        table_join: str,
        left: str,
        operator: str,
        right: str,
    ) -> QSelf:
        return self.param(
            "_join", f"{join_type}:{table_join}:{left}:{operator}:{right}"
        )

    def page(self: QSelf, page: int) -> QSelf:
        if page <= 0:
            raise PrestdUsageError("page must be >= 1")
        return self.param("_page", page)

    def page_size(self: QSelf, size: int) -> QSelf:
        if size <= 0:
            raise PrestdUsageError("page_size must be >= 1")
        return self.param("_page_size", size)

    def limit(self: QSelf, n: int) -> QSelf:
        return self.page(1).page_size(n)

    def where(self: QSelf, **kwargs: Any) -> QSelf:
        return self.__class__(
            replace(self._s, params=self._s.params + _parse_where_kwargs(kwargs))
        )  # type: ignore[return-value]

    def where_raw(self: QSelf, field: str, value: str) -> QSelf:
        return self.__class__(
            replace(self._s, params=self._s.params + ((field, value),))
        )  # type: ignore[return-value]

    def jsonb(self: QSelf, field: str, json_key: str, value: Any) -> QSelf:
        return self.param(f"{field}->>{json_key}:jsonb", _encode_scalar(value))

    def tsquery(
        self: QSelf, field: str, query: str, *, language: Optional[str] = None
    ) -> QSelf:
        k = f"{field}${language}:tsquery" if language else f"{field}:tsquery"
        return self.param(k, query)

    # ---- explain ----
    def explain(self, *, method: str = "GET", json: Any = None) -> Explain:
        url = self._s.client._build_url(self._s.path)  # type: ignore[attr-defined]
        return Explain(
            method=method.upper(),
            url=str(url),
            params=list(self._s.params),
            headers=dict(self._s.headers),
            json=json,
        )

    # ---- helpers ----
    def _has_filter(self) -> bool:
        return any(not k.startswith("_") for k, _ in self._s.params)

    def _ensure_safe_write(self) -> None:
        if self._s.safe_writes and not self._has_filter():
            raise UnsafeQueryError(
                "Refusing to execute UPDATE/DELETE without filters. "
                "Add .where(...) or call .unsafe_writes(True) to override."
            )

    def _parse_response(self, data: Any) -> Any:
        if isinstance(data, list):
            return self._s.parse_list(data)
        return self._s.parse_one(data)


class Query(QueryBase[T]):
    __slots__ = ()

    def get(self) -> Any:
        data = self._s.client._request_json(
            "GET",
            self._s.path,
            params=list(self._s.params),
            headers=dict(self._s.headers),
        )  # type: ignore[attr-defined]
        return self._parse_response(data)

    def iter(self, *, page_size: int = 1000, start_page: int = 1) -> Iterator[Any]:
        page = start_page
        while True:
            batch = self.page(page).page_size(page_size).get()
            if not batch:
                return
            for item in batch:
                yield item
            page += 1

    def first(self) -> Optional[Any]:
        data = self.limit(1).get()
        return (data[0] if data else None) if isinstance(data, list) else data

    def one(self) -> Any:
        data = self.limit(2).get()
        if isinstance(data, list):
            if len(data) == 0:
                raise NoResults("Expected exactly one result, got none.")
            if len(data) > 1:
                raise MultipleResults(f"Expected exactly one result, got {len(data)}.")
            return data[0]
        return data

    def maybe_one(self) -> Optional[Any]:
        try:
            return self.one()
        except NoResults:
            return None

    def update(self, data: Any, *, method: str = "PATCH") -> Any:
        self._ensure_safe_write()
        payload = self._s.encode(data)
        resp = self._s.client._request_json(
            method.upper(),
            self._s.path,
            params=list(self._s.params),
            json=payload,
            headers=dict(self._s.headers),
        )  # type: ignore[attr-defined]
        return resp

    def delete(self) -> Any:
        self._ensure_safe_write()
        resp = self._s.client._request_json(
            "DELETE",
            self._s.path,
            params=list(self._s.params),
            headers=dict(self._s.headers),
        )  # type: ignore[attr-defined]
        return resp


class AsyncQuery(QueryBase[T]):
    __slots__ = ()

    async def get(self) -> Any:
        data = await self._s.client._arequest_json(
            "GET",
            self._s.path,
            params=list(self._s.params),
            headers=dict(self._s.headers),
        )  # type: ignore[attr-defined]
        return self._parse_response(data)

    async def first(self) -> Optional[Any]:
        data = await self.limit(1).get()
        return (data[0] if data else None) if isinstance(data, list) else data

    async def one(self) -> Any:
        data = await self.limit(2).get()
        if isinstance(data, list):
            if len(data) == 0:
                raise NoResults("Expected exactly one result, got none.")
            if len(data) > 1:
                raise MultipleResults(f"Expected exactly one result, got {len(data)}.")
            return data[0]
        return data

    async def maybe_one(self) -> Optional[Any]:
        try:
            return await self.one()
        except NoResults:
            return None

    async def update(self, data: Any, *, method: str = "PATCH") -> Any:
        self._ensure_safe_write()
        payload = self._s.encode(data)
        resp = await self._s.client._arequest_json(
            method.upper(),
            self._s.path,
            params=list(self._s.params),
            json=payload,
            headers=dict(self._s.headers),
        )  # type: ignore[attr-defined]
        return resp

    async def delete(self) -> Any:
        self._ensure_safe_write()
        resp = await self._s.client._arequest_json(
            "DELETE",
            self._s.path,
            params=list(self._s.params),
            headers=dict(self._s.headers),
        )  # type: ignore[attr-defined]
        return resp

    async def iter(self, *, page_size: int = 1000, start_page: int = 1):
        page = start_page
        while True:
            batch = await self.page(page).page_size(page_size).get()
            if not batch:
                return
            for item in batch:
                yield item
            page += 1


# -------------------------
# Table objects (pydantic-free)
# -------------------------


@dataclass(frozen=True, slots=True)
class Table(Generic[T]):
    client: Any
    database: str
    schema: str
    name: str
    safe_writes: bool = True

    # optional hooks
    encode: Encoder = default_encode
    parse_one: ParseOne = identity_parse_one
    parse_list: ParseList = identity_parse_list

    def with_codec(
        self,
        *,
        encode: Optional[Encoder] = None,
        parse_one: Optional[ParseOne] = None,
        parse_list: Optional[ParseList] = None,
    ) -> "Table[Any]":
        return replace(
            self,
            encode=encode or self.encode,
            parse_one=parse_one or self.parse_one,
            parse_list=parse_list or self.parse_list,
        )

    def _path(self) -> str:
        db = quote(self.database, safe="")
        sc = quote(self.schema, safe="")
        tb = quote(self.name, safe="")
        return f"/{db}/{sc}/{tb}"

    def query(self) -> Query[T]:
        return Query(
            _QueryState(
                client=self.client,
                path=self._path(),
                safe_writes=self.safe_writes,
                encode=self.encode,
                parse_one=self.parse_one,
                parse_list=self.parse_list,
            )
        )

    def get(self) -> Any:
        return self.query().get()

    def select(self, *fields: str) -> Query[T]:
        return self.query().select(*fields)

    def where(self, **kwargs: Any) -> Query[T]:
        return self.query().where(**kwargs)

    def insert(self, data: Any) -> Any:
        payload = self.encode(data)
        resp = self.client._request_json("POST", self._path(), json=payload)  # type: ignore[attr-defined]
        return self.parse_list(resp) if isinstance(resp, list) else self.parse_one(resp)

    def insert_many(self, rows: Sequence[Any], *, method: str = "tuple") -> Any:
        payload = [self.encode(r) for r in rows]
        headers: dict[str, str] = {}
        if method.lower() == "copy":
            headers["Prest-Batch-Method"] = "copy"
        resp = self.client._request_json(
            "POST",
            f"/batch{self._path()}",
            json=payload,
            headers=headers,
        )  # type: ignore[attr-defined]
        # copy method may return empty; parse only if list-like
        if isinstance(resp, list):
            return self.parse_list(resp)
        return resp


@dataclass(frozen=True, slots=True)
class AsyncTable(Generic[T]):
    client: Any
    database: str
    schema: str
    name: str
    safe_writes: bool = True

    # optional hooks
    encode: Encoder = default_encode
    parse_one: ParseOne = identity_parse_one
    parse_list: ParseList = identity_parse_list

    def with_codec(
        self,
        *,
        encode: Optional[Encoder] = None,
        parse_one: Optional[ParseOne] = None,
        parse_list: Optional[ParseList] = None,
    ) -> "AsyncTable[Any]":
        return replace(
            self,
            encode=encode or self.encode,
            parse_one=parse_one or self.parse_one,
            parse_list=parse_list or self.parse_list,
        )

    def _path(self) -> str:
        db = quote(self.database, safe="")
        sc = quote(self.schema, safe="")
        tb = quote(self.name, safe="")
        return f"/{db}/{sc}/{tb}"

    def query(self) -> AsyncQuery[T]:
        return AsyncQuery(
            _QueryState(
                client=self.client,
                path=self._path(),
                safe_writes=self.safe_writes,
                encode=self.encode,
                parse_one=self.parse_one,
                parse_list=self.parse_list,
            )
        )

    async def get(self) -> Any:
        return await self.query().get()

    def select(self, *fields: str) -> AsyncQuery[T]:
        return self.query().select(*fields)

    def where(self, **kwargs: Any) -> AsyncQuery[T]:
        return self.query().where(**kwargs)

    async def insert(self, data: Any) -> Any:
        payload = self.encode(data)
        resp = await self.client._arequest_json("POST", self._path(), json=payload)  # type: ignore[attr-defined]
        return self.parse_list(resp) if isinstance(resp, list) else self.parse_one(resp)

    async def insert_many(self, rows: Sequence[Any], *, method: str = "tuple") -> Any:
        payload = [self.encode(r) for r in rows]
        headers: dict[str, str] = {}
        if method.lower() == "copy":
            headers["Prest-Batch-Method"] = "copy"
        resp = await self.client._arequest_json(
            "POST",
            f"/batch{self._path()}",
            json=payload,
            headers=headers,
        )  # type: ignore[attr-defined]
        if isinstance(resp, list):
            return self.parse_list(resp)
        return resp


# -------------------------
# Client(s)
# -------------------------


def _merge_headers(
    a: Optional[Mapping[str, str]], b: Optional[Mapping[str, str]]
) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if a:
        out.update(a)
    if b:
        out.update(b)
    return out


@dataclass(frozen=True, slots=True)
class RetryConfig:
    retries: int = 0
    backoff: float = 0.2
    retry_statuses: Tuple[int, ...] = (502, 503, 504)


@dataclass(frozen=True, slots=True)
class DatabaseRef:
    client: Any
    name: str

    def schema(self, name: str) -> "SchemaRef":
        return SchemaRef(client=self.client, database=self.name, name=name)


@dataclass(frozen=True, slots=True)
class SchemaRef:
    client: Any
    database: str
    name: str

    def table(self, name: str, *, safe_writes: bool = True) -> Table[Any]:
        return self.client.table(
            name, database=self.database, schema=self.name, safe_writes=safe_writes
        )


class _BaseClient:
    def __init__(
        self,
        base_url: str,
        *,
        database: Optional[str],
        schema: Optional[str],
        jwt: Optional[str],
        headers: Optional[Mapping[str, str]],
        timeout: Union[float, httpx.Timeout, None],
        verify: Union[bool, str],
        follow_redirects: bool,
        limits: Optional[httpx.Limits],
        enable_logs: bool,
        log_level: int,
        log_request_body: bool,
        log_response_body: bool,
        max_log_body_chars: int,
        retry: Optional[RetryConfig],
        logger: Optional[logging.Logger],
    ):
        self._base_url = base_url.rstrip("/")
        self.database = database
        self.schema = schema

        self._logger = logger or get_logger()
        self._log = LogConfig(
            enabled=enable_logs,
            level=log_level,
            log_request_body=log_request_body,
            log_response_body=log_response_body,
            max_body_chars=max_log_body_chars,
        )
        if enable_logs:
            self._logger.setLevel(log_level)

        self._retry = retry or RetryConfig()

        base_headers: Dict[str, str] = {"Accept": "application/json"}
        if jwt:
            base_headers["Authorization"] = f"Bearer {jwt}"
        self._base_headers = _merge_headers(base_headers, headers)

        self._timeout = timeout
        self._verify = verify
        self._follow_redirects = follow_redirects
        self._limits = limits

    def db(self, name: str) -> DatabaseRef:
        return DatabaseRef(client=self, name=name)

    def schema_ref(self, name: str, *, database: Optional[str] = None) -> SchemaRef:
        db = database or self.database
        if not db:
            raise PrestdUsageError(
                "No database provided. Set client.database or pass database=..."
            )
        return SchemaRef(client=self, database=db, name=name)

    def _build_url(self, path: str) -> str:
        return f"{self._base_url}/{path.lstrip('/')}"

    def _log_request(
        self, method: str, url: str, *, params: Any, json_body: Any
    ) -> None:
        if not self._log.enabled or not self._logger.isEnabledFor(logging.DEBUG):
            return
        msg = f"HTTP {method} {url}"
        if params:
            msg += f" params={params}"
        if self._log.log_request_body and json_body is not None:
            msg += f" json={_truncate(str(json_body), self._log.max_body_chars)}"
        self._logger.debug(msg)

    def _log_response(
        self,
        method: str,
        url: str,
        status: int,
        elapsed_s: float,
        *,
        text: Optional[str],
    ) -> None:
        if not self._log.enabled:
            return
        level = logging.DEBUG if status < 400 else logging.WARNING
        if not self._logger.isEnabledFor(level):
            return
        msg = f"HTTP {method} {url} -> {status} ({elapsed_s*1000:.1f}ms)"
        if (
            self._log.log_response_body
            and text
            and self._logger.isEnabledFor(logging.DEBUG)
        ):
            msg += f" body={_truncate(text, self._log.max_body_chars)}"
        self._logger.log(level, msg)

    def _raise_for_status(
        self, method: str, url: str, response: httpx.Response
    ) -> None:
        if 200 <= response.status_code < 300:
            return
        req_id = response.headers.get("X-Request-Id") or response.headers.get(
            "X-Request-ID"
        )
        try:
            text = response.text
        except Exception:
            text = None
        try:
            js = response.json()
        except Exception:
            js = None
        raise PrestdHTTPError(
            response.status_code, method, url, "Request failed", text, js, req_id
        )

    def _decode_response(self, response: httpx.Response) -> Any:
        if not response.content:
            return None
        try:
            return response.json()
        except Exception:
            try:
                return response.text
            except Exception as e:
                raise PrestdDecodeError("Failed to decode response") from e


class Prestd(_BaseClient):
    """Synchronous client."""

    def __init__(
        self,
        base_url: str,
        *,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        jwt: Optional[str] = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Union[float, httpx.Timeout, None] = 30.0,
        verify: Union[bool, str] = True,
        follow_redirects: bool = True,
        limits: Optional[httpx.Limits] = None,
        enable_logs: bool = False,
        log_level: int = logging.INFO,
        log_request_body: bool = False,
        log_response_body: bool = False,
        max_log_body_chars: int = 2048,
        retry: Optional[RetryConfig] = None,
        logger: Optional[logging.Logger] = None,
        client: Optional[httpx.Client] = None,
    ):
        super().__init__(
            base_url,
            database=database,
            schema=schema,
            jwt=jwt,
            headers=headers,
            timeout=timeout,
            verify=verify,
            follow_redirects=follow_redirects,
            limits=limits,
            enable_logs=enable_logs,
            log_level=log_level,
            log_request_body=log_request_body,
            log_response_body=log_response_body,
            max_log_body_chars=max_log_body_chars,
            retry=retry,
            logger=logger,
        )
        self._owns_client = client is None
        if client is not None:
            self._client = client
        else:
            kwargs: Dict[str, Any] = {
                "timeout": timeout,
                "headers": self._base_headers,
                "verify": verify,
                "follow_redirects": follow_redirects,
            }
            if limits is not None:
                kwargs["limits"] = limits
            self._client = httpx.Client(**kwargs)

    def __enter__(self) -> "Prestd":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Any = None,
        json: Any = None,
        headers: Optional[Mapping[str, str]] = None,
        auth: Optional[httpx.Auth] = None,
    ) -> httpx.Response:
        url = self._build_url(path)
        all_headers = _merge_headers(self._base_headers, headers)
        self._log_request(method.upper(), url, params=params, json_body=json)

        attempts = self._retry.retries + 1
        for attempt in range(attempts):
            t0 = time.perf_counter()
            try:
                resp = self._client.request(
                    method.upper(),
                    url,
                    params=params,
                    json=json,
                    headers=all_headers,
                    auth=auth,
                )
            except httpx.TimeoutException as e:
                if attempt < attempts - 1:
                    time.sleep(self._retry.backoff * (2**attempt))
                    continue
                raise PrestdTimeoutError(str(e)) from e
            except httpx.RequestError as e:
                if attempt < attempts - 1:
                    time.sleep(self._retry.backoff * (2**attempt))
                    continue
                raise PrestdConnectionError(str(e)) from e

            elapsed = time.perf_counter() - t0
            self._log_response(
                method.upper(),
                url,
                resp.status_code,
                elapsed,
                text=resp.text if self._log.log_response_body else None,
            )

            if (
                resp.status_code in self._retry.retry_statuses
                and attempt < attempts - 1
            ):
                time.sleep(self._retry.backoff * (2**attempt))
                continue

            self._raise_for_status(method.upper(), url, resp)
            return resp

        raise PrestdConnectionError("Request failed")

    def _request_json(
        self,
        method: str,
        path: str,
        *,
        params: Any = None,
        json: Any = None,
        headers: Optional[Mapping[str, str]] = None,
        auth: Optional[httpx.Auth] = None,
    ) -> Any:
        return self._decode_response(
            self.request(
                method, path, params=params, json=json, headers=headers, auth=auth
            )
        )

    # --- resources ---
    def table(
        self,
        name: str,
        *,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        safe_writes: bool = True,
    ) -> Table[Any]:
        db = database or self.database
        sc = schema or self.schema
        parts = name.split(".")
        if len(parts) == 2:
            sc, name = parts
        elif len(parts) == 3:
            db, sc, name = parts
        if not db:
            raise PrestdUsageError(
                "No database provided. Set client.database or pass database=..."
            )
        if not sc:
            raise PrestdUsageError(
                "No schema provided. Set client.schema or pass schema=..."
            )
        return Table(
            client=self, database=db, schema=sc, name=name, safe_writes=safe_writes
        )

    # --- common endpoints ---
    def health(self) -> Any:
        return self._request_json("GET", "/_health")

    def databases(self) -> Any:
        return self._request_json("GET", "/databases")

    def schemas(self) -> Any:
        return self._request_json("GET", "/schemas")

    def tables(self) -> Any:
        return self._request_json("GET", "/tables")

    def show(self, database: str, schema: str, table: str) -> Any:
        return self._request_json("GET", f"/show/{database}/{schema}/{table}")

    def list_schema_tables(self, database: str, schema: str) -> Any:
        return self._request_json("GET", f"/{database}/{schema}")

    # --- auth helpers ---
    def auth_bearer(self, username: str, password: str) -> Any:
        return self._request_json(
            "POST", "/auth", json={"username": username, "password": password}
        )

    def auth_basic(self, username: str, password: str) -> Any:
        return self._request_json(
            "POST", "/auth", auth=httpx.BasicAuth(username, password)
        )


class AsyncPrestd(_BaseClient):
    """Asynchronous client."""

    def __init__(
        self,
        base_url: str,
        *,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        jwt: Optional[str] = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Union[float, httpx.Timeout, None] = 30.0,
        verify: Union[bool, str] = True,
        follow_redirects: bool = True,
        limits: Optional[httpx.Limits] = None,
        enable_logs: bool = False,
        log_level: int = logging.INFO,
        log_request_body: bool = False,
        log_response_body: bool = False,
        max_log_body_chars: int = 2048,
        retry: Optional[RetryConfig] = None,
        logger: Optional[logging.Logger] = None,
        client: Optional[httpx.AsyncClient] = None,
    ):
        super().__init__(
            base_url,
            database=database,
            schema=schema,
            jwt=jwt,
            headers=headers,
            timeout=timeout,
            verify=verify,
            follow_redirects=follow_redirects,
            limits=limits,
            enable_logs=enable_logs,
            log_level=log_level,
            log_request_body=log_request_body,
            log_response_body=log_response_body,
            max_log_body_chars=max_log_body_chars,
            retry=retry,
            logger=logger,
        )
        self._owns_client = client is None
        if client is not None:
            self._client = client
        else:
            kwargs: Dict[str, Any] = {
                "timeout": timeout,
                "headers": self._base_headers,
                "verify": verify,
                "follow_redirects": follow_redirects,
            }
            if limits is not None:
                kwargs["limits"] = limits
            self._client = httpx.AsyncClient(**kwargs)

    async def __aenter__(self) -> "AsyncPrestd":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Any = None,
        json: Any = None,
        headers: Optional[Mapping[str, str]] = None,
        auth: Optional[httpx.Auth] = None,
    ) -> httpx.Response:
        url = self._build_url(path)
        all_headers = _merge_headers(self._base_headers, headers)
        self._log_request(method.upper(), url, params=params, json_body=json)

        attempts = self._retry.retries + 1
        for attempt in range(attempts):
            t0 = time.perf_counter()
            try:
                resp = await self._client.request(
                    method.upper(),
                    url,
                    params=params,
                    json=json,
                    headers=all_headers,
                    auth=auth,
                )
            except httpx.TimeoutException as e:
                if attempt < attempts - 1:
                    await asyncio.sleep(self._retry.backoff * (2**attempt))
                    continue
                raise PrestdTimeoutError(str(e)) from e
            except httpx.RequestError as e:
                if attempt < attempts - 1:
                    await asyncio.sleep(self._retry.backoff * (2**attempt))
                    continue
                raise PrestdConnectionError(str(e)) from e

            elapsed = time.perf_counter() - t0
            self._log_response(
                method.upper(),
                url,
                resp.status_code,
                elapsed,
                text=resp.text if self._log.log_response_body else None,
            )

            if (
                resp.status_code in self._retry.retry_statuses
                and attempt < attempts - 1
            ):
                await asyncio.sleep(self._retry.backoff * (2**attempt))
                continue

            self._raise_for_status(method.upper(), url, resp)
            return resp

        raise PrestdConnectionError("Request failed")

    async def _arequest_json(
        self,
        method: str,
        path: str,
        *,
        params: Any = None,
        json: Any = None,
        headers: Optional[Mapping[str, str]] = None,
        auth: Optional[httpx.Auth] = None,
    ) -> Any:
        resp = await self.request(
            method, path, params=params, json=json, headers=headers, auth=auth
        )
        return self._decode_response(resp)

    # --- resources ---
    def table(
        self,
        name: str,
        *,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        safe_writes: bool = True,
    ) -> AsyncTable[Any]:
        db = database or self.database
        sc = schema or self.schema
        parts = name.split(".")
        if len(parts) == 2:
            sc, name = parts
        elif len(parts) == 3:
            db, sc, name = parts
        if not db:
            raise PrestdUsageError(
                "No database provided. Set client.database or pass database=..."
            )
        if not sc:
            raise PrestdUsageError(
                "No schema provided. Set client.schema or pass schema=..."
            )
        return AsyncTable(
            client=self, database=db, schema=sc, name=name, safe_writes=safe_writes
        )

    # --- common endpoints ---
    async def health(self) -> Any:
        return await self._arequest_json("GET", "/_health")

    async def databases(self) -> Any:
        return await self._arequest_json("GET", "/databases")

    async def schemas(self) -> Any:
        return await self._arequest_json("GET", "/schemas")

    async def tables(self) -> Any:
        return await self._arequest_json("GET", "/tables")

    async def show(self, database: str, schema: str, table: str) -> Any:
        return await self._arequest_json("GET", f"/show/{database}/{schema}/{table}")

    async def list_schema_tables(self, database: str, schema: str) -> Any:
        return await self._arequest_json("GET", f"/{database}/{schema}")

    # --- auth helpers ---
    async def auth_bearer(self, username: str, password: str) -> Any:
        return await self._arequest_json(
            "POST", "/auth", json={"username": username, "password": password}
        )

    async def auth_basic(self, username: str, password: str) -> Any:
        return await self._arequest_json(
            "POST", "/auth", auth=httpx.BasicAuth(username, password)
        )


__all__ = [
    "Prestd",
    "AsyncPrestd",
    "Table",
    "AsyncTable",
    "Query",
    "AsyncQuery",
    "LogConfig",
    "RetryConfig",
    "DatabaseRef",
    "SchemaRef",
    "Explain",
    "enable_default_console_logging",
    "get_logger",
    "PrestdError",
    "PrestdUsageError",
    "PrestdHTTPError",
    "PrestdTimeoutError",
    "PrestdConnectionError",
    "PrestdDecodeError",
    "UnsafeQueryError",
    "NoResults",
    "MultipleResults",
]
