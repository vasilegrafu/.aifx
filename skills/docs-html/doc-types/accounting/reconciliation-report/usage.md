# reconciliation-report

_Authoring guidance for the `reconciliation-report` document type — audience, depth, and rules._

- Audience: whoever must trust the books — the periodic proof that internal
  records match the bank/broker (IBKR statements included).
- Filename: `docs/reconciliation-report-<account>-<period>.html`.
- Depth: none.
- Rules: the two adjusted balances MUST meet — an unreconciled difference is
  named, sized, and owned, never absorbed; every difference gets a cause
  (timing vs error — errors get a correcting journal-entry); done on a fixed
  cadence, not when suspicion strikes.
