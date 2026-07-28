# data_providers/ — reference

Deep reference for the **only code in this skill that touches the network**:
the client, the credential resolution, and the four decisions that make a
report's numbers trustworthy. The authoring contract lives in `../SKILL.md`;
what the provider itself does and does not serve is in `fmp/endpoints.md`.

```
data_providers/
  fmp/
    client.py        FmpClient — get(), get_many(), rate limiting
    credentials.py   api_key() — a two-place resolution order
    endpoints.md     what FMP actually serves, what the plan gates, what lies
```

One provider so far. A second would sit beside `fmp/` with the same three
files; nothing in the skill imports a provider by any name but its own.

## The API

```python
from data_providers.fmp import FmpClient

client = FmpClient()                     # key resolved for you
data   = client.get("profile", symbol="MU")
many   = client.get_many([("income-statement", {"symbol": "MU", "limit": 5}),
                          ("quote",            {"symbol": "MU"})])
```

| member | contract |
|---|---|
| `FmpClient(key=None, base_url=…, timeout=30.0)` | `key=None` resolves through `credentials.api_key()` |
| `.get(endpoint, **params)` | one call, parsed JSON. `params` pass through untouched; `None` values are dropped |
| `.get_many(calls)` | several endpoints in one pass, **keyed by endpoint name** |
| `FmpError` | raised on any failure. A `RuntimeError` subclass |

Base URL is `https://financialmodelingprep.com/stable`.

## Four decisions worth knowing before you change anything

### 1. It raises; it never returns empty

The established getters in `solution.atlas` swallow exceptions and return `[]`,
which suits a dashboard that would rather show a gap than a stack trace. **A
report is the opposite case.** An empty list here becomes a missing row, then a
broken sum, then a sankey that no longer conserves — all rendered without
complaint.

So `get()` raises `FmpError` on a bad status, a transport error, an
`"Error Message"` in the body, **and on an empty `[]`/`{}`/`None` response**.
Failing loudly at the source is what lets the 13 identity assertions downstream
assume their input is real.

### 2. No caching, on purpose

The obvious optimisation is to cache responses so repeated builds are instant,
and it is the wrong call. A financial report's whole claim is that it describes
the world **at a stated moment**. A cache reproduces a stale price perfectly and
silently — exactly the failure the report's basis-of-preparation block exists to
prevent.

A full report is ~13 calls and about thirteen seconds. Pay it. If you are
iterating on a view and the fetch is in your way, that is an argument for
working on a showcase, not for adding a cache.

### 3. The rate limiter is politeness, not protection

290 calls / 10 s, sliding window, mirroring the convention already used in
`solution.atlas`. A single report never approaches it. It exists so that a loop
over many symbols cannot make this skill the reason a key gets throttled.

Sequential by design: FMP rate-limits per key, so ten calls take about ten
seconds either way, and `get_many`'s value is that a report **declares its whole
data appetite in one place** rather than scattering `get()` calls through its
derivation.

### 4. The key never reaches a traceback

The key travels in the query string. `httpx` puts the full URL in
`HTTPStatusError`, so the handler catches it and re-raises `FmpError` with the
**endpoint name only**, using `from None` to drop the chained exception.

**Preserve that if you touch error handling.** This repository is public and is
served by jsDelivr; a key in a pasted traceback is a leaked key.

## Credentials

```
1. FMP_API_KEY               environment variable — preferred
2. credentials.local.json    {"api_key": "..."} beside credentials.py, gitignored
3. hard error naming both
```

First hit wins. There is deliberately **no third place it looks** — a skill that
silently reads credentials from wherever it can find them is one refactor away
from reading them from somewhere it should not.

A key exists in `solution.atlas` at
`config/config.dev.json -> service_providers:fmp:api_key`, and the error message
says so. Read it **into the environment**; do not copy it into a file that might
be committed.

## Adding an endpoint

1. Check `fmp/endpoints.md` first — it records which paths 404, which the
   Starter plan gates to annual, and where the MCP tool's names differ from the
   API's. That file exists because those cost real time to rediscover.
2. Add it to the report's `ENDPOINTS` (or `QUARTER`) table, never as a loose
   `get()` inside the derivation.
3. An HTTP 402 means the plan gates it, not that your parameters are wrong. The
   error message says as much.

## Adding a provider

Create `data_providers/<name>/` with the same three files. Keep the same two
contracts — **raise rather than return empty**, and **never let the key into an
exception** — because the assertions downstream are written assuming both.
