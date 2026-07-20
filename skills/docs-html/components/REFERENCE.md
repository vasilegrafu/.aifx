# components/ — reference

Deep reference for the component catalog. The authoring contract lives in
`../SKILL.md`; the generated call-form list is `../CATALOG.md`; how components
are *styled* (the CSS module map, page-local CSS, rebranding) is in
`../css/REFERENCE.md`. This file is how components are *organized and called*.

## The component model

- A component is a Jinja macro in `components/<category>/<name>/component.html.j2`
  (macro name = folder name with `-` → `_`), exposed on the `c` namespace so
  templates call `{{ c.<name>(...) }}` (leaf) or
  `{% call c.<name>(...) %}…{% endcall %}` (container) — no imports.
- The macro file's FIRST line is `{# purpose: one line #}` — read by
  `builder.py catalog` into `CATALOG.md`.
- Every component has a `usage.md` beside it (when + how, the rules) and a live
  demo in `../showcases/components.html`.
- Each category folder has its own `components/<category>/usage.md`: a one-line
  blurb (the single source for `CATALOG.md` group intros and the showcase
  bands) plus a **Use when** line.

**To look something up, don't open files — ask the builder.** `CATALOG.md` lists
every call form + purpose; `python builder.py show <name>` prints one
component's call form, purpose, and full `usage.md`.

The nine categories: `structure`, `content`, `lists`, `callouts`, `blocks`,
`business`, `front-back-matter`, `diagrams`, `math`. For which CSS module styles
each one, see `../css/REFERENCE.md`.

## Adding a component

Add `components/<category>/<new>/{usage.md, component.html.j2}` (pick the
category folder; the builder discovers recursively). The macro file's FIRST line
is `{# purpose: … #}`. Style it in a `css/modules/` file (see
`../css/REFERENCE.md` → "Adding a module"). Add a demo to
`../showcases/components.html.j2`, then run `python builder.py catalog` and
`python builder.py showcase`.
