# api-specification

_Authoring guidance for the `api-specification` document type — audience, depth, and rules._

The contract for an API: conventions, endpoints, request/response shapes,
error codes. Reference-grade — a consumer builds against it without reading
the source.

- Audience: API consumers and maintainers. Altitude: precise contract.
- Filename: `docs/api-specification-<api>.html`
- Template: `document.html.j2` (in this folder)
- Depth: `ask` — full means reading the real routes/handlers/models.

## Research guidance
- Real endpoints, methods, paths, auth, status codes from the code.
- Real request/response bodies — use actual field names and types.

## Rules
- Every endpoint: method + path, purpose, params, request body, responses
  (per status code). One collapsible or subsection per endpoint.
- Request/response bodies use the framed [[code-block]] (JSON) with tokens.
- State conventions once (auth, versioning, error envelope, pagination) and
  do not repeat them per endpoint.
- Error responses are documented, not just success paths.
