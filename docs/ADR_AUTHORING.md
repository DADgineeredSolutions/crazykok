# ADR Authoring

Architecture decision records are canonical Markdown files in `docs/adr/`.
They are not application data and must never be copied into a database table.

## File Contract

Every ADR uses YAML front matter with schema version, immutable four-digit ID,
immutable slug, title, status, date, category, tags, keywords, and relationship
IDs. Its filename is `{id}-{slug}.md`, and its H1 is `ADR {id}: {title}`.

Allowed statuses are `proposed`, `accepted`, `rejected`, `deprecated`, and
`superseded`. Allowed categories are `architecture`, `backend`, `data`,
`deployment`, `domain`, `frontend`, `process`, `product`, and `security`. Tags
use lower-case kebab-case. Keywords are free-text search synonyms.

Required sections are:

1. Context
2. Decision
3. Consequences
4. Alternatives Considered
5. Review Trigger

## Gatekeeper Workflow

After the one-time schema migration, do not create or edit ADR files directly.
Start the local API and use its loopback-only endpoints:

```text
GET  http://127.0.0.1:8000/internal/adrs/schema
GET  http://127.0.0.1:8000/internal/adrs
GET  http://127.0.0.1:8000/internal/adrs/{id}
POST http://127.0.0.1:8000/internal/adrs/validate
POST http://127.0.0.1:8000/internal/adrs
PUT  http://127.0.0.1:8000/internal/adrs/{id}
```

Creation accepts structured metadata and named sections but no ID. The server
allocates the next ID while holding a filesystem lock and writes the canonical
file atomically. Updates require the latest `content_hash` and a
`change_summary`; a stale hash returns HTTP 409.

Accepted decisions cannot have their Decision section materially rewritten.
Create a new ADR with `supersedes` instead. There is intentionally no delete or
renumber endpoint.

The API writes files only. Review at `https://docs.crazykok.local`, inspect the
Git diff, run validation/tests, and commit outside the API.

## Safety Boundary

The internal routes are enabled only for local development, bound to the
loopback host port, and blocked by every Nginx virtual host. Production must set
`ADR_AUTHORING_ENABLED=false`. The API never stages, commits, or pushes files.

