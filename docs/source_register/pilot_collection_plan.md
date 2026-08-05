# Pilot Collection Plan

The initial collection plan focuses on Bengaluru and Hyderabad.

The structured candidate source register is `docs/source_register/source_register.csv`. Rows in that file are candidates only. Do not treat public-page collection or automation as approved until the terms, robots/access limits, review evidence, reviewer, and collection decision are complete.

Generic source families are tracked in `docs/source_register/source_discovery_backlog.csv`, not in the source register. Each discovered organizer, studio calendar, coffee school, roaster, cafe, or training studio must later be added as its own concrete source-register row with a stable `source_id`.

## Pilot categories

- Cooking and baking
- Art and painting
- Pottery and ceramics
- Coffee making

## Collection priorities

1. Confirm permitted access method for each candidate source.
2. Capture raw API, HTML, CSV, feed, archive, or manual-validation artifacts before transformation.
3. Record source name, source URL, access method, collection timestamp, city, category, and response hash.
4. Validate that event dates, prices, venue/locality, organizer, age suitability, format, and availability status can be collected consistently.
5. Track source coverage by city and category before using the data for demand scoring.

## Pilot success checks

- Core fields have acceptable completeness.
- Duplicate events can be resolved across sources.
- Organizer identities can be matched with confidence.
- Category classification is consistent for the four pilot categories.
- At least two demand-signal types are available for major pilot records.
- The process can be repeated without changing the architecture.

## Day 2 restriction

No collectors, API calls, live page fetches, scraping, or database setup are part of the Day 2 source-register work.

## Day 3 governance contracts

Day 3 adds the source-review workflow and metadata contracts only. No live workshop data is collected.

Before any future collector runs:

1. The source must have a concrete `source_register.csv` row.
2. The source must have review evidence, reviewer, reviewed timestamp, and re-review date.
3. `automation_permission_status` must allow the operation, and `collection_decision` must be approved or explicitly permitted for the intended use.
4. Permitted and prohibited fields must be documented.
5. Maximum request frequency or manual-only limits must be recorded.
6. Raw response metadata must validate against `config/schemas/raw_response_metadata.schema.json`.
7. Collection-run metadata must validate against `config/schemas/collection_run_metadata.schema.json`.

Robots rules, sitemap visibility, and public page access are not permission to reuse content. Terms can change and must be re-reviewed.

Raw payloads will be immutable once collection begins and must stay under `data/raw/`. Sensitive request information such as cookies, authorization headers, session tokens, API keys, passwords, or personal credentials must never be stored.
