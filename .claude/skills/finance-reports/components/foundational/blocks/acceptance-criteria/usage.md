# acceptance-criteria

_Authoring guidance for the `acceptance-criteria` component — when to use it, how, and the rules._

A Given / When / Then scenario block — the checkable pass/fail conditions for a
user story, use case, or test case. Styled by: `css/foundational/blocks.css`
(`.acceptance`, `.gwt`). Pairs with [[requirement]] cards and the [[steps]]
main-flow list.

## Markup

```jinja
{{ c.acceptance_criteria(id="AC-014", title="Wrong password is rejected",
    given=["a registered user", "the account is not locked"],
    when=["they submit an incorrect password"],
    then=["the login is refused", "the failed-attempt counter increments"]) }}
```

## Rules

- **Clauses are observable and checkable** — a state or an action, never prose
  reasoning. If you cannot test it, it is not acceptance criteria.
- **`given`, `when` and `then` are each a list of clause strings.** The first
  clause in each list is labelled with the keyword; every following clause is
  rendered as an "and", so multi-condition steps read naturally without you
  writing the conjunction.
- **Give each scenario an `AC-` id**, and where it realises a requirement or
  story, trace it to that id in the surrounding text (see [[trace-id]]).
- **One scenario per block.** A `when` list describing two different actions is
  two scenarios sharing an id, and the id is what a failure gets reported
  against.
