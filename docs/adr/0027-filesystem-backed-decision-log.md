---
schema_version: 1
id: '0027'
slug: filesystem-backed-decision-log
title: Use A Filesystem-Backed Decision Log
status: accepted
date: '2026-07-03'
category: architecture
tags:
  - adr
  - documentation
  - local-first
keywords:
  - decision record
  - architecture history
  - docs subdomain
supersedes: []
superseded_by: []
---

# ADR 0027: Use A Filesystem-Backed Decision Log

## Context

Architecture decisions must remain portable, reviewable in Git, usable by coding agents, and readable in a browser. A database-backed decision log would duplicate repository documentation and make the database an unnecessary dependency for project governance.

## Decision

Keep ADR Markdown files in `docs/adr/` as the only record store. Generate a read-only decision-log site from those files and serve it on the configured docs subdomain. Route creation and modification through a local-only API that validates structured proposals, allocates immutable identifiers, and writes canonical files without performing Git operations.

## Consequences

- Git remains the history, review, rollback, and audit mechanism.
- The public documentation site is static and requires no database or runtime API.
- ADR metadata must follow a strict machine-readable schema.
- Local authoring requires the gatekeeper API to be running and the ADR directory to be writable.
- Deployments rebuild the static documentation bundle when decisions change.

## Alternatives Considered

- Store ADRs in an application database table.
- Allow coding agents and contributors to edit ADR files without validation.
- Render ADR files through a public runtime API.
- Adopt a hosted documentation or decision-management service.

## Review Trigger

Review this ADR if multiple concurrent authors, remote authoring, or a repository split makes local filesystem locking and Git review insufficient.
