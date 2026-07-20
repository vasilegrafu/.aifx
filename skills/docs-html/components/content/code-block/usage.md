# code-block

_Authoring guidance for the `code-block` component — when to use it, how, and the rules._

Styled by: `css/modules/content.css` (plain) + `css/modules/code.css` (frame + palette)

Markup skeleton: `component.html.j2` in this folder — the canonical source the
builder composes (parameters declared at its top). The example(s) below are
filled illustrations.
(framed block, title bar, runtime syntax coloring)

Source code, configuration, terminal output. Two forms. **Documents hold code
as PLAIN TEXT** — the language is declared with `data-lang`, and coloring
happens at view time in the browser (`docs-html.js` loads Prism lazily from
CDN; palette in `code.css`). No token markup is ever written into a document.

## Form 1 — plain (always valid, hand-editing friendly)
```html
<pre><code>def main():
    return limiter.acquire(partition)</code></pre>
```
Add `data-lang="python"` to the `<code>` to get coloring. Inline code inside
prose: plain `<code>…</code>`.

## Form 2 — framed, with title bar
The professional form for developer-facing documents. The frame is a
`<figure class="code">`; the `<figcaption>` is the title bar (file path left,
language label right); the macro's `lang=` fills both the label and `data-lang`:

```html
<figure class="code">
  <figcaption>database/session_maker.py <span class="lang">python</span></figcaption>
  <pre><code data-lang="python">def main():
    # acquire per-partition
    return limiter.acquire(partition)</code></pre>
</figure>
```

Macro form: `{% call c.code_block(path="database/session_maker.py", lang="python") %}…{% endcall %}`.

## Rules
- Escape `<`, `>`, `&` in code text.
- Code is plain text — never write token `<span>`s or `language-*` classes
  into a document. The runtime adds what it needs; if the CDN is unreachable
  the code simply renders plain, still fully readable.
- `data-lang` values are Prism language ids (`python`, `sql`, `json`, `bash`,
  `yaml`, `csharp`, …); grammars load on demand. Unknown ids degrade to plain.
- Code never goes inside a [[diagram-mermaid]] block or vice versa.
