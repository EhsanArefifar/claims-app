# ADR-001: Environment Setup

**Date:** 2026-06-XX  
**Status:** Accepted

## Context

Starting a greenfield insurance claims application. Need a development 
environment that works on a locked-down corporate laptop (no admin rights, 
restricted network) and from home, without duplicating setup across machines.

## Decisions

### 1. GitHub Codespaces over local development
Corporate laptop has no admin rights and may block local Docker installs. 
Codespaces runs entirely in the browser — nothing to install, nothing to 
configure per machine. One environment, accessible from anywhere.

### 2. devcontainer Postgres over Neon (managed cloud DB)
Neon is free and persistent across rebuilds, but introduces a network 
dependency and an external account to manage. The devcontainer Postgres 
runs as a sidecar container — no internet required, starts with the 
environment, and is sufficient for local development. Neon remains an 
option if Codespaces storage becomes a constraint.

### 3. Python 3.12
Current stable release at project start. No legacy constraints pushing 
toward an older version. FastAPI and SQLAlchemy both support it fully.

### 4. FastAPI over Flask or Django
FastAPI generates OpenAPI docs automatically (Swagger UI at /docs), has 
native async support, and uses Python type hints for request/response 
validation. Flask requires more manual wiring; Django carries more 
overhead than needed for an API-first application.

## Consequences

- Development environment is tied to GitHub — if GitHub is unavailable, 
  work stops. Acceptable tradeoff given the corporate laptop constraint.
- Postgres data lives in a Docker volume. If the codespace is deleted 
  (not stopped), data is lost. Migrations (Slice 1+) will make this 
  recoverable.
- Free tier gives ~60 active hours/month on a 2-core machine. Sufficient 
  for current pace; revisit if it becomes a bottleneck.