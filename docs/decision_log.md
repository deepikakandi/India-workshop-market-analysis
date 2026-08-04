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
