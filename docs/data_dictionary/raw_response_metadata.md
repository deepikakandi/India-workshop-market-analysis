# Raw Response Metadata

`config/schemas/raw_response_metadata.schema.json` defines the metadata contract for future immutable raw payloads. It supports API, HTML, feed, manual, sitemap, robots, terms-review, and imported-file sources.

No live workshop data was collected on Day 3.

## Identity

- `collection_id`: stable identifier for one collected artifact.
- `collection_run_id`: run-level identifier linking many artifacts.
- `source_id`: source-register ID.
- `source_record_identifier`: source-native ID or URL slug when safe.
- `parent_collection_id`: parent artifact, such as a sitemap that led to a page.

## Request

- `requested_url`
- `canonical_url`
- `request_method`
- `request_headers_safe`
- `request_parameters_safe`
- `collection_method`
- `collector_name`
- `collector_version`

Never store secrets, cookies, authorization headers, session tokens, API keys, passwords, or personal credentials.

## Timing

Use timezone-aware ISO 8601 timestamps.

- `requested_at`
- `response_received_at`
- `collected_at`
- `source_event_time`
- `collection_duration_ms`

## Response

- `http_status`
- `content_type`
- `content_encoding`
- `response_size_bytes`
- `content_hash_sha256`
- `raw_storage_path`
- `response_language`
- `final_url`
- `redirect_count`

Raw payloads must be stored under `data/raw/` and treated as immutable once collection begins.

## Compliance

- `source_review_id`
- `collection_decision`
- `terms_reviewed_at`
- `robots_reviewed_at`
- `permission_basis`
- `attribution_required`
- `retention_policy`
- `contains_personal_data`
- `personal_data_notes`

Robots rules do not by themselves provide permission to reuse content. Source terms can change and must be re-reviewed.

## Run quality

- `success`
- `error_type`
- `error_message_safe`
- `retry_count`
- `rate_limit_observed`
- `parser_status`
- `validation_status`
- `notes`

## Reproducibility

- `git_commit_sha`
- `python_version`
- `environment_name`
- `schema_version`
