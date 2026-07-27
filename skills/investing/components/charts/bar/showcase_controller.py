"""Showcase controller for the `bar` component.

CONTRACT (every showcase_controller.py follows it):

    context() -> dict

The dict reaches showcase.html.j2 as `d`. Build it line by line — this is the
controller in the web sense: it assembles a view model and hands it over. It
emits NO markup and calls NO macro; the view does both, so the showcase
exercises the same path a report does.

Show the states that matter — the default, and the ones where the component
has to make a decision (a legend appears past one series, an axis name widens
the margin). Keys should read as what the data IS, not as which case uses it,
so the view can recombine them.

The macro these feed must match the {# data: … #} header in component.html.j2:

    series[] {name:str, points:num[]}   categories: str[]
"""


def context():
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    segments = ["Cloud", "License", "Hardware", "Services"]

    fy24 = {"name": "FY24", "points": [12.4, 13.1, 13.9, 15.2]}
    fy23 = {"name": "FY23", "points": [10.8, 11.5, 12.2, 13.0]}

    revenue = {"name": "Revenue", "points": [12.4, 13.1, 13.9, 15.2]}
    by_segment = {"name": "FY24", "points": [22.1, 14.7, 3.2, 5.4]}
    margin_by_segment = {"name": "FY24", "points": [31.2, 88.4, 9.1, 24.7]}

    return {
        "quarters": quarters,
        "segments": segments,
        "revenue": revenue,
        "fy24": fy24,
        "fy23": fy23,
        "by_segment": by_segment,
        "margin_by_segment": margin_by_segment,
    }
