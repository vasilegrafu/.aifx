# cycle-position

_Authoring guidance for the `cycle-position` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

Marks where you believe the economy, a sector, or a market sits on a phased
cycle, with the evidence for the call written into the phase itself. It turns
the vaguest sentence in macro writing — "we are late cycle" — into a claim with
a position, a date, and a reason.

```jinja
{{ c.cycle_position(
    at=2, asof="July 2026",
    note="Late cycle: growth decelerating with inflation already normalised — historically the phase that rewards quality and duration over cyclicals.",
    phases=[
        ("Early", "Growth accelerating from a low base; credit reopening."),
        ("Mid",   "Growth above trend; margins peak; policy neutral."),
        ("Late",  "Growth decelerating; policy restrictive turning easier; curve re-steepening."),
        ("Recession", "Output contracting; credit spreads wide; earnings revised down."),
    ]) }}
```

Rules: three to five phases, and the phase vocabulary stays constant across
every document in a project so calls can be compared over time. The `note` is
the SO WHAT — what this position implies for allocation — not a restatement of
the phase name. Date the call: a cycle position with no date cannot be scored
later. State the evidence in each phase note so a reader can disagree with the
placement rather than with the conclusion. If you are genuinely between phases,
say so in the note rather than marking two phases current.
