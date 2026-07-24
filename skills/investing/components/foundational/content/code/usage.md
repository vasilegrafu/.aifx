# code

_Authoring guidance for the `code` component — when to use it, how, and the rules._

A plain (unframed) code block. Macro: `code(lang="")` — a `{% call %}`
container whose body is the literal code, plain text. Pass `lang=` to set
`data-lang` and get view-time syntax coloring (see `code-block/usage.md`).
For a titled block with a language label in a title bar, use `code-block`.
