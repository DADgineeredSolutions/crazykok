---
schema_version: 1
id: '0030'
slug: publish-a-generated-openapi-contract-with-replaceable-interactive-docs
title: Publish A Generated OpenAPI Contract With Replaceable Interactive Docs
status: accepted
date: '2026-07-05'
category: architecture
tags:
- api
- contract-testing
- documentation
- openapi
keywords:
- hal
- json schema
- oasdiff
- redoc
- scalar
- schemathesis
supersedes: []
superseded_by: []
---

# ADR 0030: Publish A Generated OpenAPI Contract With Replaceable Interactive Docs

## Context

The API needs one machine-readable authority for reference documentation, public schemas, compatibility review, and implementation fitness testing. FastAPI can derive OpenAPI from the same typed routes that serve requests, while the documentation renderer runs in a separate container. The renderer must support interactive requests and Crazy Kok hypermedia without making its internal component model part of the application architecture.

## Decision

Generate the canonical public OpenAPI 3.1 document from intentionally public FastAPI routes and publish it, its YAML representation, and standalone component schemas through discoverable versioned API resources. Keep a generated repository snapshot only as the compatibility baseline; it is never edited as a second source of truth. Render the contract with a pinned, self-hosted Scalar API Reference container. Keep Crazy Kok branding and safe GET traversal of live HAL links in a thin local shell that observes standard HTTP responses rather than forking or importing renderer internals. Enforce contract fitness in three independent layers: deterministic snapshot drift, oasdiff backward-compatibility checks, and Schemathesis live response conformance.

## Consequences

API docs, schemas, tests, and interactive requests consume the same current contract. Internal ADR-authoring routes remain absent from public descriptions. Scalar can be upgraded or replaced with Redoc, Swagger UI, or another OpenAPI renderer without changing API endpoints or the HAL extension. Generated descriptions still require explicit summaries, media types, examples, and error contracts in route code, and compatibility-baseline updates require deliberate review.

## Alternatives Considered

Use open-source Redoc and maintain a fork for try-it and HAL actions. This preserves a familiar reading experience but creates a long-lived renderer maintenance burden. Use Swagger UI, which is interactive and customizable but provides a less polished reference experience. Hand-author OpenAPI, which supports design-first work but would create a competing authority unless code generation were restructured around it. Publish only FastAPI default /openapi.json, which exposes the wrong scope and provides no schema discovery, compatibility baseline, or docs-container boundary.

## Review Trigger

Review if Scalar no longer meets accessibility or maintenance needs, the API adopts design-first generation, authentication changes browser request constraints, or OpenAPI can directly express and render the required hypermedia actions without the local extension.
