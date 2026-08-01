# service_providers/ — reference

Deep reference for the **only code in this skill that touches the network**:
the client, the credential resolution, and the four decisions that make a
report's numbers trustworthy. The authoring contract lives in `../SKILL.md`;
what the provider itself does and does not serve is in `fmp/endpoints.md`.

```
service_providers/
  config.py          non-secret settings, from config/config.<env>.json
  fmp/
    client.py        FmpClient — get(), get_many(), rate limiting
    credentials.py   api_key() — a two-place resolution order
    endpoints.md     what FMP actually serves, what the plan gates, what lies
```

One provider so far. A second would sit beside `fmp/` with the same three
files; nothing in the skill imports a provider by any name but its own.
`config.py` is shared, because the environment is a property of the run rather
than of any one provider.

## Config and secrets are two files, split per FILE

```
config/config.<env>.json    TRACKED     api_url, timeouts, anything not secret
secrets.<env>.json          GITIGNORED  api_key, and nothing else
```

Both at the repo root, both chosen by the same `<env>`, so a run cannot read
dev settings against a prod key.

**The split is per-file rather than per-field on purpose.** This repository is
public and served by jsDelivr, so "is this safe to commit?" must be a property
of the FILE, decided once — not a judgement made per field every time someone
adds one. Nobody puts an `api_key` in a tracked config deliberately; they do it
by adding a field beside the fields already there. `config.service_provider()`
therefore rejects a `service_providers.*.api_key` outright and says where the
key belongs.

`client.py` holds no URL of its own: `base_url` defaults to
`service_provider("fmp")["api_url"]`, so pointing a run at a different FMP
surface is a config edit rather than a code change.

## The API

```python
from service_providers.fmp import FmpClient

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
1. FMP_API_KEY            environment variable — preferred, and the only one
                          that works in CI, where there is no file
2. secrets.<env>.json     {"fmp": {"api_key": "..."}} at the REPO ROOT,
                          gitignored. <env> is ENVIRONMENT — no default
3. hard error naming both
```

First hit wins. There is deliberately **no third place it looks** — a skill that
silently reads credentials from wherever it can find them is one refactor away
from reading them from somewhere it should not.

**Why the repo root rather than beside this file.** A skill is meant to be
copied or junctioned into another project as `skills/finance-reports/` and
nothing above it. A credential kept inside that subtree travels with every
copy; one kept above it cannot.

**Why two environments.** A dev key and a production key have different rate
limits and different blast radii, and the way that goes wrong is someone
burning a production quota on a test run.

**Why there is no default environment.** The same reason `--out` has none: an
absent default is a question, not a gap. A default would let a run use the
wrong key and the wrong config in silence — the request succeeds, the numbers
arrive, and only the quota ever says which key paid. `ENVIRONMENT` unset is a hard
error, an unrecognised value is a hard error, and `report_builder.py` takes
`--env dev|prod` as a **required** argument. Required rather than optional
because a required argument cannot be forgotten, and it lands in shell history
and CI logs where a variable set in some earlier shell does not.

**Every build says what it resolved**, before any network call:

```
environment: dev   (config.dev.json, key from secrets.dev.json)
```

`credentials.describe()` produces the second half and never returns the key
itself. It exists for the one silent override left in the order above: a stale
`FMP_API_KEY` in a shell beats `secrets.prod.json` with nothing on screen to
say so.

**There is no template file, and its absence is the safety property.**
`.gitignore` matches `secrets.*.json` with **no exception**, so nothing by that
name is trackable under any circumstance. A shipped `secrets.example.json`
would need a negation to stay tracked, and the failure mode is not hypothetical
here: `git.commit&push.bat` runs `git add .` against a repository that is
public *and* served by jsDelivr. One mis-ordered line in `.gitignore` and a key
is fetchable at a URL. Four lines of JSON written by hand from `README.md` are
cheaper than that.

A placeholder of the form `<...>` is still detected and rejected by name at
build time, rather than being sent to the API so the reader has to work
backwards from a 401.

## Adding an endpoint

1. Check `fmp/endpoints.md` first — it records which paths 404, which the
   Starter plan gates to annual, and where the MCP tool's names differ from the
   API's. That file exists because those cost real time to rediscover.
2. Add it to the report's `ENDPOINTS` (or `QUARTER`) table, never as a loose
   `get()` inside the derivation.
3. An HTTP 402 means the plan gates it, not that your parameters are wrong. The
   error message says as much.

## Adding a provider

Create `service_providers/<name>/` with the same three files. Keep the same two
contracts — **raise rather than return empty**, and **never let the key into an
exception** — because the assertions downstream are written assuming both.
