"""A thin, deliberately un-clever FMP client. The only thing in this skill
that touches the network.

NO CACHING, ON PURPOSE. A financial report's whole claim is that it describes
the world at a stated moment, and a cache reproduces a stale price perfectly and
silently — the failure the basis-of-preparation block exists to prevent. A full
report is ~13 calls and about ten seconds. Pay it.

The rate limiter is politeness, not protection (290 calls / 10 s).
"""

import time
from collections import deque

import httpx

from .credentials import api_key

# FMP's Starter plan. See endpoints.md for what this plan cannot reach.
RATE_LIMIT, RATE_WINDOW = 290, 10.0


class FmpError(RuntimeError):
    """A request failed. Raised rather than returning [] — see the note below."""


class FmpClient:
    """`get(endpoint, **params)` -> parsed JSON.

    RAISES RATHER THAN RETURNING EMPTY. An empty list becomes a missing row,
    then a broken sum, then a sankey that no longer conserves — all rendered
    without complaint. Failing loudly at the source is what lets the identity
    assertions downstream assume their input is real."""

    def __init__(self, key: str | None = None, base_url: str | None = None,
                 timeout: float = 30.0):
        # Both resolved lazily and from the SAME environment: the URL out of
        # the tracked config.<env>.json, the key out of the gitignored
        # secrets.<env>.json. Neither is a constant in this file, so pointing a
        # run at a different FMP surface is a config edit, not a code change.
        from ..config import service_provider

        self._key = key or api_key()
        self._base = (base_url or service_provider("fmp")["api_url"]).rstrip("/")
        self._timeout = timeout
        self._calls: deque[float] = deque()

    # ------------------------------------------------------------------ rate
    def _throttle(self) -> None:
        now = time.monotonic()
        while self._calls and now - self._calls[0] > RATE_WINDOW:
            self._calls.popleft()
        if len(self._calls) >= RATE_LIMIT:
            time.sleep(RATE_WINDOW - (now - self._calls[0]) + 0.05)
        self._calls.append(time.monotonic())

    # ------------------------------------------------------------------- get
    def get(self, endpoint: str, **params):
        """One endpoint, one call. `params` are passed through untouched."""
        self._throttle()
        query = {k: v for k, v in params.items() if v is not None}
        query["apikey"] = self._key
        url = f"{self._base}/{endpoint.lstrip('/')}"
        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(url, params=query)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as exc:
            # The key is in the query string; never let it reach a log or a
            # traceback that might be pasted somewhere.
            raise FmpError(f"{endpoint}: HTTP {exc.response.status_code}. "
                           f"On the Starter plan this often means the endpoint "
                           f"is gated — see endpoints.md") from None
        except httpx.RequestError as exc:
            raise FmpError(f"{endpoint}: {type(exc).__name__}") from None

        if isinstance(data, dict) and "Error Message" in data:
            raise FmpError(f"{endpoint}: {data['Error Message']}")
        if data in ([], {}, None):
            raise FmpError(f"{endpoint}: empty response for {query.get('symbol', '?')} "
                           f"— wrong symbol, or the plan does not cover it")
        return data

    def get_many(self, calls: list[tuple[str, dict]]) -> dict:
        """Several endpoints in one pass, keyed by endpoint name.

        Sequential, because FMP rate-limits per key and ten calls take about ten
        seconds either way. The value of the method is that a report declares
        its whole data appetite in one place instead of scattering `get` calls
        through its shaping code."""
        return {endpoint: self.get(endpoint, **params) for endpoint, params in calls}
