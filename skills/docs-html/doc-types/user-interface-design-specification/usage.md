# user-interface-design-specification

How the UI looks and behaves: principles, screens, components, interaction
flows, accessibility.

- Audience: designers, front-end engineers, product. Altitude: interface
  behaviour, not visual pixel-perfection.
- Filename: `docs/user-interface-design-specification-<app>.html`
- Template: `document.html.j2` (in this folder)
- Depth: `ask` — full means reviewing real screens/mockups.

## Rules
- Screens documented with a [[figure]] (mockup/screenshot) + a caption; every
  image has meaningful alt text.
- Interaction flows use a Mermaid `flowchart` (screen-to-screen navigation).
- Accessibility is a first-class section, not an afterthought — state target
  (e.g. WCAG 2.1 AA) and how it is met.
- Reusable UI components are listed once; screens reference them.
