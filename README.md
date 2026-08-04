# Indian Metro Workshop Market Analysis

Maintainable analytics-engineering repository for studying the paid workshop market across Bengaluru, Mumbai, Delhi NCR, Hyderabad, Pune, and Chennai.

## Proposed architecture

This project uses a layered pipeline:

1. Source discovery: maintain a source register covering access method, fields, city coverage, historical depth, reliability, and restrictions.
2. Collection: collect permitted API, web, feed, export, archive, and manually validated data using Python.
3. Raw storage: keep immutable payloads in `data/raw/` and store response metadata in PostgreSQL `raw`.
4. Cleaning and standardization: normalize events, organizers, venues, localities, prices, age groups, categories, delivery formats, and business models using Python.
5. Warehouse modeling: use dbt to build staging, intermediate, analytics, and Power BI marts in PostgreSQL.
6. Analysis and BI: use Jupyter for exploration/statistics and Power BI against stable tables in the `powerbi` schema.

Core flow:

```text
APIs/web/manual sources
  -> Python collectors
  -> immutable raw files + PostgreSQL raw schema
  -> Python cleaning pipelines
  -> PostgreSQL standardized schema
  -> dbt staging/intermediate/marts
  -> Jupyter analysis + Power BI output tables
```

## Folder structure

```text
.
├── config/                    # Example local settings and dbt profile template
├── data/
│   ├── raw/                   # Immutable raw responses; not committed
│   ├── manual/                # Manually entered/validated source-support files; contents not committed
│   ├── interim/               # Temporary cleaned extracts; not committed
│   ├── processed/             # Local analytical extracts; not committed
│   └── external/              # Manually sourced reference files; not committed
├── db/
│   └── init/                  # PostgreSQL bootstrap scripts
├── dbt/
│   ├── models/
│   │   ├── staging/           # Source-facing standardization views
│   │   ├── intermediate/      # Reusable analytical transformations
│   │   └── marts/
│   │       ├── analysis/      # Analysis-ready marts
│   │       └── powerbi/       # Stable Power BI output tables
│   ├── macros/
│   ├── seeds/
│   ├── snapshots/
│   └── tests/
├── docs/
│   ├── architecture/
│   ├── dashboard/
│   ├── data_dictionary/
│   ├── notebook_plans/
│   ├── project_scope/
│   └── source_register/
├── notebooks/
│   ├── eda/
│   ├── feasibility/
│   └── hypothesis_tests/
├── reports/
│   ├── exports/
│   └── powerbi/
├── powerbi/                   # Power BI workspace notes, PBIX handoff guidance, and connection docs
├── scripts/                   # CLI entrypoints and operational scripts
├── src/workshop_market/
│   ├── collection/            # API/web collectors
│   ├── cleaning/              # Standardization and entity resolution
│   ├── common/                # Shared config, logging, database helpers
│   └── quality/               # Data-quality validation helpers
└── tests/
    ├── unit/
    └── integration/
```

## Technology choices

- Python 3.12: collection, cleaning, validation, and analysis.
- httpx, Beautiful Soup, Scrapy, optional Playwright: API/web collection, with Playwright only for JavaScript-heavy permitted pages.
- PostgreSQL 16: durable relational storage for raw metadata, standardized tables, analytics marts, and Power BI output.
- dbt Core + dbt-postgres: repeatable SQL transformations, documentation, tests, and lineage.
- Pandera + pytest: data-quality checks and automated test runs.
- RapidFuzz: duplicate detection for event and organizer matching.
- JupyterLab, pandas, Polars, SciPy, statsmodels, scikit-learn: EDA, hypothesis testing, scoring, and feasibility modeling.
- Docker Compose: local PostgreSQL and dbt runtime.
- Power BI: connects to `powerbi` schema tables/views.

## Implementation sequence

1. Confirm source register and compliance rules.
2. Define taxonomy for cities, categories, age groups, formats, price tiers, and operating models.
3. Run a two-city pilot: Bengaluru and Hyderabad; cooking/baking, art, pottery, and coffee making; individual workshops, camps, and birthday events.
4. Store raw API/HTML/CSV/manual responses with source URL, timestamp, access method, hash, and collection run ID.
5. Build cleaning pipelines for date, price, location, category, age-group, organizer, venue, and format normalization.
6. Add duplicate and organizer-matching logic with confidence scores and manual review queues.
7. Create dbt staging models, dimensions, fact tables, snapshots, and Power BI marts.
8. Add automated quality gates for completeness, duplicates, invalid dates/prices, classification confidence, source coverage, and demand-signal coverage.
9. Use notebooks to validate demand metrics, pricing power, recurring-revenue potential, market gaps, and feasibility assumptions.
10. Expand to Mumbai, Delhi NCR, Pune, and Chennai after pilot gates pass.

## Risks and assumptions

- Historical data will be partial. Use "maximum recoverable historical data" and report earliest available dates by source.
- Some sites may prohibit scraping or require official APIs. Collection must follow source terms and preserve a compliance register.
- One platform can overrepresent a city, category, or price tier. Every analytical table should expose source coverage.
- Sold out, registration closed, cancelled, and unavailable are different states and should not be collapsed too early.
- Reviews and social engagement are demand proxies, not confirmed sales.
- Duplicate events across platforms are expected and need fuzzy matching plus manual validation samples.
- Category, audience, and operating-model labels will often be ambiguous; preserve original labels and standardized confidence scores.
- Power BI tables should be stable and intentionally modeled, not direct notebook exports.

## Local setup

1. Copy environment template:

   ```bash
   cp .env.example .env
   ```

2. Set a local `POSTGRES_PASSWORD` in `.env`.

3. Start PostgreSQL:

   ```bash
   docker compose up postgres
   ```

4. Run dbt debug:

   ```bash
   docker compose run --rm dbt debug
   ```

5. Install Python dependencies locally if desired:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev,analysis]"
   ```

6. Run tests:

   ```bash
   pytest
   ```

## Current scaffold status

This repository currently contains structure, configuration, documentation, Docker Compose, dbt skeleton files, and basic tests only. It intentionally does not include collectors, credentials, production schemas, or full application logic yet.
