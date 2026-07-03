---
schema_version: 1
id: '0012'
slug: research-provenance
title: Track Research Provenance
status: accepted
date: '2026-07-03'
category: data
tags:
  - provenance
  - research
keywords:
  - source tracking
  - data audit
supersedes: []
superseded_by: []
---

# ADR 0012: Track Research Provenance


## Context

This project is a private, local-first operating system for discovering opportunities and planning operations for a food vending business in and around Drenthe. It will likely be implemented over multiple sessions with help from AI coding agents. Decisions must be explicit so the project stays coherent.

## Decision

Store source URLs, retrieval dates, verification dates, notes, and confidence ratings.

## Consequences

Makes researched data auditable and trustworthy.

## Alternatives Considered

- Leave the decision implicit in chat history.
- Let the coding agent infer the design.
- Choose a broader or more complex option earlier than needed.

## Review Trigger

Review this ADR if the project scope, deployment model, data model, or primary workflow changes materially.
