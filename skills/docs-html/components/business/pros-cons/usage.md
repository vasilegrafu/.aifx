# pros-cons

_Authoring guidance for the `pros-cons` component — when to use it, how, and the rules._

Styled by: `css/modules/business.css`

A two-column weighing block: Pros (green edge) beside Cons (red edge). For
due-diligence, option comparisons, decision sections in any domain.

`{{ c.pros_cons(pros=["...", "..."], cons=["...", "..."]) }}`

Rules: comparable granularity on both sides; a decision follows the block
(callout `decision` or a decision-record) — the block itself never concludes.
