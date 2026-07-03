---
schema_version: 1
id: '0018'
slug: tests-for-business-logic
title: Test Business Logic
status: accepted
date: '2026-07-03'
category: process
tags:
  - business-logic
  - testing
keywords:
  - automated tests
  - quality assurance
supersedes: []
superseded_by: []
---

# ADR 0018: Test Business Logic


## Context

This project is a private, local-first operating system for discovering opportunities and planning operations for a food vending business in and around Drenthe. It will likely be implemented over multiple sessions with help from AI coding agents. Decisions must be explicit so the project stays coherent.

## Decision

Add tests for import, duplicate detection, search filters, scoring, and calendar feed generation.

## Consequences

Makes Codex-generated changes safer.

## Alternatives Considered

- Leave the decision implicit in chat history.
- Let the coding agent infer the design.
- Choose a broader or more complex option earlier than needed.

## Review Trigger

Review this ADR if the project scope, deployment model, data model, or primary workflow changes materially.
