# scenarios

_Authoring guidance for the `scenarios` component — when to use it, how, and the rules._

Styled by: `css/modules/business.css`

Side-by-side scenario cards (base / bull / bear, best / expected / worst):
each with a title, its assumptions as bullets, and a bold outcome line.
Tones color the card's top edge: `good` green, `neutral` blue, `bad` red.

```jinja
{{ c.scenarios([
    ("Bull", "good", ["Rate cuts land H2", "Margins recover"], "+40% · price 68"),
    ("Base", "neutral", ["Flat rates", "Stable share"], "+12% · price 54"),
    ("Bear", "bad", ["Recession", "Price war"], "−25% · price 36"),
]) }}
```

Rules: 2–4 scenarios; assumptions must be falsifiable statements, not vibes;
every scenario states an explicit outcome so they can be compared.
