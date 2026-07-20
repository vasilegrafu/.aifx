# formula

_Authoring guidance for the `formula` component — when to use it, how, and the rules._

Styled by: `css/modules/math.css` (+ KaTeX's own stylesheet at view time)

A display formula: LaTeX source as plain text, rendered in the browser by
KaTeX (loaded lazily from CDN by `docs-html.js`). Inline math inside prose is
hand-written: `<span class="math">E = mc^2</span>`.

```jinja
{% call c.formula() %}{% raw %}d_1 = \frac{\ln(S/K) + (r + \sigma^2/2)\,t}{\sigma\sqrt{t}}{% endraw %}{% endcall %}
```

Rules:
- The document holds LaTeX TEXT — never images of equations (same principle
  as diagrams). If the CDN is unreachable the source stays visible in mono.
- Escape HTML specials in the TeX when hand-editing: `<` → `&lt;`, `>` →
  `&gt;`, `&` → `&amp;` (rare in math, but real).
- In Jinja templates wrap the TeX in `{% raw %}…{% endraw %}` so braces are
  never parsed as template syntax.
- Invalid TeX renders as red text (KaTeX throwOnError:false) — fix it, don't
  ship it.
