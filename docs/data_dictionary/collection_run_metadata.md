# Collection Run Metadata

`config/schemas/collection_run_metadata.schema.json` defines the run-level contract for future collection jobs. Day 3 defines the contract only; it does not configure PostgreSQL or build collectors.

Required fields:

- `collection_run_id`
- `source_id`
- `collector_name`
- `collector_version`
- `git_commit_sha`
- `started_at`
- `completed_at`
- `run_status`
- `requested_count`
- `successful_count`
- `failed_count`
- `skipped_count`
- `duplicate_count`
- `bytes_collected`
- `rate_limit_events`
- `failure_summary`
- `approved_collection_scope`
- `city_scope`
- `category_scope`
- `initiated_by`
- `environment_name`

## Governance rule

Before a future collector runs, the source must have an approved or explicitly permitted collection scope in the source register. A source with `pending_review`, `rejected`, or `not_technically_feasible` must not run automated collection.

## Security rule

Run metadata must describe scope, counts, status, and failures without storing secrets, cookies, authorization headers, tokens, passwords, or credentials.
