"""The checks a showcase controller makes, written once.

`_validate_context` does the half StrictUndefined cannot: a key present and
WRONG. Those checks are nearly all about AGREEMENT — points against their
categories, names against the other names in the same legend — and agreement is
the same relation whatever component is asking. Ten of the charts share one
contract exactly:

    series[] {name:str, points:num[]}   categories: str[]

Copied into ten files it would be ten claims about that contract, free to
disagree, which is how `bar` and `area` would drift the moment one of them
learned something. Here, a lesson is learned once.

A component still writes the checks only IT can make -- `area` capping the
overlapping fills at two, `sankey` conserving flow -- beside a call to these.
"""

import math

#: Number.MAX_SAFE_INTEGER. A page parses its data with JSON.parse, where every
#: number becomes a float64, so an integer past this arrives rounded.
JS_SAFE_INT = 2 ** 53 - 1


def assert_numbers(component, where, values):
    """Every value is a real, finite, JS-safe number.

    THREE FAILURES THAT ALL RENDER AS SILENCE, not as an error:

    - NaN and the infinities pass every isinstance test and reach
      `_render.html.j2`'s `| tojson`, which writes them into the <pre> as bare
      NaN / Infinity. That is not JSON, so the browser's JSON.parse throws and
      the page shows no chart at all.
    - bool is an int in Python, so `True` would draw as 1.
    - JS has one number type, float64; an integer past 2**53 arrives rounded.
      Floats are already float64 and round-trip exactly, so only ints can lose.
    """
    for i, v in enumerate(values):
        assert isinstance(v, (int, float)) and not isinstance(v, bool), \
            (f"{component}: {where} value {i} is {v!r}; must be a number, "
             f"it goes straight to ECharts")
        assert math.isfinite(v), \
            (f"{component}: {where} value {i} is {v!r}; tojson writes it "
             f"unquoted and the browser's JSON.parse rejects it, so the chart "
             f"never renders")
        assert not isinstance(v, int) or abs(v) <= JS_SAFE_INT, \
            (f"{component}: {where} value {i} is {v}, past JavaScript's safe "
             f"integer range; it would arrive rounded")


def assert_labels(component, where, labels):
    """A non-empty list of non-empty, DISTINCT strings.

    Duplicates are the interesting half: two ticks a reader cannot tell apart,
    and a tooltip that picks whichever came first."""
    assert isinstance(labels, list) and labels, \
        f"{component}: {where} must be a non-empty list"
    assert all(isinstance(c, str) and c for c in labels), \
        f"{component}: {where} must hold non-empty str"
    repeated = sorted({c for c in labels if labels.count(c) > 1})
    assert not repeated, \
        (f"{component}: {where} repeats {', '.join(map(repr, repeated))}; two "
         f"labels a reader cannot tell apart, and a tooltip that picks "
         f"whichever came first")


def assert_enum(component, where, value, allowed):
    """A field whose value carries MEANING the CSS reads.

    `tone`, `kind`, `status`, `verdict` -- a typo does not raise, it renders
    unstyled, which reads as "neutral" rather than as "broken"."""
    assert value in allowed, \
        (f"{component}: {where} is {value!r}; one of "
         f"{', '.join(map(repr, sorted(allowed)))}. An unrecognised value is "
         f"not an error at render -- it just loses its styling")


def assert_rows(component, where, rows, required, minimum=1):
    """Every row is a dict carrying `required`, and there is at least one.

    The shape check that comes before any judgement about the values: a row
    missing a key raises at render under StrictUndefined, but a row that is not
    a dict at all fails somewhere less obvious."""
    assert isinstance(rows, list) and len(rows) >= minimum, \
        f"{component}: {where} needs at least {minimum} row(s)"
    for i, row in enumerate(rows):
        assert isinstance(row, dict), \
            (f"{component}: {where}[{i}] is {type(row).__name__}, not a dict")
        missing = [k for k in required if k not in row]
        assert not missing, \
            (f"{component}: {where}[{i}] is missing {', '.join(missing)}; the "
             f"view reads them and StrictUndefined would stop the build here "
             f"with the template named instead of the row")


def assert_all_drawn(component, d, calls):
    """Nothing in the context goes undrawn.

    Every other check runs from the calls to the context; this one runs back,
    and it is what notices a section the view renamed or data orphaned by one
    it deleted."""
    drawn = {name for axis, keys in calls for name in (axis, *keys)}
    undrawn = sorted(set(d) - drawn)
    assert not undrawn, \
        f"{component}: {', '.join(undrawn)} in the context but drawn by no section"


def assert_series_categories(component, d, calls, max_series=None):
    """The contract ten charts share, checked against every call the view makes.

        series[] {name:str, points:num[]}   categories: str[]

    `calls` is the <section>s of showcase.html.j2, one entry each, read as
    categories -> the series drawn against them. PER SECTION rather than
    grouped by axis, because both checks that matter are relative: points
    against ITS categories, and names against the OTHER names in the same
    legend. A section added to the view is an entry added here.

    `max_series` is for the components where more series is not more
    information -- overlapping fills hide one another past two.
    """
    assert_all_drawn(component, d, calls)

    for axis, series_keys in calls:
        assert axis in d, f"{component}: {axis!r} missing from the context"
        categories = d[axis]
        assert_labels(component, f"{axis!r}", categories)

        if max_series is not None:
            assert len(series_keys) <= max_series, \
                (f"{component}: {len(series_keys)} series against {axis!r}, "
                 f"more than the {max_series} this component can show apart")

        for key in series_keys:
            assert key in d, f"{component}: {key!r} missing from the context"
            series = d[key]
            assert isinstance(series, dict), \
                (f"{component}: {key!r} must be a dict of name and points, got "
                 f"{type(series).__name__}")
            assert isinstance(series.get("name"), str) and series["name"], \
                (f"{component}: {key!r} needs a non-empty str name, which "
                 f"labels the legend")
            points = series.get("points")
            assert isinstance(points, list) and points, \
                f"{component}: {key!r} needs a non-empty list of points"
            assert_numbers(component, f"{key!r} points", points)

            # The check StrictUndefined cannot make. ECharts pairs series to
            # categories BY INDEX and complains about neither a short nor a
            # long list: the chart draws, and the surplus is simply not there.
            assert len(points) == len(categories), \
                (f"{component}: {key!r} has {len(points)} points against "
                 f"{len(categories)} {axis}; the chart would draw and drop the "
                 f"difference silently")

        # From two series up the macro adds a legend, keyed BY NAME, so
        # duplicates collapse into one entry and a series becomes unlabelled.
        # Per section, not global: two sections may each draw a series called
        # "FY24" as long as no section draws both.
        names = [d[k]["name"] for k in series_keys]
        repeated = sorted({n for n in names if names.count(n) > 1})
        assert not repeated, \
            (f"{component}: {' and '.join(series_keys)} share the name "
             f"{', '.join(map(repr, repeated))}; one legend key would stand "
             f"for both")
