"""components — formatting: the one place a number becomes a string.

Hung on the Jinja env by showcase_builder.env(), which is the only importer.

WHY THEY LIVE IN components/. Only components use them — 20 call sites across
components/*.j2 and none in reports/*.j2. A report's controller does the
arithmetic and hands over NUMBERS; the macro it calls turns them into strings.
That is what lets this directory not reach outside itself for anything its own
templates need.

In docs-html the author passed pre-formatted strings, which meant every
generator re-implemented money()/pct()/signed() and two documents could
disagree about what a thousands separator looks like. One definition, applied
by the component.

EVERY FILTER PASSES STRINGS THROUGH UNCHANGED. A controller legitimately needs
to emit "n/m" where a ratio has no meaning — a CAGR from a negative base, say —
and forcing that through a numeric format would either crash or invent a
number. Passing it through is the honest behaviour.
"""


def _passthrough(fn):
    def wrapped(value, *a, **kw):
        if isinstance(value, str) or value is None:
            return "" if value is None else value
        return fn(value, *a, **kw)
    return wrapped


@_passthrough
def f_money(v, digits=0):
    return f"{v:,.{digits}f}"


@_passthrough
def f_pct(v, digits=1):
    return f"{v:.{digits}f}%"


@_passthrough
def f_signed(v, digits=0):
    return f"{v:+,.{digits}f}"


@_passthrough
def f_bps(v):
    return f"{v:+,.0f} bps"


@_passthrough
def f_num(v, digits=2):
    return f"{v:,.{digits}f}"


FORMATS = {"money": f_money, "pct": f_pct, "signed": f_signed,
           "bps": f_bps, "num": f_num, "raw": lambda v: v}


def f_fmt(value, spec="num", *a, **kw):
    """Dispatch by name, so a component can take `fmt="money"` as an argument.

    Named `fmt` rather than `format` because Jinja already ships a `format`
    filter (printf-style) and shadowing it would break any template using it."""
    if spec not in FORMATS:
        raise ValueError(f"unknown format {spec!r} — one of {', '.join(FORMATS)}")
    return FORMATS[spec](value, *a, **kw)


#: What the env exposes. Derived from FORMATS rather than restated, so the two
#: cannot drift — `fmt` dispatches over exactly the names available directly.
#: `raw` comes along as the identity filter, which is what it already meant.
FILTERS = {**FORMATS, "fmt": f_fmt}
