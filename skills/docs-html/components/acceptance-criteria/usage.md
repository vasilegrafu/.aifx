# acceptance-criteria

A Given / When / Then scenario block — the checkable pass/fail conditions for a
user story, use case, or test case. Leaf macro:
`acceptance_criteria(id="AC-1", title="", given=[], when=[], then=[])`.

- `given`, `when`, `then` are each a list of clause strings. The first clause
  in each list is labelled with the keyword; every following clause is an
  "and", so multi-condition steps read naturally.
- Keep clauses **observable and checkable** — a state or an action, never prose
  reasoning. If you cannot test it, it is not acceptance criteria.
- Give each scenario an `AC-` id and, where it realises a requirement or story,
  trace it to that id in the surrounding text (see [[trace-id]]).

```jinja
{{ c.acceptance_criteria(id="AC-014", title="Wrong password is rejected",
    given=["a registered user", "the account is not locked"],
    when=["they submit an incorrect password"],
    then=["the login is refused", "the failed-attempt counter increments"]) }}
```

Styled by: `css/blocks.css` (`.acceptance`, `.gwt`). Pairs with
[[requirement]] cards and the [[steps]] main-flow list.
