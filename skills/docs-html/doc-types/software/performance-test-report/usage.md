# performance-test-report

_Authoring guidance for the `performance-test-report` document type — audience, depth, and rules._

- Audience: whoever decides the system is ready for its load.
- Filename: `docs/performance-test-report-<system>-<date>.html`.
- Depth: none — written from real test runs.
- Rules: the setup section makes the run reproducible (versions, hardware,
  workload); results compare against pre-declared targets, never post-hoc
  ones; charts via mermaid xychart with the data in the document; anomalies
  are explained or listed as open questions — never smoothed away.
