# recommendation

_Authoring guidance for the `recommendation` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

The call, stated once and early: what to do, at what price, over what horizon,
with how much conviction. A reader who reads nothing else reads this block, so
it appears immediately after the executive summary — never buried at the end.
Tone colors the edge: `good` accumulate, `neutral` hold, `bad` reduce/avoid.

```jinja
{{ c.recommendation(
    action="Accumulate", tone="good",
    facts=[
        ("Price target", "$268"),
        ("Upside", "+15.3%"),
        ("Horizon", "12 months"),
        ("Conviction", "Medium"),
        ("Max position", "4% of portfolio"),
    ],
    rationale="Services mix lifts gross margin faster than consensus models it; the hardware cycle is priced as if flat.") }}
```

Rules: the action is a verb the reader can execute today ("Accumulate below
$240"), never "attractive" or "one to watch". A price target without a horizon
is not a target — always give both. Conviction is a real input to sizing, so
state it and let `expected_value` or `scorecard` justify it. The rationale is
ONE sentence; the argument itself belongs in `thesis_pillars`. Revisit and
re-date this block on every document update — a stale call is worse than none.
