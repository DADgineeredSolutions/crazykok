---
schema_version: 1
id: '0008'
slug: local-document-storage
title: Store Documents Locally With Metadata
status: accepted
date: '2026-07-03'
category: data
tags:
  - documents
  - local-storage
keywords:
  - vendor documents
  - file metadata
supersedes: []
superseded_by: []
---

# ADR 0008: Store Documents Locally With Metadata


## Context

This project is a private, local-first operating system for discovering opportunities and planning operations for a food vending business in and around Drenthe. It will likely be implemented over multiple sessions with help from AI coding agents. Decisions must be explicit so the project stays coherent.

## Decision

Store vendor documents locally and link them with database metadata.

## Consequences

Keeps PDFs, maps, vendor packs, and rules available offline.

## Alternatives Considered

- Leave the decision implicit in chat history.
- Let the coding agent infer the design.
- Choose a broader or more complex option earlier than needed.

## Review Trigger

Review this ADR if the project scope, deployment model, data model, or primary workflow changes materially.
