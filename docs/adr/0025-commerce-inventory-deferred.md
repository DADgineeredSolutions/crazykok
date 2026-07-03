---
schema_version: 1
id: '0025'
slug: commerce-inventory-deferred
title: Defer Commerce And Inventory Features
status: accepted
date: '2026-07-03'
category: product
tags:
  - commerce
  - scope
keywords:
  - inventory
  - point of sale
  - orders
supersedes: []
superseded_by: []
---

# ADR 0025: Defer Commerce And Inventory Features


## Context

This project is a private, local-first operating system for discovering opportunities and planning operations for a food vending business in and around Drenthe. It will likely be implemented over multiple sessions with help from AI coding agents. Decisions must be explicit so the project stays coherent.

## Decision

Defer product catalog, inventory, barcodes, QR codes, orders, shipments, customers, and delivery tracking.

## Consequences

Captures the future direction while keeping current milestones focused.

## Alternatives Considered

- Leave the decision implicit in chat history.
- Let the coding agent infer the design.
- Choose a broader or more complex option earlier than needed.

## Review Trigger

Review this ADR if the project scope, deployment model, data model, or primary workflow changes materially.
