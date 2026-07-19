# presentation

A deck of sequential 16:9 pages — like a PowerPoint presentation read one
page after another. Pure HTML + CSS (+ Mermaid for diagrams): no
navigation code — readers scroll or press PageDown/PageUp and pages snap
into view; page numbers are CSS counters.

- Audience: MUST be established (exec / dev / client) — ask if unstated.
  It changes altitude, not just length:
  - exec: outcomes, money, risk, asks. No implementation detail. ≤ 10 pages.
  - dev: structure, trade-offs, diagrams, code where it earns its place.
  - client: their problem, the solution's value, plan, what you need from them.
- Filename: `docs/<slug>.html` (include the occasion when relevant:
  `sprint-12-review.html`)
- Template: `document.html.j2` (in this folder)
- Depth: `full` when built from an existing document (the research is done —
  read that document); `ask` when from scratch on a broad topic.

## Rules
- `<body class="presentation">`; each `<section class="page">` is one page
  (see `components/page/usage.md`).
- One idea per page; content must FIT the fixed page — overflow is clipped
  by design. A page that doesn't fit is two pages.
- First page: `class="page page-title"` with h1 + metadata. Last page:
  next steps / asks.
- No TOC, no speaker notes.
- When built from a document, link the source document on the title page;
  never contradict it — if the deck needs different facts, update the
  document first.
