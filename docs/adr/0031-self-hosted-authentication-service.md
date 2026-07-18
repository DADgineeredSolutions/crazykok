---
schema_version: 1
id: '0031'
slug: self-hosted-authentication-service
title: Use A Self-Hosted Authentication Service
status: accepted
date: '2026-07-13'
category: security
tags:
- authentication
- authentik
- authorization
- gateway
- sso
keywords:
- auth0 alternative
- forward auth
- service token
- single sign-on
supersedes:
- '0016'
superseded_by: []
---

# ADR 0031: Use A Self-Hosted Authentication Service

## Context

CrazyKok now has multiple browser-accessible surfaces: the main app, API,
database console, API reference, documentation, and future operational tooling.
The original no-authentication decision was appropriate while the application
was local-first and single-user, but the system now needs a reusable identity
boundary before more tools are exposed.

## Decision

Use a self-hosted authentication service at `auth.crazykok.local` locally and
`auth.crazykok.com` in production. Prefer authentik as the first implementation
because it provides hosted login flows, upstream SSO integrations, proxy
providers/outposts, OAuth2/OIDC, and group claims without building custom
password or session handling inside CrazyKok.

Nginx remains the public TLS gateway. It exposes authentik and includes
switchable forward-auth hooks for the main app, direct API host, and database
console. FastAPI independently understands authentik proxy headers, configured
OIDC/JWKS bearer tokens, and an internal bearer service token so API routes can
enforce identity and write-role checks when `AUTH_API_REQUIRED=true`.

## Consequences

- Authentication is centralized instead of duplicated across React, FastAPI,
  sqlite-web, and future operational services.
- Google SSO and other upstream providers can be configured in the auth service
  without changing application code.
- The first boot remains recoverable because gateway enforcement is disabled
  until authentik providers/outposts are configured.
- Production deployments must manage authentik secrets, Postgres data, backups,
  provider configuration, and service-token rotation.
- API authorization remains server-side; UI affordances may hide actions, but
  FastAPI still validates identity and write roles.
- External API clients can use authentik-issued OIDC bearer tokens once the API
  JWKS URL, issuer, and audience are configured.

## Alternatives Considered

- Auth0 or another hosted identity provider, rejected for cost and avoidable
  external dependency.
- Keycloak, kept as a fallback for enterprise-heavy requirements but avoided for
  the first slice because it is operationally heavier.
- OAuth2 Proxy alone, useful as a component but not a complete identity
  administration surface.
- Custom authentication in FastAPI/React, rejected because it would create
  unnecessary password, session, MFA, and SSO maintenance burden.

## Review Trigger

Review if authentik cannot support required upstream providers, proxy
authorization becomes insufficient for service-to-service communication, the app
needs tenant-specific permissions, or a hosted identity provider becomes cheaper
and safer than self-hosting.

## Resources

- ![Authentication surface map](/adr-assets/0031-self-hosted-authentication-service/auth-surface-map.svg)
- ![Browser forward-auth sequence](/adr-assets/0031-self-hosted-authentication-service/browser-forward-auth-sequence.svg)
- ![API authorization flow](/adr-assets/0031-self-hosted-authentication-service/api-auth-flow.svg)
- ![Machine-to-machine API authentication sequence](/adr-assets/0031-self-hosted-authentication-service/service-to-service-auth-sequence.svg)
- [Deployment authentication setup](../DEPLOYMENT.md#authentication-setup)
- [SSO-only browser authentication policy](../policies/2026-07-13-sso-only-browser-authentication.md)
