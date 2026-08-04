# Proposed Analytics Architecture

## 1. Architecture

The repository is organized as a reproducible analytics-engineering system with five layers:

1. Source discovery and compliance register: document sources, permitted access methods, fields, restrictions, coverage, and reliability before collection.
2. Collection layer: Python collectors for official APIs, compliant public web pages, feeds, exports, and manually validated source files.
3. Raw preservation layer: store every response exactly as collected in `data/raw/` and load response metadata into PostgreSQL `raw`.
4. Standardization layer: Python cleaning pipelines normalize cities, categories, age groups, prices, organizers, venues, formats, and event/product types.
5. Warehouse and BI layer: dbt builds staging, intermediate, analytical marts, and Power BI output tables in PostgreSQL.

The intended data flow is:

`sources -> Python collectors -> data/raw + raw schema -> Python cleaners -> standardized schema -> dbt models -> analytics/powerbi schemas -> notebooks and Power BI`

## 2. Folder Structure

See the root README for the active folder map. The important split is:

- `src/workshop_market/collection`: API and web collection modules.
- `data/raw`: immutable raw payloads, excluded from git.
- `data/manual`: manually entered or manually validated source-support files, excluded from git except documentation.
- `src/workshop_market/cleaning`: Python standardization and entity-resolution code.
- `db/init`: PostgreSQL schema bootstrap scripts.
- `dbt/models/staging`: dbt source-facing standardization views.
- `dbt/models/intermediate`: reusable analytical logic.
- `dbt/models/marts/powerbi`: stable Power BI-facing tables.
- `powerbi`: Power BI workspace notes and handoff documentation.
- `notebooks`: EDA, hypothesis testing, and feasibility work.
- `tests`: repository, cleaning, and quality tests.

## 3. Technology Choices

- Python 3.12 for collection, cleaning, validation, and analysis.
- httpx, Beautiful Soup, Scrapy, and optional Playwright for compliant web/API collection.
- PostgreSQL 16 for durable local relational storage.
- dbt Core with dbt-postgres for SQL transformations and documented BI marts.
- Pandera plus pytest for automated data-quality checks.
- JupyterLab for exploratory analysis and hypothesis testing.
- Power BI consumes tables/views from the `powerbi` schema.
- Docker Compose runs PostgreSQL and dbt in a repeatable local environment.

## 4. Implementation Sequence

1. Freeze study taxonomy and source register template.
2. Configure local environment and PostgreSQL schemas.
3. Build a two-city pilot for Bengaluru and Hyderabad across cooking/baking, art, pottery, and coffee making.
4. Store raw responses and metadata before extracting fields.
5. Implement standardization for city, locality, category, age group, format, price, organizer, and event/product type.
6. Add entity-resolution rules for duplicate listings and organizers.
7. Build dbt staging models, dimensions, fact tables, snapshots, and Power BI marts.
8. Add automated data-quality gates for completeness, duplicates, valid prices/dates, and classification confidence.
9. Use notebooks for EDA, scoring framework validation, hypothesis tests, and feasibility scenarios.
10. Expand collection to all six metros only after pilot quality gates pass.

## 5. Risks and Assumptions

- Historical event listings may be incomplete; report maximum recoverable history rather than total market history.
- Platform bias is likely; preserve source-level coverage metrics and avoid using one source as market truth.
- Sold-out, registration-closed, and unavailable statuses must remain separate.
- Duplicate listings across platforms will require fuzzy matching and manual validation samples.
- Age groups, categories, and operating models often need confidence scores because public descriptions are vague.
- Google Maps, social media, and event platforms may restrict automated collection; use official APIs, exports, or compliant public collection.
- Observational web data can support demand proxies but should not be described as causal proof.
