# aifx-finance — version history

The SINGLE source of truth for the version is `version.json` at the **repo root**
(machine-readable); this file is its human ledger — newest release first, one
entry per version, written when the version is bumped. **One version governs the
whole repository** and every skill under `skills/` (finance-reports, …); no
version number lives anywhere else (not in the CSS, not in the JS, not in
documents, not per skill).

Semver contract:
- **PATCH** — visual fix, no markup contract change. Safe for every document.
- **MINOR** — additive: new component, new style, new JS feature, new skill.
- **MAJOR** — a markup contract changed, a skill was removed, **or a published
  command changed shape**; documents must opt in to upgrade, a consumer may
  lose a directory it linked, and a command from the previous release may stop
  working.

A published version is immutable: any change, however small, is a new version.
Each release is the git tag `v<version>`; jsDelivr serves every skill from it at
`…/aifx-finance@<version>/skills/<skill>/…`.

---

## 7.0.0 — 2026-08-01

**Major.** `--env` is removed. A command that worked on 6.0.0 now fails with
*unrecognized arguments*, which is the whole reason this is MAJOR rather than
minor — **no document is affected**, and a 6.0.0 page renders identically on
7.0.0 assets.

The semver contract above gained a clause for it. It covered a markup change
and a removed skill; it had nothing to say about the CLI, exactly as it had
nothing to say about removing a skill before 5.0.0 needed it to.

### The environment is declared, not passed

```
1. ENVIRONMENT     the variable — a shell, CI, or setx
2. .env            `ENVIRONMENT=dev` at the repo root, gitignored
3. hard error
```

**Why the flag went.** Two reasons, and the second is decisive:

- It reached only builds driven through `report_builder.py`. Anything importing
  `FmpClient` directly still needed the declaration, so one fact had two homes
  and they were free to disagree.
- **A flag cannot be inherited.** 6.0.0 assumed whoever ran a build would type
  it. In practice builds are driven by a tool that spawns its own shell, which
  inherits nothing from an editor's terminal settings — so the flag had to be
  retyped on every invocation by someone who had no way to make it stick.

**`.env` is not the default coming back.** A default is a value nobody chose
that applies everywhere. This is a file someone wrote, gitignored, naming one
checkout on one machine — a fresh clone has none and fails loudly until it
declares one. What 6.0.0's required flag was protecting against was not
*unstated* but *unnoticed*, and that protection is stronger now, because the
build prints the source as well as the value:

```
environment: dev (from .env)   config.dev.json, key from secrets.dev.json
```

That names the two overrides that were previously silent: a shell `ENVIRONMENT`
beating this checkout's `.env`, and a stale `FMP_API_KEY` beating the secrets
file. `resolve()` returns `(value, source)` for the first; `describe()` reports
the second without ever returning the key.

`_from_dotenv()` reads one key and understands `KEY=value`, `#` comments and
blank lines — deliberately not a dotenv parser, since a fuller one invites
putting things in that file that belong in `config/` (not secret) or
`secrets.<env>.json` (secret). It reads **utf-8-sig**: a BOM is invisible in
every editor and would make the first key match nothing, so the file would look
correct and be silently ignored. PowerShell 5.1 writes one by default.

**Migrating:** drop `--env dev` from every command and write `.env` at the repo
root containing `ENVIRONMENT=dev`. Nothing else changes.

---

## 6.0.0 — 2026-08-01

**Major.** Four renames and one naming rule. Every domain class in the system
changed its name, so **no document upgrades to 6.0.0 by repointing its two head
links** — it must be regenerated. Documents pinned to `@5.x` and earlier are
unaffected and keep rendering from their own immutable tags.

### The repository, the skill, and the reports are renamed

`.aifx` → **`aifx-finance`**, and `skills/investing` → **`skills/finance-reports`**.
The CDN base in `version.json` follows, so every page generated from here links
`…/aifx-finance@6.0.0/skills/finance-reports/…`.

Two consequences worth stating plainly. A project that junctioned or symlinked
`skills/investing` loses that directory on the next pull. And every document
published before today pins `cdn.jsdelivr.net/gh/vasilegrafu/.aifx@…`: GitHub
redirects the old repository name and jsDelivr follows the redirect, so they
keep rendering — but that redirect dies permanently if any account ever creates
a repository called `.aifx`.

`reports/` gained a taxonomy: a report is now filed under its **subject** —
`company/`, `portfolio/`, `market/`, `economy/` — with `financial-profile` at
`company/financial-profile`. Filed by subject rather than by method, because a
report has exactly one subject and usually several methods; a method-shaped
shelf makes every filing decision a judgement call. The domain is shelving for
a reader, not part of the address: discovery is recursive, so a report is still
run by name alone, and a name must be unique across every domain.

### One naming rule, and the end of `investing-`

> **A class is unprefixed ONLY in `foundational/`. Anywhere else it carries the
> name of the directory it lives in.**

`.fa-dcf-value`, `.portfolio-holdings-weight`, `.macro-indicator-row`,
`.chart-figure`, `.diagram-canvas` — and a bare `.bridge-row`, because bridge is
foundational. 460 occurrences of `investing-` are gone.

`bundle.css` had defended that prefix as "the skill's name, not the
discipline's, so a component can move between disciplines without a class
rename." That was a rationalisation of a coincidence. 4.0.0 created the
convention with **two** prefixes, `investing-` and `business-`, which were
domains; 5.0.0 deleted `business`, and the survivor happened to share the
skill's name. Then the skill was renamed and the prefix named nothing that
existed — not the skill, not the directory, not the discipline. A prefix that
names anything other than its own directory has no way to stay true.

The rule is about **anchoring, not spelling**: `.diagram-tools .zoom-label` and
`.diagram-canvas.grabbing` satisfy it, because the unprefixed part is a
descendant or compound of a prefixed class and cannot be selected alone. Three
exceptions are external or contractual — `.katex` belongs to KaTeX, and
`.mermaid` / `.apache-echarts` are engine markup hooks a published document
carries.

### `domain-specific/` held one mislabeled bucket; it now holds three

`fundamental-analysis` was the only discipline, and about half of what it
contained was not fundamental analysis. Reading all 45 purpose headers: 23 were
(statements, valuation, peers, solvency, thesis), **8 were portfolio
analytics** (holdings, performance, attribution, exposure, risk, drawdown,
stress, trades), **2 were macro**, and **12 knew no discipline at all**.

The 12 are shapes, not subjects — a waterfall, a two-way grid, a labelled bar,
a cohort table — and `foundational/`'s own entry rule is "nothing here knows a
discipline." They were domain-specific only because they arrived from
docs-html's investing category in 3.0.0. They move to `foundational/blocks`
(bridge, funnel, heatmap, quadrant-map, scorecard, composite-score) and
`foundational/content` (sensitivity-table, roll-forward, cohort-table,
variance-analysis, metric-trend, expected-value), and lose their prefix, which
is what promotion means.

**Components 45 → 33 domain, 41 → 53 foundational. The total is unchanged at 109.**

`fundamental-analysis.css` splits three ways to match. The three shared skins it
opened with could not follow any one discipline — `table.fin` is opted into by
all three plus six of the promoted components, the `.trend-*` glyph column is
shared by `metric-trend` (now foundational) and `macro-indicators` (now macro),
and the labelled-bar row grammar is shared by `bridge` and `funnel` (now
foundational) with `debt-maturity` (still `fa`). Duplicating them three ways is
the drift 4.2.0 and 5.0.0 were spent deleting, so they were promoted instead:
`table.fin` with `.tone-*` and `.trend-*` to `foundational/content.css`, the bar
row to `foundational/blocks.css`.

The `investing` **layer** becomes `domain`, holding all three files. They are
mutually exclusive by namespace, so there is nothing for them to fight over,
and a fourth discipline costs one `@import` and no layer edit — the shape
`charts/` and `diagrams/` already use. The layer is named for the SCOPE, which
is what let the old name outlive the thing it was named after.

### Three smaller repairs the rule exposed

- **`.sep`**, the 1px divider between toolbar button groups, was defined
  **byte-identically** in both `charts.css` and `diagrams.css`. It is now in
  `foundational/base.css` beside `.doc-toolbar`, which was already there — one
  rule for all three toolbars.
- **`.mermaid-editor*`** → `.diagram-mermaid-editor*`, the only genuine
  violation of the rule outside `domain-specific/`. Safe to rename: the editor
  panel is built by `diagram-mermaid.js` at runtime, so no published document
  contains those classes.
- `charts.css` was reported as styling `.diagram-tools`. It does not — the
  reference is in a comment. Nothing to fix, recorded so it is not re-found.

### The engine modules take their directory's name, and stop borrowing a class

`js/modules/diagram-mermaid.js` → **`diagrams-mermaid.js`** and
`chart-apache-echarts.js` → **`charts-apache-echarts.js`**, so an engine module
is named for the directory it sits in — the same rule the classes follow. The
`MODULES` list in `bundle.js` and each module's own `register({name})` follow;
a name that does not resolve to a file is a 404 at runtime and a silently dead
feature, so the two are checked against each other.

`chart-apache-echarts.css` had hung its containment rules off **`.chart-canvas`**,
the class the SHARED frame owns. An engine file reaching into shared markup is
the seam leaking: those rules are true of ECharts and false of the next engine.
`charts-apache-echarts.js` now adds **`.charts-apache-echarts-canvas`** to the
canvas before it draws, and the three rules hang off that. Safe to change — the
canvas and its class are built at runtime, so no published document names them.

### `data_providers/` becomes `service_providers/`, with config beside secrets

The directory is renamed in place — it stays **inside** the skill, so the
README's Option B still works: junction `skills/finance-reports/` and the data
layer comes with it. `service_providers` also matches the key the config
document uses.

Settings now come in two files per environment, and **the split is per FILE,
not per field**:

```
config/config.<env>.json    TRACKED     api_url, and anything else not secret
secrets.<env>.json          GITIGNORED  api_key, and nothing else
```

**There is no `secrets.example.json` to copy**, deliberately: `.gitignore`
matches `secrets.*.json` with no exception, so nothing by that name is
trackable under any circumstance. A shipped template would need a negation, and
the repo's own `git.commit&push.bat` runs `git add .` against a public,
CDN-served repository — one mis-ordered line and a key is fetchable at a URL.
The shape is documented in `README.md`, which also gained the setup it never
had: venv, config, secrets, and the run command.

This repository is public and served by jsDelivr, so "is this safe to commit?"
has to be a property of the file, decided once, rather than a judgement made
per field every time someone adds one. Nobody puts an `api_key` in a tracked
config deliberately; they do it by adding a field beside the fields already
there. `config.service_provider()` rejects a `service_providers.*.api_key`
outright and says where the key belongs.

`client.py` loses its `BASE_URL` constant: `base_url` defaults to
`service_provider("fmp")["api_url"]`, so pointing a run at a different FMP
surface is a config edit rather than a code change.

`credentials.local.json`, which sat beside `credentials.py`, is replaced by
`secrets.<env>.json` **at the repo root** — outside the skill on purpose, since
a credential kept inside that subtree travels with every copy of the skill and
one kept above it cannot. `config/` sits beside it and costs nothing new: the
skill already resolves `REPO_ROOT` to read `version.json`. `FMP_API_KEY` still
wins over both; it is the only option that works in CI, where there is no file.

### There is no default environment

`` is **required** on `report_builder.py`, and `ENVIRONMENT` unset
is a hard error. This is the decision `--out` already made one directory over:
an absent default is a question, not a gap.

A default would let a run use the wrong credentials and the wrong config in
silence — the request succeeds, the numbers arrive, and only the quota or the
rate limit ever says which key paid for them. One switch selects both files, so
a run cannot read dev settings against a prod key. Required rather than
optional because a required argument cannot be forgotten, and it lands in shell
history and CI logs where a variable set in some earlier shell does not.

Every build now states what it resolved, before the ~13 calls:

```
environment: dev   (config.dev.json, key from secrets.dev.json)
```

That line also exposes the one silent override left in the order: a stale
`FMP_API_KEY` in a shell beats `secrets.prod.json`, and now says so.

**Migrating:** move your key out of `credentials.local.json` into
`secrets.dev.json` and delete the old file; add `--env` to every build command.
`.gitignore` covers `secrets.*.json` and does **not** cover `config/`.

### Tooling: a declared environment, and scenarios instead of an output shelf

`requirements.txt` names the two libraries the tree needs — Jinja renders every
template, httpx is the only thing that touches the network — with `.venv/`
gitignored. Nothing here builds the published CSS or JS; those are still served
raw from the git tag, which is what keeps a published tag immutable without
qualification.

**`skills_testing_scenarios/`** holds a runnable scenario per report, at an
address mirroring the skill's own taxonomy —
`finance-reports/company/financial-profile/test-scenario.md`. Each states the
command, what must be true of the output, what it costs, and what each failure
mode points at. The generated `.html` is gitignored: it carries live market
data and would churn on every run.

There is no `output/` shelf, deliberately. `--out` is required and has no
default, and a conventional directory is the beginning of a default — the
page's local asset href is computed relative to where the file is written, so
the destination is a decision, not a habit.

### Migrating

Regenerate. There is no head-link edit that carries a 5.x document to 6.0.0,
because the class names in its body changed. An existing document left pinned
to `@5.0.0` keeps rendering exactly as it does today, which is what the pin has
always been for.

---

## 5.0.0 — 2026-08-01

**Major.** The `docs-html` skill is removed. `investing` is the whole repo.

447 files and 23,180 lines: 116 components, 83 doc-types across ten domains,
`builder.py` and its five subcommands, the showcase gallery, and a second copy
of the design system. It was capable and too hard to use — composing a document
meant learning a doc-type catalog, a component catalog and a builder CLI before
writing a sentence, and what came out was still a skeleton to fill in by hand.

**Nothing already published breaks.** A document composed against docs-html
links `…/.aifx@4.4.2/skills/docs-html/…`, and a published tag is immutable, so
every document ever generated keeps rendering from the version it was authored
against. That is what the pin has always been for.

**What does break:** a project that junctioned or symlinked `skills/docs-html`
into its `.claude/skills/` loses that directory on the next pull, and no new
document can be composed. Both are recoverable from tag `v4.4.2` or from
history — which is why this is MAJOR rather than MINOR. The contract above had
no clause for removing a skill; it does now.

**The duplication goes with it.** Each skill carried a full copy of the design
system and the copies had already drifted: `charts.js`, `foundational/base.css`
and `charts/charts.css` differed between the trees while the rest stayed
identical. A fix like 4.4.2's had two homes and reached one. There is now
exactly one `theme.css`, one chart frame, one set of chart components.

`investing` is unchanged by this release and never depended on docs-html: its
`bundle.css` resolves only its own modules, and no path in the tree pointed
across. The `/* docs-html — … */` headers still sitting in its CSS are stale
comments from the original copy, not references.

---

## 4.4.2 — 2026-07-28

**Patch.** Six axis charts in `investing` name their series again.

A rename had written the ECharts key as `"s.name"` where `"name"` was meant,
in `line`, `smoothed-line`, `stacked-line`, `stacked-column`,
`stacked-horizontal-bar` and `bar-negative`. 4.4.1 fixed `area`; this finishes
the family.

The engine received an unknown key and no name at all, which fails twice and
silently. The legend is keyed by name, so past one series it drew blank
swatches; and the axis label never rendered while the grid still widened its
margin to 46px to make room for it, leaving a reserved gutter with nothing in
it. The chart still drew, and drew almost right, which is how it survived a
rename and a release.

Documents built on 4.4.0 or earlier are unaffected — a chart's option is baked
into the page at build time, so an existing document already carries whatever
its series were named when it was composed.

---

## 4.4.1 — 2026-07-28

**Patch.** A divider no longer double-spaces the heading beneath it.

A heading straight after an `<hr>` — or after `.doc-meta`'s bottom border —
stacked its own prose lead-in on top of the divider's `--block-gap`. Adjacent
margins collapse to the LARGER of the two, so the 1.6rem `h3` lead-in won:
every rule sat 16px below the block above it and 26px above the heading below,
off-centre in a gap half again bigger than the page's rhythm. Both are now 16px.

The rule needs two arms, because a bare `<section>` has no padding or border
and its first heading's margin collapses THROUGH it: the adjacency is
`hr + section`, and `hr + h3` never matches. That is the shape every component
showcase has.

Reports are untouched — they carry no `<hr>`, and a `<nav class="toc">` sits
between the header and the first section, so neither arm matches.

Also in `investing`: showcases for the `area` and `apache-echarts` components,
and `area/component.html.j2` picked up the `"s.name"` fix that 4.4.2 extends to
the rest.

---

## 4.4.0 — 2026-07-28

**Minor.** Two shipped changes in the `investing` bundle, plus a build-side
restructure that does not reach a document.

**Charts no longer flash their spec.** The JSON used to sit on screen until the
engine drew over it, so every chart showed a wall of raw data first. The spec
now ships `hidden` from the one macro all chart components funnel through, and
the three paths that used to fail in silence — invalid JSON, a spec the engine
refuses, an engine that never loads — each state what happened in a card where
the chart should have been, with *show source* one click away. New CSS:
`.chart-figure.chart-failed`, `.chart-status`, `.chart-source-toggle`. In the
runtime, `markError(pre)` becomes `fail(pre, message)`.

Additive for existing documents: a 4.3.1 document whose specs carry no `hidden`
renders on 4.4.0 assets exactly as it did. Nothing has to opt in.

**Local-first asset loading.** A generated page now links the bundle twice
over — the local copy, relative to wherever the file was written, and the
version-pinned CDN as an `onerror` fallback. Local first, so a page previews
the current tree the moment it is generated; CDN second, so the same file still
renders once it leaves the tree. The two halves live beside the bundles they
load, `css/css.loader.html.j2` and `js/js.loader.html.j2`, because they fail
differently: a `<link>` retargets its own `href`, while a `<script>` that has
failed will not re-fetch on a new `src` and must be replaced with a fresh
element.

**Build-side, no effect on the shipped bundle.** Reports and showcases became
one pattern — a shell, a controller returning data, and a view that is the only
thing calling a macro — so Python no longer emits markup on either side. Each
directory owns its engine and runs alone (`reports/report_builder.py`,
`components/showcase_builder.py`); `builder.py` is dispatch only, and `check`,
`list` and `show` are gone. The skill gained a `SKILL.md`.

**Removed from `investing` only:** the `return-distribution` component and the
`boxstats` filter that existed solely for it. `docs-html` keeps both, and no
generated document is affected — an existing box plot is already static markup.
Component count 110 → 109.

---

## 4.3.1 — 2026-07-24

**Patch.** Fixes the `investing` **`bar`** chart: an earlier sweep had
over-replaced string literals, leaving `"s.name"` as ECharts option keys where
`"name"` was meant — so series and axis names were silently dropped (ECharts
ignores unknown keys, so it drew cleanly and lied). No markup contract change.

Also adds per-component **showcases** (`showcase.py` beside each component;
`builder.py showcase` renders each into a browsable page) — build-side tooling
that does not affect the shipped CSS/JS bundle.

---

## 4.3.0 — 2026-07-24

**Minor.** Adds the **`investing`** skill — a data-driven report generator
(`service_providers/fmp` → `report.builder.py` → `report.html.j2` → thin
components → HTML), with 110 components seeded from docs-html 4.2.0 and one
report (`financial-profile`). No change to docs-html markup: a 4.2.0 document
upgrades, if desired, by repointing its two head links to `@4.3.0`, and still
resolves unchanged on the retained `v4.2.0` tag if left alone.

### Versioning is now repo-wide

The repo previously carried one `version.json` per skill. With a second
independently-usable skill, that split invited drift, so the version moved to a
single **root `version.json`**, and both builders read it and substitute the
skill name into the CDN path. A change to *either* skill now bumps this one
number and gets one entry here.

---

## 4.2.0 — 2026-07-24

**Minor.** The exhibit title becomes a title, and `financial-profile` gains two
exhibits. No markup contract change: a 4.1.0 document upgrades by repointing its
two head links, and will look different in one specific way — see below.

### A table caption now outranks the row beneath it

**This is the only change that alters existing documents.** Table captions and
leading figure captions were set at `.72rem`, bold, uppercase, `.12em` tracked,
in the muted tone. The column-header row directly beneath them was set at
`.70rem`, bold, uppercase, `.10em` tracked, in the muted tone — a difference of
`.02rem` and `.02em`. The title carried no rank of its own and read as a second
header row, while the chart title beside it was already 15px bold ink.

One treatment now, in `foundational/content.css`, matched to that chart title:

```css
caption, figcaption:first-child { font-size: .95rem; font-weight: 700; color: var(--fg); }
```

`:first-child` carries the distinction: **a figcaption that LEADS its figure is
a title, one that FOLLOWS is a caption**, and the softer `.85rem` rule still
styles the latter. Verified across the showcase: 42 of 43 titled exhibits at
15.2px. The one exception is `figure.code > figcaption`, a code header with a
language badge rather than a title.

Adding the rule was not the fix — **deleting fifteen copies of it was.** The
same four declarations were restated in `investing.css` and `business.css`, and
because `content` sits before `business` and `investing` in the `@layer` order,
those copies would have won. Nothing restates the treatment now, which is why
changing it in one place changes every exhibit.

Two smaller consequences: `.investing-st-unit` carried `text-transform: none`
and `letter-spacing: 0` resets that existed only because the caption was
uppercase — dead, and replaced with a proper subordinate treatment; and
`.change-history` no longer keeps its own `.68rem` variant.

### `financial-profile` gains a balance-sheet sankey and a stacked area

The **balance-sheet sankey** puts assets on the left, `Total assets` in the
middle, and the claims on the right — liabilities as `cost`, equity as
`retained`. It answers in one look what the table answers with arithmetic: how
much of what it owns does the company actually own? A caveat rides with it, in
both `sankey/usage.md` and the doc-type's: **a balance sheet is a stock, not a
flow.** Nothing moves along those ribbons, and a reader who has just read two
flow sankeys will otherwise read movement into this one.

The **stacked area** goes between the segment table and the 100% mix chart, so
the evolution section runs totals → shares → attribution. A reader who sees
composition shift before seeing the total move cannot tell growth from
substitution.

---

## 4.1.0 — 2026-07-23

**Minor.** A new document type, and the chart title area gains a single owner.
Purely additive: every 4.0.0 document keeps working untouched, and **the
published CSS and JS are byte-identical to 4.0.0** — nothing in `css/` or `js/`
changed, so this release only affects documents composed from now on.

### New doc-type: `financial-profile`

`investing/financial-profile` — where a company's money comes from, where it
goes, and how that shape changed. It answers the question that comes *before*
[[investment-thesis]]: understand the business, without making a call on it.

Five sections, and **two sankeys on purpose**, because "how the money is spent"
has two honest answers that disagree. The first is accounting — revenue
consumed by cost of revenue, R&D, SG&A and tax. The second is cash — capex,
buybacks, dividends, debt repayment. For a mature company the second routinely
dwarfs the first and appears nowhere on the income statement.

Doc-type count 74 → 75. No new components: it composes existing ones.

### The chart title area has one owner

`components/charts/_render.html.j2` now sets the title, places the legend clear
of it, and reserves the top margin — for all 21 chart kinds, from one rule.

Each chart used to set its own title and separately guess its own clearance,
and the copies drifted: sixteen repeated the literal `(52 if caption else 16)`,
while `sankey` pinned its series at 14 and drew its caption straight through
the ribbons. `pie`, `funnel` and `gauge` reserved nothing at all — the gauge
arc ran under its own caption. Five kinds bypassed the shared tail entirely,
and four of those five duplicated it byte for byte.

Radial charts (`radar`, `gauge`) now derive their centre from the height they
were given instead of two hand-tuned percentages.

### `unit` — required by shape, not everywhere

Every chart accepts `unit`, rendered as a subtext line under the caption in the
theme's muted tone (`title.subtextStyle` was already in the registered theme,
unused). But a unit is only *required* where there is nowhere else to read it.
Each chart declares its family in a `{# unit: … #}` header:

| family | kinds | where the unit lives |
|---|---|---|
| `required` | sankey, pie, funnel, gauge, price-history, distribution | the subtext — a ribbon or a slice is a bare number |
| `axis` | bar, line, area, the stacked forms, waterfall | the axis name (`y_name`) |
| `multi` | scatter | per axis — two measures, two units |
| `none` | correlation matrix, 100% stacked, drawdown, radar | nothing; the scale is fixed by construction |

### `builder.py check` gained a chart audit

Structural rules rendering cannot catch: every chart declares a known family
and satisfies it, and none sets its own title. For a `required` kind the
**showcase demo** must also state a unit — the showcase is the reference
example, and a demo that omits one teaches every copy to omit it.

### Bar width

`stacked_normalized` derives its `barMaxWidth` from the widest label it is
about to draw, rather than taking the theme's 44px cap that is right for bars
read by length but not for a column read by the text inside it. Its share
labels also round to one decimal — `52.4779` inside a bar is noise around the
one digit that matters.

---

## 4.0.0 — 2026-07-23

**Major.** Four markup contract changes, and the tree reorganised so its layout
states what each part is for. Documents pinned to `@3.x` are unaffected; a
document upgrades by editing its two head links, and will need the migration
notes at the end of this entry.

### The cover carries only the type and the title

`metadata_header(type_name, title)` — the `<dl>` of **Author / Date / Version**
and the **organization line** above it are gone.

Those four facts were composed into every document whether or not they meant
anything: the author was whatever `git config user.name` returned, the date was
the day the *skeleton* was generated rather than the day the content was
written, the version sat at `0.1` unless someone remembered to bump it, and the
organization line said the same thing on every page of every project. A fact
nobody maintains is worse than an absent one, because a reader trusts it.

A document that genuinely tracks revisions uses [[change-history]], which is
dated per row. A document that must state its owner or reviewers adds a `<dl>`
by hand — the CSS still styles it; see `components/foundational/structure/metadata-header/usage.md`.

Removing them made three mechanisms dead, so they went too: `git_user()` in
`builder.py` (with its `subprocess` and `datetime` imports), `--brand-name`,
and the whole body-class machinery.

### `presentation` removed

The doc-type, `presentation.css`, and the `page` component. It was the only
user of `{# body-class: … #}`, so `BODY_CLASS_RE`, the `body_class` render
context and the conditional in `base.html.j2` went with it.

**74 doc-types, 116 components.**

### Domain CSS is namespaced

Every class in `domain-specific/` now starts with its domain:
`.bridge-bar` → `.investing-bridge-bar`, `.swot` → `.business-swot`. 310 class
names across 51 files. Markup now says which domain owns a rule, and the two
domains cannot reach into each other's names.

Two classes failed the prefix test and moved to `foundational/` instead, which
is the more useful result:

- **`.badge`** → `foundational/blocks.css`. business.css's own comment called it
  "a generic status/rating pill", and three investing components used it.
- **`.neg`** → `foundational/content.css`. It was the system's only genuine
  collision — both domain modules defined it — and "this number is negative" is
  arithmetic, not a domain concept. It is hand-written in doc-type markup across
  accounting, finance and general documents.

Where a class name arrives as a **macro argument** — `financial_table` takes
rows of `("subtotal", …)` from 11 doc-types — the macro adds the prefix, so
authoring keeps its plain vocabulary and only the emitted markup changes.

### `css/` and `components/` are grouped by scope

Both trees use the same five groups, so a component and the CSS that styles it
sit in matching places:

| group | what it means |
|---|---|
| `foundational/` | any document may use it; nothing here knows a domain |
| `domain-specific/` | one domain owns it; its classes carry that domain's name |
| `math/` · `diagrams/` · `charts/` | rendering subsystems, each with a lazy CDN engine |

The last three are separate because each carries its own engine (KaTeX, Mermaid,
ECharts) and a document using none of them downloads none of them.

### One colour file

`css/foundational/theme.css` holds **every colour in the system** as `:root`
custom properties — surfaces, semantic tones, the syntax palette, the data ramps
and the chart palette. `base.css` keeps typography and spacing and no colour at
all; `brand.css` is gone, its one token folded in as `--accent`.

Retheming and rebranding are now the same act: edit that one file. **No other
module may hardcode a colour** — verified, and the check is in
`css/REFERENCE.md`.

Charts follow it: `js/modules/charts.js` reads `--chart-palette-N`,
`--chart-ramp-N` and `--chart-*` with `getComputedStyle` at load instead of
carrying its own hex, so a retheme reaches every existing chart.

### No print stylesheet

`print.css` is deleted. Ctrl+P uses the browser's own defaults — paper size,
margins and pagination come from the print dialog. What remains is the
`@media print` block each module keeps for itself: the floating toolbar hides,
diagrams freeze to static fully-visible images, columns collapse to one. Those
stop screen-only UI reaching paper; they impose no layout.

### `builder.py`: one check, less machinery

**Added `builder.py check`** — the skill's only automated guard. It parses every
component template and composes every doc-type and showcase, failing on a
surviving `{% … %}` (never on `{{ … }}`, which is the placeholder a skeleton is
*supposed* to carry). 116 components in about two seconds. It exists because
these failures are silent: a malformed chart spec renders as a code box
indistinguishable from an unreachable CDN.

**Removed** `lib/` entirely — `dataviz.py` and `chartkit.py`. The sixteen chart
components that delegated to `chartkit` now build their own ECharts option in
their own template, like the five that always did; every rendered spec was
diffed against the old output and is byte-identical. `builder.py charts` and
`builder.py dataviz` are gone with them. `SKILL.md`'s "Commands" section is
split into **CLI** (the five real subcommands) and **Procedures** (what you
carry out) — there is no `builder.py modify`, `release` or `audit`.

### Migrating a 3.x document

1. Point both head links at `@4.0.0`.
2. Delete the `<dl>` of Author/Date/Version from `<header class="doc-meta">`,
   or keep it and edit the values to something true.
3. If the document uses investing or business components, prefix their classes
   (`bridge-` → `investing-bridge-`, `swot` → `business-swot`); leave `badge`
   and `neg` alone.
4. A presentation has no 4.x equivalent — keep it pinned to `@3.4.0`.

Or simply leave it pinned. `@3.4.0` is immutable and keeps working.

---

## 3.4.0 — 2026-07-22

Additive. The `investment-thesis` doc-type finally composes from the investing
components it was built for, and the investing catalogue is cut to that one
type.

### `investment-thesis` composes a real thesis

It used only generic components — `prose`, `facts`, `financial_table`,
`callout` — so `builder.py new investment-thesis` handed you a generic business
document and the forty-five investing components stayed invisible unless you
knew to write the macro call yourself. It now instantiates nine:

| section | components |
|---|---|
| Summary | `security_header` · `recommendation` |
| Thesis | `thesis_pillars` |
| Valuation | `valuation_multiples` · `valuation_range` |
| Scenarios | `scenarios` · `expected_value` |
| Catalysts | `catalyst_timeline` |
| Risks | `risk_metrics` |

The skeleton deliberately stops at what a thesis is **dishonest without** — the
call, the claims, the price, the odds, the risks. Anything more is a document
you spend the first ten minutes deleting. `dcf_summary`, `five_forces`,
`peer_comparison`, `footnote_disclosures`, `bridge` and the rest are listed in
the doc-type's `usage.md` under *when the argument needs them*, so they are
discoverable without being imposed.

Two of the instantiated components carry arithmetic nothing validates:
`expected_value` probabilities must sum to 100%, and `valuation_range` bars must
share one `scale_min`/`scale_max` — a football field drawn on mixed scales
compares nothing. Both are called out in the usage.md.

### `risk_metrics` gained `subject_label`

The subject column was hardcoded to "Strategy" while the benchmark column was
parameterised. That asymmetry read wrongly the first time the component was used
in a single-stock thesis, where the column is a ticker. Default is unchanged, so
nothing that already calls it is affected.

### investing holds one doc-type

The other nine — backtest-report, due-diligence-report, earnings-note,
investment-policy-statement, market-outlook, portfolio-review,
strategy-specification, trade-journal, watchlist — are removed. Doc-types go
84 → 75.

Removing them meant editing eight files that referenced them by name
(`doc-types/REFERENCE.md`, `README.md`, the category blurb, and five cross
references in other usage.md files). A document type that no longer exists but
is still advertised is worse than one that was never there.

---

## 3.3.0 — 2026-07-22

Additive: sixteen new chart kinds, taking the catalogue to **117 components and
21 chart forms**. No markup contract change — existing documents are untouched
and need no re-composing.

### New — the common chart forms, as macros

Every form now has a macro rather than requiring a hand-written spec:

| over time | across categories | relationships |
|---|---|---|
| `c.line` | `c.bar` | `c.scatter` |
| `c.smoothed_line` | `c.stacked_column` | `c.radar` |
| `c.area` | `c.stacked_horizontal_bar` | `c.gauge` |
| `c.stacked_line` | `c.stacked_normalized` | |
| `c.stacked_area` | `c.bar_negative` | |
| | `c.waterfall` | |
| | `c.pie` | |
| | `c.funnel_chart` | |

Four of them compute something the author would otherwise redo by hand:

- **`waterfall`** — ECharts has no waterfall series; it is a transparent
  placeholder stack whose heights are running cumulative totals. Getting the
  placeholder wrong still draws a chart, which is exactly why this is not left
  to the call site.
- **`stacked_normalized`** — each value as a share of its column total. Pass raw
  amounts.
- **`bar_negative`** — bars coloured by the SIGN of the value, using the
  semantic direction tones. Colour is never the only cue: the bar's side of the
  zero line says the same thing.
- **`radar`** — per-indicator maxima derived from the data unless given, because
  ad-hoc per-axis maxima let a radar draw any shape you like.

`funnel_chart` carries the suffix because `funnel` is already the CSS component
in `investing`, and component names are unique across every category.

### Honest caveats, written into the components

`components/charts/usage.md` now lists a **CSS twin** for five of these —
`waterfall`/[[bridge]], `funnel-chart`/[[funnel]], `gauge`/[[meter]],
`radar`/[[scorecard]], `pie`/[[exposure-bars]]. The twin needs no engine, prints
cleanly, and keeps its numbers as selectable text; prefer it when the figures are
meant to be read rather than compared by eye.

`gauge`'s own usage.md opens by arguing against itself: a gauge spends a great
deal of ink on one number, and the design system's rule is that a single
headline number is a `kpi-tiles` tile. It earns its place only when the RANGE
matters as much as the value. It ships with no coloured danger bands —
deliberately, since banding the arc adds a judgement the number does not carry.

### Structure

- **`lib/`** — `chartkit.py` (the option builders; eleven of the kinds are one
  function plus flags) and `dataviz.py` moved here. `builder.py` stays at the
  root because it is the command you type. The boundary: templates hold markup,
  `lib/` holds computation, and `components/` stays a tree the builder can walk
  without special cases.
- **`components/charts/_render.html.j2`** — the tail every chart component
  shares, so the engine is named in one place for the whole family rather than
  once per kind. The `_` prefix marks a template the builder does not discover;
  the convention is now documented in `components/REFERENCE.md`.

`python builder.py charts` covers all 21 kinds from their `{# sample: … #}`
headers — 45 specs checked for valid JSON and the relief rule.

---

## 3.2.0 — 2026-07-22

Additive: two more chart kinds, and the relief rule becomes enforceable instead
of merely documented. No markup contract change.

### New — two chart presets

- **`c.return_distribution(series, …)`** — a box plot built from **raw
  observations**. Quartiles (type-7 interpolation) and **Tukey whiskers**
  (1.5 × IQR) are derived at compose time by a new `boxstats` filter, so the
  rendered spec carries the numbers and a reader can check them. Points beyond
  the fences are drawn as **outliers rather than absorbed into the whisker** —
  an outlier quietly extending a whisker is how a fat tail disappears from a
  chart, and that is the reason this is a component rather than a recipe.
- **`c.correlation_matrix(labels, matrix, …)`** — pairwise relationships on the
  sequential `RAMP`. The categorical palette would imply unrelated categories,
  and ECharts' stock blue-to-red `visualMap` reads as good-to-bad on a number
  carrying no such judgement: a −0.8 correlation is not "bad", it is the point
  of a diversifier. Values are printed as well as coloured.

`risk-return` deliberately stays a **recipe** — its spec is already as short and
readable as the data it carries, so a macro would hide the chart without
simplifying it. The test a preset must pass is unchanged: compute something,
enforce a rule, or prevent a known mistake.

### New — the relief rule is checked

`python builder.py charts` now validates two things about every chart spec, the
presets' and the showcase's alike: that it is valid JSON, and that it satisfies
the dataviz **relief rule** — more than three automatically-coloured series
reaches a palette slot below 3:1 on the chart surface, so it needs visible data
labels rather than colour alone.

Only **automatic** colours count. A series or item that sets its own colour is
not drawing from the rotating palette, which is why a fifteen-node role-coloured
sankey passes and a four-series bar chart does not. Pie, funnel and treemap
label by default, so for those the violation is switching labels *off*.

### `c.sankey` gained layout control

`label_room` (default 150) reserves right margin for terminal nodes, whose
labels sit outside the node and otherwise clip. Node width, gap, alignment and a
white label text-border are now sensible defaults rather than something every
call site re-specifies. This came out of migrating a real sixteen-node document,
which is the only way that gap was going to surface.

---

## 3.1.0 — 2026-07-22

Additive: the chart layer grows a checked colour system, three chart presets,
and two build-time checks. **No markup contract change** — a document's HTML is
byte-identical whichever version composed it, so nothing published needs
re-composing. Two things below are nevertheless worth reading before upgrading:
the palette changes colour, and two authoring macros are renamed.

### The categorical palette is replaced — charts will look different

The old palette's comments claimed it was "validated" and colourblind-safe. The
new `python builder.py dataviz` check proves it was not: slots 6 and 8 (orange
and red) collapsed to a CIEDE2000 distance of **4.8** under deuteranopia, and
only the first **three** slots were safe. Any chart with four or more series had
confusable colours.

It is now the **Okabe-Ito** reference set — the published standard for
categorical colour under colour vision deficiency — with pure black replaced by
the document's own ink (`#182338`), since a pure-black series reads as an axis.
Slots are ordered by contrast on the chart surface, because the early slots are
used most and must be the legible ones:

```
1 #0072b2 blue   2 #d55e00 vermillion  3 #009e73 bluish green  4 #cc79a7 purple
5 #56b4e9 sky    6 #e69f00 orange      7 #182338 ink           8 #f0e442 yellow
```

Worst pair is now **11.1** and it holds at every prefix length, so four series
are as safe as eight. Slots 4, 5, 6 and 8 sit below 3:1 and still need the
relief rule (data labels or a table view); slots 1-3 and 7 do not.

Upgrading a document changes its chart colours. That is the point, but it is
visible — check any chart whose colours were chosen around the old palette.

### Renamed authoring macros

Component names dropped a prefix that only repeated their category:

```jinja
c.chart_apache_echarts(...)   ->  c.apache_echarts(...)
c.diagram_mermaid(...)        ->  c.mermaid(...)
```

This is **not** a markup change — both emit exactly the markup they did before
(`pre.chart.apache-echarts`, `pre.mermaid`), and no composed document contains a
macro name. Only templates calling these macros need editing, and every
in-repo caller was updated. The JS/CSS module filenames keep their
`chart-`/`diagram-` prefix: that prefix is the engine convention, not a
category echo.

### New — colour system

- **`RAMP`**, a sequential light-to-dark scale for continuous encodings
  (heatmap, `visualMap`). The categorical palette implied categories where the
  data had an order, and ECharts' stock blue-to-red default read as good/bad.
- **`TOKENS.positive` / `.negative` / `.caution`** — semantic *direction* tones,
  the documented exception to "status colours are reserved". Direction is not
  identity: a candlestick's up/down, a flow's cost/retained. Never assign one to
  a series, and never as the sole cue — positive/negative fail deuteranopia
  separation by construction, so candlestick bodies are hollow/filled too.
- **`docsHtml.chart.resolveColors`** — a spec may now NAME a design colour
  instead of writing a hex: `"palette:1"`, `"token:positive"`, `"ramp:2"`. It
  lives in the shared layer, so every engine resolves the same references and no
  hex is ever forked into a document.

### New — theme coverage

`buildTheme()` styled only `line` and `bar`; everything else fell through to
ECharts' stock colours, which collide with the reserved status hues. It now
covers `pie`, `scatter`, `boxplot`, `candlestick`, `sankey`, `funnel`,
`heatmap`, `radar`, `graph`, plus `visualMap`, `dataZoom`, `markPoint` and
`markLine`.

### New — chart presets

Three macros that compute something, enforce a rule, or prevent a known mistake:

- **`c.sankey(nodes, links, …)`** — colours nodes by ROLE (`source` / `stage` /
  `cost` / `retained`), not by identity, so the colour count never depends on
  the node count. Left to itself ECharts cycles the palette and a fifteen-node
  flow gives two unrelated nodes the same hue.
- **`c.price_history(bars, …)`** — candlestick plus volume as two stacked grids
  sharing an axis pointer, never a dual y-axis (the charting mistake the rules
  already forbid). Takes OHLCV as a human reads it and reorders internally.
- **`c.drawdown_curve(series, …)`** — derives the running peak and each drawdown
  at compose time from a level series, so the document carries the input and the
  arithmetic is auditable.

`components/charts/usage.md` is now the **approved chart-kind catalogue** —
which kinds exist, which are presets and which are hand-written recipes
(`risk-return`, `return-distribution`), and why. Also new: `.chart-note`, the
one-line reading beneath a chart.

### New — two checks

- **`python builder.py dataviz`** — contrast on the chart surface, pairwise
  separation under protanopia / deuteranopia / tritanopia (CIEDE2000, floor
  10.0, calibrated just under Okabe-Ito's own 11.1), and monotonic ramp
  luminance. Fails the build on a confusable pair. Colour science lives in
  `dataviz.py`, out of the composer.
- **`python builder.py charts`** — renders every preset from a `{# sample: … #}`
  header and validates the emitted spec is JSON. This exists because the failure
  is silent by design: a malformed spec does not raise, the engine simply leaves
  the source visible as a code box, indistinguishable from an unreachable CDN.

Presets accordingly build a data structure and serialise it once rather than
hand-writing JSON, and delegate the markup to the engine macro. Both rules, and
the six steps for adding a chart kind, are in `js/REFERENCE.md`.

---

## 3.0.2 — 2026-07-22

Bug fix. No markup contract change — safe for every document; upgrade by
changing the version in the two hrefs. **Recommended for anyone whose readers
are not all on Chromium or Edge.**

- **Bar geometry now renders correctly in Firefox and Safari.** Fourteen
  components carry their geometry in `data-` attributes that CSS reads with
  typed `attr()` — `width: attr(data-pct type(<percentage>), 0%)`. That syntax
  is CSS Values 5 and today ships only in Chromium 133+. Elsewhere the engine
  cannot parse the declaration and **drops it whole**: the `0%` fallback is
  inside the syntax it could not parse, so `width` reverts to `auto` and the
  bar fills its track. Every bar rendered full width — a `bridge` showed
  `+13,031` and `+4,200` as the same size. Wrong data, not missing data.

  New `js/modules/attr-fallback.js` detects the gap once
  (`CSS.supports("width", "attr(...)")`) and, only where it exists, applies the
  same geometry as an inline style. Chromium never enters that path and its
  rendering is byte-for-byte unchanged.

  Affected: `blocks/meter`, and in `investing` — `aging-schedule`, `bridge`,
  `capital-allocation`, `debt-maturity`, `exposure-bars`, `funnel`,
  `holdings-table`, `ownership-table`, `quadrant-map`, `scorecard`,
  `segment-reporting`, `stress-test`, `valuation-range`.

  Verified in Firefox 153: typed `attr()` absent, all 79 geometry elements
  corrected, 89 of 90 rendered measurements within 2% of their declared
  percentage — the one outlier being `funnel-bar`'s deliberate `min-width:
  11rem` legibility floor, which behaves identically in Chromium.

- **Documentation corrected.** Nine `usage.md` files, `css/modules/blocks.css`
  and `css/modules/investing.css` claimed these components "degrade to an empty
  track" with the numbers staying readable. That was false in the dangerous
  direction — the tracks came out full, contradicting the numbers printed
  beside them. `SKILL.md`, `js/REFERENCE.md` and `css/REFERENCE.md` updated too.

The polyfill is deliberately deletable: when Firefox and Safari ship typed
`attr()`, remove the file and the line in `js/docs-html.js`. Nothing else
references it.

---

## 3.0.1 — 2026-07-22

Visual fix. No markup contract change — safe for every document; upgrade by
changing the version in the two hrefs.

- **`kpi-tiles` values are smaller**: `1.5rem` -> `1.25rem` (24px -> 20px), with
  line-height at `1.2`. They were reading as poster numbers rather than headline
  metrics; the weight (800) and tight tracking carry the emphasis instead of the
  size. A long value like `$1,001,000` now also fits one line in a 9rem tile.
- **Component gallery: more air between specimens.** `.gx-spec-head` gained a
  `2.5rem` top margin, so consecutive demos are separated by 40px instead of
  16px and it is obvious where one component ends and the next begins. A spec
  header directly after a category band keeps the tighter `1.2rem`, since the
  band already supplies its own space. This is page-local chrome in
  `showcases/components.html.j2`, not a shared module — documents download none
  of it.

---

## 3.0.0 — 2026-07-22

**Charts changed their markup hook, and gained a whole component category for
investing.** The breaking change is the first one; the second is purely
additive.

### Breaking — charts name their engine

`pre.chart` alone is no longer a recognised markup hook. A chart block now wears
two classes: `chart`, the marker every chart engine shares, and a second class
selecting the engine.

```html
<pre class="chart">…</pre>                   <!-- 2.x -->
<pre class="chart apache-echarts">…</pre>    <!-- 3.0 -->
```

The macro is renamed to match: `c.chart_echarts()` → `c.chart_apache_echarts()`.

Why: charts had no engine seam. Everything lived in one `chart.js` — the
validated categorical palette written directly into an **ECharts theme object**,
the card, the source fallback, `data-height`, the resize reflow — so a second
engine could not have reused the palette the dataviz method validated, and had
nowhere to hook. Diagrams solved this in 1.8.0 with a shared viewport plus one
engine file beside it; charts now use the same split.

- Added: `js/modules/charts.js` — the shared, engine-agnostic chart frame,
  `docsHtml.chart`. Owns `PALETTE` and `TOKENS` **as plain data in no engine's
  format**, `Frame` (card, canvas, `data-height`, source hiding, toolbar), one
  debounced resize dispatch for the whole page, and `markError`.
- Added: `js/modules/chart-apache-echarts.js` — the engine. Owns the pinned
  `echarts@5.5.1` CDN and *translates* the shared tokens into an ECharts theme.
- Renamed: CSS layer `chart` → `charts`. `css/modules/chart.css` becomes
  `charts.css` (frame, toolbar, and the `pre.chart` readable-source fallback —
  one definition for every engine) plus `chart-apache-echarts.css`.
- Moved: the component leaves `components/diagrams/` for a new twelfth category,
  `components/charts/`. A chart is data; a diagram is a drawn relationship.
- **New: a chart toolbar.** Every rendered chart now carries download-as-SVG and
  copy-source, top-right of the card — from the shared layer, so any future
  engine inherits them.
- Rebrand the dataviz palette in `js/modules/charts.js` now, not in the engine.

Adding a chart engine is documented in `js/REFERENCE.md` as the same five
mechanical steps as a diagram engine.

### Added — the `investing` component category (45 components)

An eleventh component category for documents that must support an allocation
decision: buy, hold, sell, size, or wait. Nothing in it is a prettier table —
each component encodes a rule its `usage.md` enforces.

- The security and the call: `security-header`, `recommendation`.
- Company analysis: `thesis-pillars` (claim + evidence + **falsifier**),
  `scorecard`, `metric-trend`, `valuation-multiples`, `peer-comparison`,
  `earnings-surprise`, `valuation-range` (football field), `catalyst-timeline`,
  `expected-value`.
- Statements: `income-statement`, `balance-sheet` (with an explicit
  assets = liabilities + equity check), `cash-flow-statement` (with the free
  cash flow derivation), `dcf-summary`, `segment-reporting` (revenue share vs
  profit share), `footnote-disclosures`. Statement lines cross-reference notes
  via `note=` → `id="note-N"`.
- Decomposition and valuation: `bridge` (waterfall, cumulative maths done at
  compose time), `sensitivity-table`, `roll-forward`, `dupont`,
  `capital-allocation`, `composite-score`, `debt-maturity`, `working-capital`.
- Portfolio and market: `holdings-table`, `performance-table`, `exposure-bars`,
  `risk-metrics`, `trade-log`, `attribution`, `drawdown-table`, `stress-test`.
- Economy and strategy: `macro-indicators`, `cycle-position`, `heatmap`,
  `five-forces`, `quadrant-map`, `funnel`, `cohort-table`, `unit-economics`,
  `ownership-table`, `variance-analysis`, `aging-schedule`, `covenant-table`.

**No new JavaScript.** Every bar width, bar offset and plot position is computed
at compose time and carried as a `data-` attribute read by CSS `attr()`, so the
authoring contract's ban on `style=` holds throughout; each component also
prints its own values, so nothing becomes unreadable without `attr()`.

`css/modules/investing.css` defines four shared skins rather than 45 bespoke
ones: `table.fin` (a marker class every numeric table opts into), `.statement`,
the labelled-bar figure row, and the level-graded cell grid. It is layered after
`business` so `valuation-multiples` and `covenant-table` can reuse `.badge`.

**Migration.** Only charts need action. In each document, change
`<pre class="chart">` to `<pre class="chart apache-echarts">`; the JSON spec
inside is untouched, as is every other component. A document with no chart in it
upgrades to 3.0.0 by changing the version in its two hrefs, nothing else.

Documents already published against `@1.x` or `@2.x` need no action at all: each
pins an immutable tag and loads the assets of that tag, so it keeps its old
markup *and* the code that understands it. Verified against
`data-analysis-report-apple-income-fy2025.html` (pinned `@2.0.0`), which still
renders unchanged.

---

## 2.0.0 — 2026-07-21

**draw.io / diagrams.net support is removed.** `pre.drawio` is no longer a
recognised markup hook — this is the breaking change. Mermaid is now the only
diagram engine.

Why: draw.io diagrams are mxGraph XML with **no auto-layout** — every box needs
an explicit `x`/`y` and every connector a hand-picked exit/entry side and a
routed corridor. Authoring or editing one by hand (or by assistant) means
solving a layout problem before saying anything about the system, and the
results collide and overlap as soon as the diagram changes. Mermaid's dagre
layout removes that entire class of work: you write relationships, it places
them. The 3.6 MB diagrams.net bundle goes with it.

- Removed: `js/modules/diagram-drawio.js`, `css/modules/diagram-drawio.css`,
  `components/diagrams/diagram-drawio/` (`c.diagram_drawio()`), and the pinned
  `jgraph/drawio@24.7.17` CDN dependency.
- **Unchanged: everything else.** `pre.mermaid`, `pre.chart`, and every other
  component keep their exact markup. A document that has no `pre.drawio` in it
  upgrades to 2.0.0 by changing the version in its two hrefs, nothing else.
- **The multi-engine architecture stays** — deliberately. `diagrams.js` remains
  the shared, engine-agnostic viewport and `diagram-mermaid.js` remains *one*
  engine beside it, not merged into it. Adding a future engine is still a new
  `diagram-<name>.js` + `diagram-<name>.css` + two list entries and touches no
  existing code; `js/REFERENCE.md` documents the five steps.

**Migration.** Replace each `<pre class="drawio">` with a `<pre class="mermaid">`
holding the equivalent `flowchart` — nodes become ids with shapes
(`[box]`, `([stadium])`, `{diamond}`, `[(store)]`), connectors become
`a --> b` / `a -. label .-> b`, draw.io groups become `subgraph`, and fill/stroke
colours become `classDef` + `class`. Drop every coordinate.

---

## 1.8.0 — 2026-07-21

Diagram subsystem split into shared core + per-engine files. No authored-markup
change (`pre.mermaid` / `pre.drawio` are unchanged), so documents are unaffected.

- JS: `diagrams.js` is now the **engine-agnostic viewport** (`docsHtml.diagram.Viewer`
  — bounded box, pan/zoom, toolbar, fit/reset/fullscreen/download/copy, resize
  grip); `diagram-mermaid.js` and `diagram-drawio.js` only turn source into an
  `<svg>` and hand it over. Mermaid keeps the ✎ editor as its one engine tool.
- CSS: `diagrams.css` (shared chrome) + `diagram-mermaid.css` + `diagram-drawio.css`.
  Runtime classes renamed to neutral `.diagram-figure` / `.diagram-canvas` /
  `.diagram-tools` / `.diagram-resize`.
- draw.io gains the **reset-to-100%** button it was missing, and both engines now
  share one identical toolbar.
- `@panzoom` is gone: pan/zoom is self-contained for both engines (the
  diagrams.net bundle ships a global `Panzoom` that clobbered it).

---

## 1.7.0 — 2026-07-21

- `diagram-drawio` now renders into the same bounded viewport as Mermaid, with
  the on-brand toolbar (zoom % · fit · fullscreen · download SVG · copy XML,
  drag to pan, Ctrl+wheel to zoom) instead of the diagrams.net chrome. The SVG
  carries a `viewBox`, so 100% **fits the column width** with proportional
  height. Pan/zoom is self-contained — the diagrams.net bundle ships a global
  `Panzoom` that clobbered `@panzoom`, so draw.io no longer loads it.

---

## 1.6.0 — 2026-07-20

- New `drawio` feature + `diagram-drawio` component: freeform draw.io /
  diagrams.net diagrams authored as mxGraph XML (`c.diagram_drawio()`,
  `pre.drawio`), rendered to SVG at view time by the pinned diagrams.net viewer
  (`jgraph/drawio@24.7.17`, lazy). For architecture/network/infra with explicit
  layout — complements Mermaid (auto-laid-out). Styled by `diagrams.css`;
  degrades to the XML source if the viewer CDN is unreachable. Additive.

---

## 1.5.0 — 2026-07-20

- New `layout/width` component: wrap any component to give it a fixed width
  (`w`, default `24rem`) with optional `align` (left/center/right). Caps width,
  never overflows. Additive.

---

## 1.4.0 — 2026-07-20

Layout primitives. Additive — existing documents keep working unchanged.

- New `layout` component category (the 10th) with four composable primitives,
  styled by new `css/layout.css` (layer `layout`):
  - `columns` + `column` — a responsive side-by-side row; `column(span=N)` for
    asymmetric splits. Wraps/stacks when narrow.
  - `grid` — an auto-fit grid of equal tiles (`min` sets the smallest tile).
  - `card` — a titled, bordered surface; the natural cell for grid/columns, or
    standalone.
- The single-column reading model is preserved: every layout **collapses to one
  column on narrow screens and in print** (`break-inside: avoid` on cells), so
  layout is an enhancement, never a dependency.
- Showcase gains a Layout band (now ten category bands); `CATALOG.md`
  regenerated.

---

## 1.3.0 — 2026-07-20

Declarative charts. Additive — existing documents keep working unchanged.

- New `chart` feature: `<pre class="chart">` holding a JSON ECharts `option`,
  rendered to **SVG** at view time by Apache ECharts `5.5.1` (lazy, pinned CDN).
  Component `chart-echarts` (`c.chart_echarts()`), styled by new `css/chart.css`
  (layer `chart`). Covers bar/line/area/pie/scatter/heatmap/candlestick — real
  analytical charts, not just Mermaid's `xychart-beta` illustrations.
- Built-in validated `docs-html` theme: the 8-slot categorical palette (fixed
  order, colorblind-checked against the light surface via the dataviz method),
  ink/axis/grid from the base tokens. Never restyle per chart — rebrand once in
  `js/modules/chart.js`.
- Accessible by default: `aria`, hover tooltip, and a legend for ≥ 2 series are
  auto-filled when the author leaves them unset; one y-axis only (documented).
- Degradation: invalid JSON or an unreachable CDN leaves the spec visible as a
  readable code box — nothing breaks.

---

## 1.2.1 — 2026-07-20

Visual patch — no markup change, safe for every document.

- `kpi-tiles`: smaller headline number (`.kpi-value` 2rem → 1.5rem) so tiles
  read as metrics, not banners.

Tooling (unversioned assets, noted for the record): every generated file now
links the version-pinned CDN — the showcase joined documents in dropping local
refs, so all output is shareable as-is; a missing `cdn` in `version.json` is now
a hard error.

---

## 1.2.0 — 2026-07-20

Catalog completion, generated reference, and internal reorganization. Additive —
existing documents keep working unchanged.

- Catalog grows 59 → 84 doc-types; components reorganized into nine category
  folders (structure, content, lists, callouts, blocks, business,
  front-back-matter, diagrams, math). New components: comparison-table, quote,
  meter, risk-matrix, party-block, footnotes.
- New generated `CATALOG.md` (every component call form + doc-type purpose,
  built from source via `builder.py catalog`), backed by a required
  `{# purpose: … #}` header on every template. `builder.py show <name>` prints
  one item's signature/purpose + usage.md.
- Category/domain `usage.md` blurbs are the single source feeding both
  `CATALOG.md` and the showcase category bands.
- Showcase rebuilt as a category-driven gallery and moved to
  `showcases/components.html` (the builder discovers `showcases/*.html.j2`).
- Page-local CSS via a `{% block head %}` hook; showcase-only chrome left the
  shared stylesheet (`gallery.css` removed).
- Docs restructured: a per-subsystem `REFERENCE.md` (css, js, components,
  doc-types) and a "Documentation map"; SKILL.md slimmed to point at them; every
  per-item `usage.md` opens with a role line.

---

## 1.1.0 — 2026-07-19

Multi-domain expansion + CDN-only documents.

- Catalog grows 38 → 59 doc-types across ten domain folders
  (`doc-types/<domain>/<name>/`): general, software, finance, investing,
  accounting, research, economics, engineering, tools, fallback; the builder
  discovers recursively and `--list` groups by domain.
- New components: financial-table, journal-entry, scenarios, pros-cons,
  swot-grid, badge (`business.css`) and formula (`math.css`).
- New `math` feature: LaTeX rendered at view time by KaTeX 0.16.11 (lazy CDN);
  formulas are LaTeX text, never images.
- Charts documented: mermaid `xychart-beta` / `pie` through the standard
  diagram viewport.
- MINOR head-generation change: composed documents now carry version-pinned
  CDN hrefs ONLY (no local paths, no onerror fallback) — fully portable;
  the gallery keeps local refs. Existing documents keep working unchanged.

---

## 1.0.0 — 2026-07-19

First versioned release of the two-asset, single-include design system.

- One stylesheet: `css/docs-html.css` (`@layer` + `@import` of `css/modules/`),
  one script: `js/docs-html.js` (loader for `js/modules/`: core registry, util,
  icons, layout-toggle, highlight, diagrams, main).
- Layout invariants: single `<main>` column, components flush-left,
  `--block-gap` external spacing.
- Diagrams: Mermaid at natural size in a bounded viewport — pan/zoom
  (Panzoom), icon toolbar with live zoom-%, fit, fullscreen, download SVG,
  copy source; vertical resize grip; ✎ source editor as a resizable side
  panel with live re-render and Prism-colored overlay.
- Code: documents hold plain text + `data-lang`; view-time coloring (Prism,
  lazy) with the palette in `code.css`.
