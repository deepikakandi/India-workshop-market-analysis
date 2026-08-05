# Project Log

## 2026-08-04 - Day 1 repository architecture audit

- Confirmed pilot cities: Bengaluru and Hyderabad.
- Confirmed pilot categories: Cooking and baking, Art and painting, Pottery and ceramics, Coffee making.
- Reviewed repository scaffold for source discovery, collection, raw-data preservation, cleaning, PostgreSQL, dbt, notebooks, tests, and Power BI readiness.
- Added explicit documentation locations for project decisions, project log, manual data support, and Power BI handoff.
- No scraping, cloud infrastructure, scheduling system, or production pipeline logic was added.

## 2026-08-05 - Day 2 taxonomy and source-register setup

- Froze the pilot taxonomy in `config/taxonomy/pilot_scope.yml`.
- Added controlled vocabularies for categories, subcategories, audiences, formats, operating models, product/event types, price tiers, event statuses, skill levels, and pricing units.
- Added category-boundary rules without implementing a classifier.
- Created the Bengaluru and Hyderabad candidate source-discovery and compliance register.
- Added source-evaluation rules and validation tests for taxonomy and source-register consistency.
- No collectors, API calls, scraping, PostgreSQL setup, dashboards, or orchestration were added.

## 2026-08-05 - Day 2 source-register refinement

- Split concrete source instances from generic discovery families.
- Kept only individually reviewable sources in `docs/source_register/source_register.csv`.
- Moved generic organizer, studio-calendar, and coffee-source discovery work into `docs/source_register/source_discovery_backlog.csv`.
- Added review-evidence fields and a controlled `collection_decision` column.
- Left every current source as `pending_review`.

## 2026-08-05 - Day 3 source-review workflow and metadata contracts

- Added a repeatable source-review checklist.
- Added preliminary District and BookMyShow review records.
- Added reusable organizer-website and public-studio-calendar review templates.
- Updated District and BookMyShow source-register rows with preliminary evidence while keeping collection decisions pending.
- Added raw-response and collection-run metadata JSON schemas, data dictionaries, fixtures, and validation tests.
- No live workshop data, event API calls, scrapers, PostgreSQL setup, or dashboard code were added.

## 2026-08-05 - Day 4 first-party source reviews and manual pilot contract

- Registered concrete first-party candidate sources for Bengaluru and Hyderabad, including pottery, art, baking, and coffee-making coverage.
- Created individual source-review records for the Day 4 first-party sources.
- Selected a balanced Day 5 manual pilot in `config/pilot/manual_source_selection.yml`; no live workshop records were collected. Later correction made Aestraa art-only and added flexible record targets where shortfalls are allowed.
- Added the manual event-record JSON Schema, data dictionary, CSV import template, validator, fixture, and tests.
- Kept automated collection blocked unless a future source review records an official API, feed, export, written permission, or other documented permission basis.
