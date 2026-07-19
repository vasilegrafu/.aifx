# front-back-matter

Styled by: `css/blocks.css` (executive-summary lead, references, appendices).

Guidance-only component: there is NO `component.html.j2` here. Front/back
matter is a pattern composed from existing components — [[facts]],
[[approval-block]], [[references]], [[glossary]], [[appendix]] — plus normal
sections. The example(s) below are filled illustrations.

The formal scaffolding ISO/IEEE-style documents carry around the body:
front matter before the first content section, back matter after the last.

## Front matter (in order, after the metadata-header)
1. **Purpose & Scope** — a normal `<section>`: what the document covers and,
   explicitly, what it does not.
2. **Executive summary** — a `<section>` whose opening paragraph is the
   `.lead` (larger) so a busy reader gets the outcome in one glance:
   ```html
   <section id="executive-summary">
     <h2>Executive summary</h2>
     <p class="lead">v2 splits the portfolio app into webapi and webapp;
        v1 stays read-only through 2026-Q4. No data migration is required.</p>
   </section>
   ```
3. **Document control** — optional: a [[facts]] block (owner, review cycle,
   distribution) and/or the [[approval-block]] for sign-off documents.

## Back matter (after the last content section)
1. **References** — numbered, anchorable, hanging-indent `[n]`:
   ```html
   <section id="references">
     <h2>References</h2>
     <ol class="references">
       <li id="ref-29148">ISO/IEC/IEEE 29148:2018, Requirements engineering.</li>
       <li id="ref-adr">Nygard, M. <em>Documenting Architecture Decisions</em>, 2011.</li>
     </ol>
   </section>
   ```
   Cite in the body as `<a href="#ref-29148">[1]</a>`.
2. **Glossary** — the [[glossary]] section (`dl.glossary`).
3. **Appendices** — wrapped so lettering is isolated from body numbering:
   ```html
   <div class="appendices">
     <section class="appendix" id="appendix-schema">
       <h2>Data model</h2>   <!-- renders "Appendix A. Data model" -->
       …
     </section>
   </div>
   ```

## Rules
- Add front/back matter only to formal documents (SRS, architecture,
  standards, test plans). A status report or meeting-minutes does not need
  it — do not pad short documents with empty scaffolding.
- Every front/back-matter section it contains goes in the TOC, in order.
- References are numbered by CSS — never hand-number them in the markup.
