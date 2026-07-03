---
schema_version: 1
id: '0004'
slug: fastapi-backend
title: Use FastAPI For The Backend
status: accepted
date: '2026-07-03'
category: backend
tags:
  - api
  - fastapi
keywords:
  - Python API
  - web backend
supersedes: []
superseded_by: []
---

# ADR 0004: Use FastAPI For The Backend


## Context

This project is a private, local-first operating system for discovering opportunities and planning operations for a food vending business in and around Drenthe. It will likely be implemented over multiple sessions with help from AI coding agents. Decisions must be explicit so the project stays coherent.

## Decision

Use FastAPI, Pydantic, and SQLAlchemy for the backend API.

## Consequences

Gives a typed Python API with automatic OpenAPI docs and good support for data workflows.

## Alternatives Considered

- Leave the decision implicit in chat history.
- Let the coding agent infer the design.
- Choose a broader or more complex option earlier than needed.

## Review Trigger

Review this ADR if the project scope, deployment model, data model, or primary workflow changes materially.
