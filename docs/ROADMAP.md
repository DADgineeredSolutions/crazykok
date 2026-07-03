# Milestone Roadmap

## Milestone 01 — Foundation Documentation

Status: prepared

Includes domain model, architecture, ADRs, and milestone prompts.

## Milestone 02 — Backend Skeleton

Implement the updated opportunity/operation domain model.

Deliverables:

- FastAPI app
- SQLite config
- SQLAlchemy models
- Alembic migrations
- CRUD services
- search endpoint
- initial tests

## Milestone 03 — Frontend Skeleton

Deliverables:

- React + TypeScript app
- opportunity list
- opportunity detail
- application status UI
- operation status UI
- filters
- API integration

## Milestone 04 — Import/Export

Deliverables:

- CSV import/export for opportunities
- duplicate detection
- validation
- source preservation
- confidence preservation

## Milestone 05 — Map & Calendar Planning Views

Deliverables:

- Leaflet map view
- FullCalendar planning view
- clickable opportunity markers/events
- application deadline display
- committed operation display

## Milestone 06 — Calendar Feeds & Operations Calendar

Deliverables:

- read-only ICS feeds
- subscribable Apple/Google/Outlook calendar feeds
- all opportunities feed
- filtered opportunities feeds
- committed operations feed
- application deadlines feed
- operation tasks feed

## Milestone 07 — Operations & Outcomes

Deliverables:

- operation planning
- setup/teardown details
- staffing/equipment notes
- operation outcomes
- year-over-year comparisons
- revenue/cost/profit tracking

## Milestone 08 — HATEOS API Navigation

Deliverables:

- HATEOS scaffolding to api results
- links to navigate via the api (next, previous, related object records)

## Milestone 09 — Decision Log

Status: complete

Deliverables:

- web-accessible, read-only UI generated from the repository ADRs
- previous/next navigation between records
- overview of all ADRs linking to their rendered Markdown view
- filters and search by status, tags, category, keywords, and search-hit excerpt
- dedicated configurable docs subdomain (`docs.crazykok.local` locally and
  `docs.crazykok.com` in production)
- validated ADR metadata with unique identifiers, categories, and tags
- local-only filesystem-backed authoring API that allocates immutable IDs,
  validates structured proposals, and never commits to Git
- frontend, indexer, routing, and deployment tests

Implementation plan: `milestones/milestone-09-codex-prompt.md`.

## Milestone 10 – Venue Management

Deliverables:

- Full venue data model
- Venue CRUD screens
- Contact management
- Document attachment support
- Photo gallery
- Map location picker
- Duplicate detection (to avoid creating the same venue twice)
- Opportunity history for each venue
- Venue detail page with tabs (Overview, Contacts, Documents, - Opportunities, Notes, Statistics)
