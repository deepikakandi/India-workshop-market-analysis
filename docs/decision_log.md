# Decision Log

## 2026-08-04 - Day 1 decisions

### Pilot scope

- Pilot cities are Bengaluru and Hyderabad.
- Pilot categories are Cooking and baking, Art and painting, Pottery and ceramics, and Coffee making.
- Pune remains part of the broader six-metro market study, but not the Day 1 pilot scope.
- Excluded categories from prior draft/source briefs are not active pilot categories in repository configuration, seeds, fixtures, or working documentation.

### Architecture boundaries

- Keep the project as a lightweight analytics-engineering scaffold for now.
- Use PostgreSQL, dbt, Python, notebooks, and Power BI as the core local stack.
- Do not add Airflow, Kafka, Spark, cloud infrastructure, or production orchestration during Day 1.

### Data folder distinction

- `data/raw/` is for immutable collected responses.
- `data/manual/` is for manually entered or manually validated source-support files.
- `data/external/` remains available for third-party reference files that are not raw collection responses.

## 2026-08-05 - Day 2 decisions

### Canonical taxonomy source

- `config/taxonomy/pilot_scope.yml` is the canonical machine-readable pilot taxonomy.
- `dbt/seeds/pilot_categories.csv`, `dbt/seeds/pilot_cities.csv`, and `tests/fixtures/pilot_scope.json` mirror the canonical YAML for dbt and tests.
- Readable scope, dashboard, notebook, and collection-plan docs are maintained manually for human review.

### Controlled vocabulary boundary

- Day 2 defines controlled vocabulary and classification rules only.
- Classifier implementation, entity resolution logic, source fetching, and database tables are intentionally deferred.
- Source category text and source titles must be preserved before standardized category assignment.

### Source-register status

- `docs/source_register/source_register.csv` is the Day 2 candidate source register.
- Candidate sources are not approved for automated collection until terms, robots/access limits, authentication, cost, and reviewer notes are reviewed.
- Public page collection remains pending or unknown unless a specific reviewed source row says otherwise.

### Source instances and discovery backlog

- `source_register.csv` contains only concrete, individually reviewable source instances.
- Generic source families belong in `docs/source_register/source_discovery_backlog.csv`.
- Each discovered organizer, public studio calendar, coffee school, roaster, cafe, or training studio must later be added as its own source-register row with a stable `source_id`.
- All current source rows remain `pending_review`; no source is approved for collection on Day 2.
