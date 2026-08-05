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
