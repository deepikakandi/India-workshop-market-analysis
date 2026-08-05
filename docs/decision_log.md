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

## 2026-08-05 - Day 3 decisions

### Preliminary source decisions

- District remains `pending_review`; automated collection and bulk extraction are not approved.
- BookMyShow remains `pending_review`; automated bulk extraction is not approved.
- Limited manual feasibility observation and sitemap-structure review may be documented for research design, but protected descriptions, images, copied listing content, and personal data must not be stored or republished.
- This project note is not legal advice.

### Permission caveats

- Robots rules and sitemap availability are not permission to reuse content.
- Source terms can change and must be re-reviewed before collection begins.
- Written permission is required when terms do not clearly permit the intended collection or reuse.

### Metadata contracts

- Raw response metadata must validate against `config/schemas/raw_response_metadata.schema.json`.
- Collection-run metadata must validate against `config/schemas/collection_run_metadata.schema.json`.
- Raw payload paths must remain under `data/raw/`.
- Raw payloads will be immutable once collection begins.
- Sensitive request information, including cookies, authorization headers, session tokens, API keys, passwords, and personal credentials, must never be stored.

## 2026-08-05 - Day 4 manual-first pilot source decision

Decision: The first data pilot will use manually transcribed factual fields from individually reviewed first-party sources. Automated web collection will be added only where an official API, public feed, export, written permission, or other documented permission basis exists.

Rationale: First-party sources provide cleaner provenance and lower duplicate risk for the first pilot. Manual transcription allows controlled validation of the taxonomy and event-record contract without assuming scraping, reuse, or API rights.

Consequence: Day 5 collection must use `config/pilot/manual_source_selection.yml` and `config/schemas/manual_event_record.schema.json`. `automation_permission_status` remains restrictive even when `collection_decision = approved_manual_collection`. Manual approval is an internal project-governance decision only; it does not imply source-owner license or endorsement.
