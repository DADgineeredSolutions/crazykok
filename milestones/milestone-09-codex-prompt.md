# Codex Prompt — Milestone 09 Decision Log

Read `docs/adr/`, `docs/DEPLOYMENT.md`, `docs/SECURITY.md`, and
`docs/adr/0019-ai-agent-doc-compliance.md` before coding.

## Goal

Publish the repository's architecture decision records as a read-only,
searchable decision log at a dedicated docs subdomain. The Markdown files in
`docs/adr/` remain the source of truth; the UI is a generated view of them.

## Intended Outcome

- `https://docs.crazykok.local` serves the decision log in local development.
- Production can set `DOCS_DOMAIN=docs.crazykok.com`.
- `/` lists every ADR and exposes search and filters.
- `/adr/{slug}` renders one ADR with previous/next navigation and a link back
  to the filtered overview.
- Direct navigation and browser refresh work for every decision URL.
- The public decision log makes no runtime API request.
- A loopback-only authoring API validates and writes ADR source files; ADRs are
  never stored in an application database table.

## Architecture

Implement the decision log as a separate static frontend entry point in the
existing Vite/React build, not as records copied into SQLite.

Add a build-time ADR indexer that:

1. reads `docs/adr/*.md` in deterministic ADR-number/slug order;
2. validates the metadata contract and unique ADR identifiers;
3. emits a generated JSON/TypeScript index for the docs frontend;
4. includes the Markdown body and plain searchable text; and
5. fails the build with a useful filename-specific error for malformed ADRs.

Render Markdown with a maintained Markdown component and GitHub-flavoured
Markdown support. Do not inject raw HTML with `dangerouslySetInnerHTML`.
Repository-relative links must remain usable from an ADR detail route.

Before implementation, record this static-build architecture in a new ADR.

## Files Are The Record Store

`docs/adr/*.md` is the only ADR record store. Do not add an ADR table, mirror
ADR content into SQLite, or make the public docs UI depend on the backend.

Git provides history, review, rollback, and the final audit trail. The
authoring API is a policy-enforcement boundary around filesystem changes, not
a second persistence layer. It may build in-memory indexes and return parsed
records, but it must always derive them from the files.

## ADR Content Contract

Use YAML front matter as the machine-readable envelope and Markdown as the
human-readable decision. Each ADR must have:

- `schema_version`;
- a unique quoted four-digit `id`;
- an immutable `slug`;
- `title`;
- `status`;
- `date` in `YYYY-MM-DD` format;
- one `category` from a small controlled vocabulary;
- one or more `tags` using lower-case kebab-case tokens;
- zero or more `keywords` for useful synonyms and phrases that may not occur
  naturally in the decision text;
- optional `supersedes` and `superseded_by` ADR ID lists;
- an H1 title in the form `ADR NNNN: Title`; and
- the standard decision sections already used by the repository.

Use a small, documented category vocabulary rather than creating a new
category for every record. Start with `architecture`, `backend`, `data`,
`deployment`, `domain`, `frontend`, `process`, `product`, and `security`, and
change that vocabulary only through review. Tags are an open but normalized
faceted vocabulary. Keywords improve recall and are searchable but are not
shown as primary classification.

The filename is `{id}-{slug}.md`. The front-matter ID, filename ID, H1 ID,
front-matter title, and H1 title must agree. Quote IDs in YAML so leading zeroes
cannot be interpreted as numbers. Normalize the existing ADRs as part of this
milestone and reconcile the duplicate `0022` records without losing unique
decision content.

Example:

```md
---
schema_version: 1
id: "0026"
slug: filesystem-backed-decision-log
title: Use A Filesystem-Backed Decision Log
status: proposed
date: 2026-07-03
category: architecture
tags:
  - adr
  - documentation
keywords:
  - decision record
  - architecture history
supersedes: []
superseded_by: []
---

# ADR 0026: Use A Filesystem-Backed Decision Log

## Context

...
```

Required body sections are `Context`, `Decision`, `Consequences`,
`Alternatives Considered`, and `Review Trigger`. Additional sections are
allowed. Empty required sections and placeholder text fail validation.

The generated record shape should contain at least:

- `id`
- `slug`
- `title`
- `status`
- `date`
- `category`
- `tags`
- `keywords`
- `markdown`
- `searchText`
- `sourcePath`

## Internal ADR Authoring API

Add an internal ADR authoring router to the FastAPI codebase. It is a local
tool for humans and coding agents, not part of the public application API.

Expose it only on the API's loopback-bound host port under `/internal/adrs`.
Nginx must explicitly return 404 for `/internal/` on the application and API
virtual hosts. Add `ADR_AUTHORING_ENABLED`, default it to `true` only in local
development, and fail closed when it is disabled. Production documentation
must keep it disabled.

The API operates directly on a configured `ADR_DIRECTORY`, which is
`docs/adr/` in the repository. The local API container may receive that single
directory as a read-write bind mount; do not mount the whole repository and do
not give the public web container write access.

Provide these operations:

- `GET /internal/adrs/schema` returns allowed statuses, categories, field
  constraints, required sections, and the active schema version.
- `GET /internal/adrs` and `GET /internal/adrs/{id}` let an agent inspect the
  canonical parsed records before proposing a change.
- `POST /internal/adrs/validate` validates a structured create/update proposal
  and returns errors, warnings, and canonical Markdown without writing.
- `POST /internal/adrs` validates a structured proposal, allocates the next ID,
  atomically creates the canonical file, and returns HTTP 201 with the ID,
  path, content hash, canonical docs URL, and generated Markdown.
- `PUT /internal/adrs/{id}` validates and atomically updates an existing file.
  It requires the caller's expected content hash and a change summary, and
  returns HTTP 409 if the source changed since it was read.

Creation requests must not accept a caller-selected ID. Under a filesystem
lock, allocate `max(existing IDs) + 1`, check the ID and slug again, write a
temporary file in the ADR directory, and atomically rename it. There is no
delete or renumber endpoint, and allocated IDs are never reused. The build
indexer independently rejects duplicate IDs and slugs as defence in depth.

Accept structured metadata and named Markdown sections rather than an opaque
complete file. The service owns front-matter serialization, heading order,
filename construction, final newline, and other canonical formatting.

Business rules:

- `id`, `slug`, and original `date` are immutable after creation.
- Status uses an explicit vocabulary and transition map: a terminal decision
  cannot silently return to `proposed`.
- A proposed ADR may be edited in place.
- A material change to the decision of an accepted ADR requires a new ADR that
  supersedes it. Typographical fixes, metadata enrichment, status transitions,
  and added clarifying consequences may update the existing ADR when the
  change summary explains why.
- Relationship IDs must exist, may not refer to self, must not form a
  supersession cycle, and are updated consistently on both sides.
- Tags are deduplicated and sorted; keywords are trimmed and deduplicated
  case-insensitively.
- Unknown front-matter keys, path traversal, symlinks, raw HTML, malformed
  dates, duplicate headings, and empty required sections are rejected.
- Validation errors use a stable machine-readable error code plus a human
  explanation and field/section location.

After this milestone is activated, update `docs/AI_INSTRUCTIONS.md` and the
contributor documentation: coding agents must inspect and modify ADRs through
the internal API. Direct file edits are forbidden except for the documented
one-time migration/bootstrap procedure or recovery when the gatekeeper itself
is being repaired. The API must never run `git add`, commit, push, or otherwise
mutate Git state.

The intended authoring flow is:

1. inspect the schema and current record through the API;
2. submit suggested structured content to validation;
3. create or update through the API, which writes the canonical file;
4. review it at `docs.crazykok.local` (the local docs dev build watches ADR
   source changes; the production-style image requires a rebuild);
5. inspect the filesystem/Git diff and run validation; and
6. commit the file change out of band from the API.

## Overview UI

The overview must provide:

- total result count;
- text search;
- status, category, and tag filters;
- clear-all control;
- an empty state with a way to reset filters;
- one linked result per ADR showing ID, title, date, status, category, tags,
  and a relevant search-hit excerpt;
- URL-backed search/filter state so a result set can be bookmarked or shared;
  and
- deterministic ordering, newest ADR number first by default, with an option
  for oldest first.

Search is case-insensitive and matches ID, title, status, category, tags,
keywords, and body text. Multiple words use AND semantics. Highlight matching
terms in the title, metadata, and excerpt without interpreting the query as
HTML or a regular expression.

Keep search client-side. The ADR collection is small and build-time content
does not justify a search service.

## ADR Detail UI

Each detail page must provide:

- rendered Markdown with readable heading, list, table, code, and link styles;
- visible ADR metadata;
- a canonical, stable slug URL;
- previous and next links based on ADR number order;
- disabled/absent boundary navigation for the first and last records;
- a return link that preserves the overview query and filters when possible;
  and
- a clear not-found page for an unknown slug.

Use semantic landmarks, labelled controls, visible focus styles, and a logical
heading hierarchy. The full flow must be usable by keyboard.

## Subdomain And Deployment

- Add `DOCS_DOMAIN`, defaulting to `docs.crazykok.local`, to `.env.example`,
  Docker Compose, Nginx, and the deployment documentation.
- Serve the decision-log bundle only for `DOCS_DOMAIN`.
- Include the docs host in HTTP-to-HTTPS redirects and local certificate
  generation.
- Keep unknown hosts returning HTTP 421.
- Document the local hosts-file entry and production DNS/TLS requirement.
- Do not add the docs origin to API CORS settings; this read-only site does not
  call the API.
- Add a container health check that verifies the docs virtual host as well as
  the main application host.

## Work Plan

### 1. Normalize And Validate ADRs

- Define and document the YAML front-matter schema, status transitions,
  category vocabulary, tag/keyword rules, and canonical Markdown format.
- Reconcile duplicate ADR identifiers.
- Add category and tag metadata to every ADR.
- Document the ADR authoring contract and category vocabulary.
- Add indexer tests for valid metadata, duplicate IDs/slugs, missing fields,
  malformed dates, and deterministic ordering.

### 2. Build The Authoring Gatekeeper

- Implement the internal filesystem-backed API, schema endpoint, structured
  validation, deterministic serialization, ID allocation, filesystem locking,
  atomic writes, optimistic concurrency, and relationship validation.
- Add unit and integration tests for every business rule and failure mode,
  including concurrent create/update requests and path traversal attempts.
- Mount only the ADR directory into the local API service and prove Nginx
  cannot reach the internal routes.
- Update agent and contributor instructions to require the API after the
  one-time migration is complete.

### 3. Generate The Decision Index

- Implement the build-time parser/indexer.
- Generate the typed frontend data artifact without hand-maintained duplicate
  content.
- Ensure ADR edits are reflected by a normal frontend/container rebuild.

### 4. Build Overview And Search

- Add the dedicated docs entry point and responsive shell.
- Implement query parsing, filters, sorting, counts, excerpts, highlighting,
  URL state, reset behaviour, and empty states.
- Keep search/filter logic in independently testable pure functions.

### 5. Build ADR Reading And Navigation

- Render Markdown safely.
- Implement stable detail routes, previous/next navigation, preserved return
  state, relative links, and the not-found view.

### 6. Expose The Docs Host

- Wire `DOCS_DOMAIN` through the environment, Docker build, Nginx virtual host,
  certificate script, health checks, and deployment docs.
- Verify the application, API, and docs hosts remain isolated and unknown
  hosts still fail closed.

### 7. Verify And Document

- Add frontend component/interaction tests for overview and detail behaviour.
- Add an end-to-end smoke test for direct ADR URLs and virtual-host routing.
- Run the frontend typecheck/build, frontend tests, indexer tests, and relevant
  container/config checks.
- Update the project journal and mark the milestone complete only after all
  acceptance criteria pass.

## Acceptance Criteria

- Every valid file in `docs/adr/` appears exactly once in the overview.
- ADR content exists only in files, never in an ADR database table.
- Duplicate or malformed ADR metadata fails the build with an actionable
  error.
- Only the authoring API can allocate an ID; concurrent creation cannot produce
  duplicates and IDs cannot be deleted, changed, or reused.
- Valid API creates and updates produce deterministic canonical files; invalid
  proposals do not change the filesystem.
- Stale updates return 409 without overwriting newer content.
- Internal authoring routes are unavailable through every Nginx virtual host
  and are disabled in production.
- The authoring API never stages or commits files.
- Search finds title, metadata, tag, and body matches and displays a useful
  highlighted excerpt.
- Status, category, and tag filters combine correctly with search and survive
  refresh via the URL.
- Every overview item opens its rendered ADR.
- Previous/next navigation follows numeric ADR order and handles boundaries.
- Direct ADR URLs and refreshes work on the docs subdomain.
- Markdown content cannot inject executable HTML or script.
- The docs frontend works at mobile and desktop widths and is keyboard usable.
- `docs.crazykok.local`, application hosts, and the API host route only to
  their intended content; unconfigured hosts return 421.
- The public decision log makes no runtime API request and needs no database.
- Tests and production builds pass.

## Non-Goals

- Editing or creating ADRs in the browser
- Comments, approvals, or workflow automation
- Authentication or public SaaS hosting features
- Moving ADR source content into the database
- Searching all project documentation outside `docs/adr/`
- Server-side search, analytics, or external search services
- Changing the meaning or status of existing decisions while adding metadata

## Suggested Commit Sequence

1. `Define and normalize the ADR file contract`
2. `Add filesystem backed ADR authoring gatekeeper`
3. `Add searchable decision log frontend`
4. `Serve decision log on docs subdomain`
5. `Document and verify milestone 09`
