# test-summary-report

What the testing found: results, coverage, defects, and a pass/fail
assessment for a release decision. Signed off.

- Audience: release decision-makers, QA leads. Altitude: verdict + evidence.
- Filename: `docs/test-summary-report-<release>.html`
- Template: `document.html.j2` (in this folder)
- Depth: `full` (report actual results — numbers come from the test run).

## Rules
- Headline numbers up top ([[kpi-tiles]]): executed, passed, failed, blocked.
- The assessment is an explicit go / no-go with justification, not a shrug.
- Open defects link to defect-report ids; do not restate them.
- Ends with the [[approval-block]] for sign-off.
