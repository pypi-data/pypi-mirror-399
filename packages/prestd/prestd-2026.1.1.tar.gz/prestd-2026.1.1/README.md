# prestd

`prestd` is a Python SDK for pRESTd that provides a fluent, typed, and ergonomic API 
for interacting with Postgres backed REST endpoints. It enables developers to compose 
readable, chainable queries for selecting, inserting, updating, and deleting data—without 
writing raw HTTP calls or SQL—while supporting sync and async usage, optional Pydantic 
models, pagination helpers, and clean error handling. Designed for excellent developer
experience, `prestd` makes pRESTd feel like a native Python data client rather than a 
generic REST wrapper.

You get the full ergonomics of a fluent Python client, with the operational guarantees of 
Postgres, all while communicating over standard REST/HTTP protocols.

## Prerequisites

This is a SDK for pRESTd, so you need to have a running instance of pRESTd connected to a
Postgres database. You can find instructions for setting up pRESTd in its official
repository: https://github.com/prest/prest
