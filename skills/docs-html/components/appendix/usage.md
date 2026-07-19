# appendix

Back-matter appendix section, auto-lettered "Appendix A." etc. Macro:
`appendix(id, heading)` — a `{% call %}` container wrapping the appendix body.
It emits only the `<section class="appendix">`; the lettering counter lives on
the [[appendices]] wrapper, so appendix calls MUST sit inside one
`{% call c.appendices() %}` block (share the wrapper, or they all reset to A).
