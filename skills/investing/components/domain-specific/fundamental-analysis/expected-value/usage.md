# expected-value

_Authoring guidance for the `expected-value` component — when to use it, how, and the rules._

Styled by: `css/domain-specific/investing.css`

Scenarios with probabilities attached and the arithmetic done: the bridge
between "here is what could happen" and "therefore this is worth owning at
this size". Where `scenarios` (business category) describes the states of the
world in prose, this component prices them.

```jinja
{{ c.expected_value(
    caption="Apple — 12-month probability-weighted return from $232",
    total="+9.8%",
    rows=[
        ("Bull — Services reaccelerates, margin holds", "good",    "25%", "$298", "+28.4%", "+7.1%"),
        ("Base — mid-single-digit growth, flat multiple", "neutral", "50%", "$268", "+15.5%", "+7.8%"),
        ("Bear — DMA ruling plus hardware air pocket", "bad",     "25%", "$180", "-22.4%", "-5.6%"),
    ]) }}
```

Rules: probabilities sum to exactly 100% and the footer says so — a table that
sums to 90% is an error, not a rounding. Weighted = probability × return,
computed by hand and stated; the document never computes at view time. Three
to five scenarios, each tied to a named driver, not to a mood. If the expected
value is positive only because the bull case is generous, that is the finding
— say it under the table. Pair with `recommendation`: a positive expected
value with a thin margin of safety still sizes small.
