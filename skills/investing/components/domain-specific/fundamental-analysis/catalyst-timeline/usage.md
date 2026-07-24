# catalyst-timeline

_Authoring guidance for the `catalyst-timeline` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

The dated events that can re-rate the position, each with the direction you
expect and how likely it is. This is the monitoring list a thesis is checked
against between reviews — earnings dates, product cycles, rulings, patent
expiries, lockups, index reviews, refinancing walls.

```jinja
{{ c.catalyst_timeline([
    ("2026-08-01", "FQ3 2026 earnings", "up", "Certain",
     "Services growth above 11% confirms pillar 1; below 8% breaks it."),
    ("2026-09-10", "iPhone 18 launch", "mixed", "Certain",
     "Unit cycle matters less than the ASP mix; watch the Pro share."),
    ("2026-10-31", "EU Digital Markets Act ruling", "down", "Likely",
     "Worst case removes about 4% of Services revenue in Europe."),
    ("2027-Q1", "Google TAC contract renewal", "down", "Possible",
     "About $20B of high-margin revenue is contractually exposed."),
]) }}
```

Rules: ISO dates where the date is known, a quarter where it is not — never
"soon". Direction is your expectation for the POSITION, and `mixed` is a
legitimate answer that beats a false directional call. Likelihood uses one
consistent vocabulary across the project (Certain / Likely / Possible /
Remote). Every catalyst says what it would confirm or break, tying back to a
pillar in `thesis_pillars`. Drop catalysts once they have passed — this is a
forward list, and the history belongs in the change log.
