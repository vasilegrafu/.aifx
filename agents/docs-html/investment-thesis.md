---
name: investment-thesis
description: Research a listed company and produce an investment-thesis document from live market data. Use when the user asks for a thesis, a research pack, or an analysis of a specific ticker.
---

You produce one artifact: an `investment-thesis` document, composed from the
docs-html design system and filled with data you actually fetched.

The document's **shape is not yours to invent**. `builder.py` composes it and
the doc-type's `usage.md` states its rules. Your job is the half a template
cannot do — gather the material, read it, and write it up.

## Procedure

**1. Compose the skeleton first.** Never hand-write the structure.

```bash
cd <skill>/            # .claude/skills/docs-html
python builder.py new investment-thesis "<TICKER> — <Company name>" \
       --docs <project>/docs/stocks/<TICKER>
```

**2. Read `doc-types/investing/investment-thesis/usage.md`.** Its rules bind
you. So does `python builder.py show <component>` for any component you touch.

**3. Gather.** For a US-listed name this is the set that works — every one of
these fed the reference document:

| what | call |
|---|---|
| identity, sector, beta, employees | `company` → `profile-symbol` |
| price, market cap, 52-week range, moving averages | `quote` → `quote` |
| revenue/margins/EPS history | `statements` → `income-statement`, annual, limit 4 |
| current multiples | `statements` → `metrics-ratios-ttm` |
| the company's own multiple history | `statements` → `metrics-ratios`, annual, limit 5 |
| peer multiples on the same basis | `metrics-ratios-ttm` for each real comparable |
| targets, ratings | `analyst` → `price-target-consensus`, `ratings-snapshot` |
| forward estimates | `analyst` → `financial-estimates`, annual, limit 8 |
| the one dated catalyst | `calendar` → `earnings-company` |

Choose comparables yourself. A peers endpoint will return names that share an
index rather than a business — check each one is actually comparable before it
enters a table.

**4. Fill every factual section.** Then verify no `{{` remains in the output,
and open the file in a browser to confirm it renders.

## Rules

**Every number traces to a call you made in this session.** If you did not fetch
it, it does not go in the document. No recalled figures, no "approximately",
no filling a gap because the table looks unfinished. Close with a Sources
paragraph naming the provider, the retrieval date and the endpoints used.

**You do not make the call.** Leave the rating, the price target, the scenario
probabilities and the position size EMPTY, and say why in the Decision section.
Assembling evidence and issuing investment advice are different jobs; you are
not a licensed adviser and must not disguise one as the other. Where the
structure demands a judgement, substitute **sourced fact** and label it:

- `recommendation` → analyst consensus, explicitly attributed
- `scenarios` → published high / consensus / low targets, with **no
  probabilities attached**
- omit `expected_value` entirely — its weights are pure judgement

**State what cuts against the thesis.** If the multiple is stretched, the
margins trail the peer, or the price sits above the consensus target, that goes
in the summary, not a footnote. A pack that only marshals supporting evidence is
worthless to the person who has to decide.

**Every pillar needs a real falsifier** — an observation checkable against the
next filing. "Execution risk" is not a falsifier; "FY2026 revenue below the
$50.09B consensus" is.

## Traps that have already caught someone

- **GAAP vs non-GAAP.** Analyst EPS estimates are non-GAAP; reported EPS is
  GAAP, and they differ materially. Never compute a forward P/E from one and
  compare it to a trailing P/E from the other without saying so in the document.
- **`expected_value` probabilities must sum to 100%.** Nothing checks this.
- **`valuation_range` bars must share one `scale_min`/`scale_max`.** A football
  field drawn on mixed scales compares nothing. Nothing checks this either.
- **A loss-making peer has no meaningful P/E.** Say so rather than printing a
  negative multiple.
- **Compare a multiple against the company's own history, not just the peer.**
  The peer comparison and the own-history comparison often point opposite ways,
  and that divergence is usually the most interesting line in the document.
