"""Validation helpers for raw-response and collection-run metadata contracts.

This module validates metadata only. It does not fetch pages, call APIs, or parse
workshop payloads.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_ROOT = PROJECT_ROOT / "config" / "schemas"
SOURCE_REGISTER_PATH = PROJECT_ROOT / "docs" / "source_register" / "source_register.csv"

RAW_RESPONSE_SCHEMA_PATH = SCHEMA_ROOT / "raw_response_metadata.schema.json"
COLLECTION_RUN_SCHEMA_PATH = SCHEMA_ROOT / "collection_run_metadata.schema.json"

SHA256_PATTERN = re.compile(r"^[A-Fa-f0-9]{64}$")
APPROVED_COLLECTION_DECISIONS = {
    "approved_official_api",
    "approved_manual_collection",
    "approved_limited_public_collection",
}
DISALLOWED_HEADER_PARTS = {
    "authorization",
    "cookie",
    "set-cookie",
    "token",
    "password",
    "passwd",
    "secret",
    "session",
    "api-key",
    "apikey",
    "x-api-key",
}


@dataclass
class MetadataValidationError(ValueError):
    """Clear validation error for metadata contract failures."""

    errors: list[str]

    def __str__(self) -> str:
        return "; ".join(self.errors)


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object from disk."""

    return json.loads(path.read_text())


def load_schema(schema_path: Path) -> dict[str, Any]:
    """Load a JSON Schema document."""

    return load_json(schema_path)


def _json_schema_errors(record: dict[str, Any], schema_path: Path) -> list[str]:
    validator = Draft202012Validator(load_schema(schema_path))
    return [error.message for error in sorted(validator.iter_errors(record), key=str)]


def _parse_timezone_aware_timestamp(value: str, field_name: str) -> str | None:
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return f"{field_name} must be a valid ISO 8601 timestamp"

    if parsed.tzinfo is None or parsed.tzinfo.utcoffset(parsed) is None:
        return f"{field_name} must include timezone information"

    return None


def _timestamp_errors(record: dict[str, Any], fields: list[str]) -> list[str]:
    errors: list[str] = []
    for field in fields:
        value = record.get(field)
        if value is None:
            continue
        if not isinstance(value, str):
            errors.append(f"{field} must be a string timestamp or null")
            continue
        error = _parse_timezone_aware_timestamp(value, field)
        if error:
            errors.append(error)
    return errors


def _sensitive_key_errors(mapping: dict[str, Any], field_name: str) -> list[str]:
    errors: list[str] = []
    for key in mapping:
        normalized = key.lower().replace("_", "-")
        if any(disallowed in normalized for disallowed in DISALLOWED_HEADER_PARTS):
            errors.append(f"{field_name} contains sensitive key: {key}")
    return errors


def _raw_path_errors(raw_storage_path: str) -> list[str]:
    path = PurePosixPath(raw_storage_path)
    if path.is_absolute():
        return ["raw_storage_path must be relative and under data/raw/"]
    if ".." in path.parts:
        return ["raw_storage_path must not contain parent-directory traversal"]
    if len(path.parts) < 3 or path.parts[0] != "data" or path.parts[1] != "raw":
        return ["raw_storage_path must remain under data/raw/"]
    return []


def _raise_if_errors(errors: list[str]) -> None:
    if errors:
        raise MetadataValidationError(errors)


def validate_raw_response_metadata(record: dict[str, Any]) -> None:
    """Validate one raw-response metadata record."""

    errors = _json_schema_errors(record, RAW_RESPONSE_SCHEMA_PATH)
    errors.extend(
        _timestamp_errors(
            record,
            [
                "requested_at",
                "response_received_at",
                "collected_at",
                "source_event_time",
                "terms_reviewed_at",
                "robots_reviewed_at",
            ],
        )
    )
    errors.extend(_sensitive_key_errors(record.get("request_headers_safe", {}), "request_headers_safe"))
    errors.extend(
        _sensitive_key_errors(record.get("request_parameters_safe", {}), "request_parameters_safe")
    )

    content_hash = record.get("content_hash_sha256")
    if isinstance(content_hash, str) and not SHA256_PATTERN.fullmatch(content_hash):
        errors.append("content_hash_sha256 must be a 64-character hexadecimal SHA-256 digest")

    raw_storage_path = record.get("raw_storage_path")
    if isinstance(raw_storage_path, str):
        errors.extend(_raw_path_errors(raw_storage_path))

    _raise_if_errors(errors)


def validate_collection_run_metadata(record: dict[str, Any]) -> None:
    """Validate one collection-run metadata record."""

    errors = _json_schema_errors(record, COLLECTION_RUN_SCHEMA_PATH)
    errors.extend(_timestamp_errors(record, ["started_at", "completed_at"]))
    _raise_if_errors(errors)


def load_source_register(path: Path = SOURCE_REGISTER_PATH) -> dict[str, dict[str, str]]:
    """Load source-register rows keyed by source_id."""

    with path.open(newline="") as source_file:
        return {row["source_id"]: row for row in csv.DictReader(source_file)}


def assert_source_collection_permitted(
    source_id: str,
    *,
    source_register_path: Path = SOURCE_REGISTER_PATH,
) -> dict[str, str]:
    """Return the source row only when collection is explicitly approved.

    Future collectors should call this before making requests. A pending,
    rejected, template, or missing source is not permitted.
    """

    sources = load_source_register(source_register_path)
    row = sources.get(source_id)
    if row is None:
        raise MetadataValidationError([f"source_id is not in source register: {source_id}"])

    decision = row.get("collection_decision", "")
    if decision not in APPROVED_COLLECTION_DECISIONS:
        raise MetadataValidationError(
            [f"source_id {source_id} is not approved for collection: {decision}"]
        )

    evidence_fields = [
        "review_evidence_url",
        "reviewed_by",
        "reviewed_at",
        "collection_decision_reason",
        "permitted_use_scope",
        "permitted_fields",
        "prohibited_fields",
    ]
    missing = [field for field in evidence_fields if not row.get(field, "").strip()]
    if missing:
        raise MetadataValidationError(
            [f"approved source_id {source_id} is missing evidence fields: {', '.join(missing)}"]
        )

    if not (row.get("terms_url", "").strip() or row.get("api_documentation_url", "").strip()):
        raise MetadataValidationError(
            [f"approved source_id {source_id} must include terms_url or api_documentation_url"]
        )

    return row
