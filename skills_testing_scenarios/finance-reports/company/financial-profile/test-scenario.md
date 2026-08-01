# Scenario — `financial-profile` for AMD

Exercises the `finance-reports` skill end to end: environment resolution, the
FMP client, the arithmetic assertions in `_build_context`, the view's contract
check, and the full component render. If this passes, the skill works.

**Requires `ENVIRONMENT` to be declared** — either the variable, or
`environment.json` at the repo root containing `{"environment": "dev"}`. There
is no flag and no default.

The directory mirrors the skill's own taxonomy —
`finance-reports/company/financial-profile` — so a scenario sits at the same
address as the thing it tests.

## Run it

From the repo root, with the venv active or by full interpreter path:

```powershell
python .claude/skills/finance-reports/reports/report_builder.py `
    financial-profile AMD `
    --peers NVDA,INTC `
     `
    --out ./skills_testing_scenarios/finance-reports/company/financial-profile
```

Writes `amd-financial-profile.html` beside this file. The output is gitignored:
it carries live market data, so it differs on every run and is a build
artifact, not a fixture.

**AMD with NVDA and INTC as peers** is the useful case rather than an arbitrary
one. All three are semiconductor designers with genuinely different shapes —
AMD is fabless with heavy R&D, INTC carries the capex of its own fabs, NVDA
runs margins several times theirs. That makes `peer-comparison`,
`valuation-multiples` and the segment exhibits show real spread instead of
three near-identical columns, which is what makes a rendering fault visible.

`--peers none` is also valid and is the faster smoke test: it skips the peer
fetches and still exercises every single-company exhibit.

## What must be true

**It must exit 0 and print four lines**, in this order:

```
environment: dev (from <abs path>\environment.json)   config.dev.json, key from <abs path>\secrets.dev.json
fetching ...
deriving and asserting ...
<absolute path to the written file>
```

**Read the first line before trusting the rest.** It names both the environment
and where it was read from, and two things it can say are worth catching: `from
$ENVIRONMENT` means a shell variable is overriding `environment.json`, and
`key from $FMP_API_KEY` means a stale variable is overriding
`secrets.dev.json`. Both are legal and neither is usually intended.

**The assertions must pass silently.** `_build_context` checks identities the
data must satisfy — cost + gross == revenue, liabilities + equity == assets,
each sankey summing to its own table, the segment bridge reaching its endpoint.
A violation raises and the build stops; it never warns. This matters more than
it looks: **a sankey that does not conserve draws perfectly and lies**, because
the engine scales each node's ribbons independently.

**The rendered page must carry no stale class names.** After a build:

```powershell
$h = Get-Content .\skills_testing_scenarios\finance-reports\company\financial-profile\amd-financial-profile.html -Raw
([regex]::Matches($h,'investing-')).Count      # must be 0
([regex]::Matches($h,'\bfa-')).Count           # must be > 0
```

`investing-` was the domain prefix before 6.0.0. Any occurrence means something
in the render path still emits pre-6.0.0 markup against post-6.0.0 CSS, which
degrades silently — the page loads and simply loses that component's styling.

**Both asset halves must resolve.** The page links the local bundle relative to
where it was written and the version-pinned CDN as an `onerror` fallback:

```
href="../../../../.claude/skills/finance-reports/css/bundle.css"
https://cdn.jsdelivr.net/gh/vasilegrafu/aifx-finance@<version>/.claude/skills/finance-reports/css/bundle.css
```

The local path must have the right number of `../` for this directory's depth —
that is computed per output location, so it is exactly what moving the
destination can break. The CDN half 404s until `v<version>` is tagged **and
pushed**; that is expected on an untagged working tree and is not a scenario
failure.

**Open it in a browser.** Charts are drawn by ECharts at view time, so a
malformed spec is invisible in the HTML and shows only on the page — as a card
saying what went wrong, with *show source* beside it. A build can exit 0 with a
broken chart in it.

## Cost and caveats

- **~13 network calls** and roughly ten seconds. Nothing is cached, on purpose:
  a report's claim is that it describes the world at a stated moment, and a
  cache reproduces a stale figure perfectly and silently.
- **Needs a real key** in `secrets.dev.json`. The placeholder is detected by
  name and refused before any request goes out.
- **Numbers change between runs.** Do not diff two outputs and expect equality;
  compare structure, not values.
- Uses the **dev** key, because that is what `environment.json` declares. Run
  it against prod only if you mean to spend production quota on a test, and say
  so for one command rather than editing the file:
  `$env:ENVIRONMENT = "prod"`

## When it fails

| symptom | look at |
|---|---|
| `ENVIRONMENT is not set and ... does not declare it` | the message names the full path it looked for; `environment.json` is tracked, so a clone should have one |
| `is not one of dev, prod` | a typo in `environment.json` or in the shell variable; the message names which |
| `still holds the placeholder` | real key not yet in `secrets.dev.json` |
| an assertion raises | `_build_context` in `report_controller.py` — the data broke an identity, or the endpoint changed shape |
| `StrictUndefined` at render | the view reads a `d.*` key the controller never wrote |
| a chart card says it failed | the spec is invalid JSON or the engine refused it — *show source* |
| every bar is full width | typed `attr()` unsupported and `attr-fallback.js` did not run |
