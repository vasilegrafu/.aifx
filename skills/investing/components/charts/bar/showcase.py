"""Showcase data for the `bar` component.

CONTRACT (every showcase.py follows it):

    cases() -> list[(label, kwargs)]

Each pair is one rendered state of the component. `label` names the state for a
human browsing the page; `kwargs` is fed straight to the macro — c.bar(**kwargs)
— so the keys ARE the macro's parameters and must match the {# data: … #} header
in component.html.j2:

    series[] {name:str, points:num[]}   categories: str[]

builder.py discovers this file next to component.html.j2, renders every case
through the live CDN bundle, and writes showcase.html beside it. Show the states
that matter — the default, and the ones where the component has to make a
decision (a legend appears past one series, an axis name widens the margin).
"""


def cases():
    quarters = ["Q1", "Q2", "Q3", "Q4"]

    return [
        (
            "single series — unit as a subtext line under the caption",
            {
                "caption": "Revenue by quarter",
                "unit": "USD, billions",
                "note": "Cloud momentum builds through the year.",
                "categories": quarters,
                "series": [
                    {"name": "Revenue", "points": [12.4, 13.1, 13.9, 15.2]},
                ],
            },
        ),
        (
            "two series — a legend appears, colour is never the only cue",
            {
                "caption": "This year vs last",
                "unit": "USD, billions",
                "note": "Every quarter ahead of the prior year.",
                "categories": quarters,
                "series": [
                    {"name": "FY24", "points": [12.4, 13.1, 13.9, 15.2]},
                    {"name": "FY23", "points": [10.8, 11.5, 12.2, 13.0]},
                ],
            },
        ),
        (
            "named axis — y_name labels the axis, unit names the measure",
            {
                "caption": "Segment revenue",
                "unit": "USD, billions",
                "y_name": "USD (billions)",
                "note": "Cloud is now the largest single line.",
                "categories": ["Cloud", "License", "Hardware", "Services"],
                "series": [
                    {"name": "FY24", "points": [22.1, 14.7, 3.2, 5.4]},
                ],
            },
        ),
        (
            "percentages — a different unit family, same component",
            {
                "caption": "Operating margin by segment",
                "unit": "percent",
                "y_name": "Operating margin (%)",
                "note": "License carries the business; hardware dilutes it.",
                "categories": ["Cloud", "License", "Hardware", "Services"],
                "series": [
                    {"name": "FY24", "points": [31.2, 88.4, 9.1, 24.7]},
                ],
            },
        ),
    ]
