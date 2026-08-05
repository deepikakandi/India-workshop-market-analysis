"""CSV loading, validation, duplicate checks, and quality summaries for manual batches.

This module performs local file validation only. It does not fetch pages, call APIs,
scrape websites, or use browser automation.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from workshop_market.quality.manual_event_records import validate_manual_event_record
from workshop_market.quality.metadata_contracts import MetadataValidationError

ARRAY_FIELDS = {"secondary_category_codes", "audience_codes"}
BOOLEAN_FIELDS = {
    "tax_included",
    "materials_included",
    "take_home_product",
    "certificate_included",
    "sold_out_observed",
    "waitlist_available",
    "booking_required",
}
INTEGER_FIELDS = {
    "minimum_age",
    "maximum_age",
    "duration_minutes",
    "seats_total",
    "seats_available",
    "interested_count",
}
FLOAT_FIELDS = {
    "listed_price_inr",
    "discounted_price_inr",
    "additional_fee_inr",
    "classification_confidence",
    "price_confidence",
    "date_confidence",
    "status_confidence",
}
DATE_FIELDS = {"observed_at", "event_start_at", "event_end_at", "registration_deadline"}
TEXT_FOR_DUPLICATES = {"event_title_original", "organizer_name_original", "venue_name_original", "city_code"}


@dataclass
class RowValidationResult:
    row_number: int
    manual_record_id: str | None
    valid: bool
    errors: list[str]


def normalize_blank(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped if stripped else None


def _parse_bool(value: str, field: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "yes", "1"}:
        return True
    if normalized in {"false", "no", "0"}:
        return False
    raise ValueError(f"{field} must be true/false when provided")


def _parse_int(value: str, field: str) -> int:
    if not re.fullmatch(r"-?\d+", value.strip()):
        raise ValueError(f"{field} must be an integer when provided")
    return int(value)


def _parse_float(value: str, field: str) -> float:
    normalized = value.replace(",", "").strip()
    if not re.fullmatch(r"-?\d+(?:\.\d+)?", normalized):
        raise ValueError(f"{field} must be numeric when provided")
    return float(normalized)


def normalize_csv_row(row: dict[str, str | None]) -> tuple[dict[str, Any], list[str]]:
    normalized: dict[str, Any] = {}
    errors: list[str] = []
    for field, raw_value in row.items():
        value = normalize_blank(raw_value)
        if field in ARRAY_FIELDS:
            normalized[field] = [] if value is None else [part.strip() for part in value.split(";") if part.strip()]
        elif field in BOOLEAN_FIELDS:
            if value is None:
                normalized[field] = None
            else:
                try:
                    normalized[field] = _parse_bool(value, field)
                except ValueError as error:
                    errors.append(str(error))
                    normalized[field] = value
        elif field in INTEGER_FIELDS:
            if value is None:
                normalized[field] = None
            else:
                try:
                    normalized[field] = _parse_int(value, field)
                except ValueError as error:
                    errors.append(str(error))
                    normalized[field] = value
        elif field in FLOAT_FIELDS:
            if value is None:
                normalized[field] = None
            else:
                try:
                    normalized[field] = _parse_float(value, field)
                except ValueError as error:
                    errors.append(str(error))
                    normalized[field] = value
        else:
            normalized[field] = value
    return normalized, errors


def load_manual_csv(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(newline="") as csv_file:
        for row in csv.DictReader(csv_file):
            normalized, errors = normalize_csv_row(row)
            if errors:
                normalized["_normalization_errors"] = errors
            rows.append(normalized)
    return rows


def validate_manual_csv(path: Path) -> dict[str, Any]:
    records = load_manual_csv(path)
    results: list[RowValidationResult] = []
    for index, record in enumerate(records, start=2):
        errors = list(record.pop("_normalization_errors", []))
        try:
            validate_manual_event_record(record)
        except MetadataValidationError as error:
            errors.extend(error.errors)
        results.append(
            RowValidationResult(
                row_number=index,
                manual_record_id=record.get("manual_record_id"),
                valid=not errors,
                errors=errors,
            )
        )
    return {
        "path": str(path),
        "row_count": len(records),
        "valid": all(result.valid for result in results),
        "valid_records": sum(result.valid for result in results),
        "invalid_records": sum(not result.valid for result in results),
        "row_results": [result.__dict__ for result in results],
    }


def normalize_for_match(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value).lower()).strip()


def event_date_key(record: dict[str, Any]) -> str:
    value = record.get("event_start_at")
    if not value:
        return ""
    return str(value)[:10]


def duplicate_key(record: dict[str, Any]) -> tuple[Any, ...]:
    return (
        record.get("source_id"),
        normalize_for_match(record.get("source_record_identifier")),
        normalize_for_match(record.get("event_title_original")),
        event_date_key(record),
        normalize_for_match(record.get("organizer_name_original")),
        normalize_for_match(record.get("venue_name_original")),
        record.get("city_code"),
        record.get("listed_price_inr"),
    )


def likely_duplicate_key(record: dict[str, Any]) -> tuple[Any, ...]:
    return (
        normalize_for_match(record.get("event_title_original")),
        event_date_key(record),
        normalize_for_match(record.get("organizer_name_original")),
        normalize_for_match(record.get("venue_name_original")),
        record.get("city_code"),
        record.get("listed_price_inr"),
    )


def find_duplicate_candidates(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    likely_buckets: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for record in records:
        buckets.setdefault(duplicate_key(record), []).append(record)
        likely_buckets.setdefault(likely_duplicate_key(record), []).append(record)

    candidates: list[dict[str, Any]] = []
    for key, grouped in buckets.items():
        if len(grouped) > 1:
            candidates.append(
                {
                    "duplicate_type": "exact_source_record",
                    "key": [str(part) for part in key],
                    "manual_record_ids": [row.get("manual_record_id") for row in grouped],
                }
            )
    for key, grouped in likely_buckets.items():
        if len(grouped) > 1:
            ids = [row.get("manual_record_id") for row in grouped]
            if not any(candidate["manual_record_ids"] == ids for candidate in candidates):
                candidates.append(
                    {
                        "duplicate_type": "likely_same_event",
                        "key": [str(part) for part in key],
                        "manual_record_ids": ids,
                    }
                )
    return candidates


def parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def parse_analysis_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError("as_of_date must use YYYY-MM-DD format") from error


def infer_observation_batch_date(csv_path: Path) -> str:
    candidate = csv_path.parent.name
    parse_analysis_date(candidate)
    return candidate


def classify_current_historical(record: dict[str, Any], *, as_of: date) -> str:
    status = record.get("event_status_code")
    if status in {"completed", "cancelled"}:
        return "historical"

    start = parse_iso_datetime(record.get("event_start_at"))
    end = parse_iso_datetime(record.get("event_end_at"))
    if end and end.date() < as_of:
        return "historical"
    if start and start.date() < as_of and (not end or end.date() >= as_of):
        return "active_or_in_progress"
    if start and start.date() >= as_of:
        return "future_scheduled"
    if record.get("recurrence_type") == "recurring":
        return "undated_recurring_product"
    return "undated_course_or_product"


def confidence_bucket(value: Any) -> str:
    if value is None:
        return "missing"
    value = float(value)
    if value >= 0.9:
        return "high"
    if value >= 0.7:
        return "medium"
    return "low"


def count_by(records: list[dict[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(str(record.get(field) or "missing") for record in records).items()))


def missingness(records: list[dict[str, Any]]) -> dict[str, int]:
    if not records:
        return {}
    fields = [field for field in records[0] if not field.startswith("_")]
    def is_missing(value: Any) -> bool:
        return value is None or value == "" or value == []

    return {
        field: sum(is_missing(record.get(field)) for record in records)
        for field in fields
    }


def quality_report(csv_path: Path, *, as_of_date: date, observation_batch_date: str | None = None) -> dict[str, Any]:
    validation = validate_manual_csv(csv_path)
    records = load_manual_csv(csv_path)
    for record in records:
        record.pop("_normalization_errors", None)
    duplicates = find_duplicate_candidates(records)
    temporal_counts = dict(
        sorted(Counter(classify_current_historical(record, as_of=as_of_date) for record in records).items())
    )
    governance_failures = [
        result
        for result in validation["row_results"]
        if any("source" in error.lower() or "approved" in error.lower() or "scope" in error.lower() for error in result["errors"])
    ]
    warnings: list[str] = []
    if duplicates:
        warnings.append("Duplicate candidates require manual review; no rows were deleted.")
    if validation["invalid_records"]:
        warnings.append("One or more rows failed validation.")
    if not warnings:
        warnings.append("No duplicate or governance warnings from local validation.")

    confidence_distribution = {
        field: dict(sorted(Counter(confidence_bucket(record.get(field)) for record in records).items()))
        for field in [
            "classification_confidence",
            "price_confidence",
            "date_confidence",
            "status_confidence",
        ]
    }
    observation_batch_date = observation_batch_date or infer_observation_batch_date(csv_path)
    temporal_classification_method = (
        "Compare event_start_at/event_end_at with the explicit analysis_as_of_date; "
        "do not invent event dates for undated recurring products, courses, or workshop products."
    )
    return {
        "csv_path": str(csv_path),
        "generated_at": datetime.now().astimezone().isoformat(),
        "analysis_as_of_date": as_of_date.isoformat(),
        "observation_batch_date": observation_batch_date,
        "temporal_classification_method": temporal_classification_method,
        "total_records": len(records),
        "valid_records": validation["valid_records"],
        "invalid_records": validation["invalid_records"],
        "records_by_city": count_by(records, "city_code"),
        "records_by_source": count_by(records, "source_id"),
        "records_by_category": count_by(records, "primary_category_code"),
        "records_by_product_type": count_by(records, "product_type_code"),
        "current_vs_historical_records": temporal_counts,
        "temporal_record_counts": temporal_counts,
        "price_tier_distribution": count_by(records, "price_tier_code"),
        "missingness_by_field": missingness(records),
        "duplicate_candidates": duplicates,
        "source_url_coverage": {
            "records_with_source_url": sum(bool(record.get("source_url")) for record in records),
            "records_missing_source_url": sum(not bool(record.get("source_url")) for record in records),
        },
        "verification_status_distribution": count_by(records, "verification_status"),
        "confidence_distribution": confidence_distribution,
        "governance_failures": governance_failures,
        "warnings": warnings,
        "validation": validation,
    }


def write_quality_report(report: dict[str, Any], json_path: Path, md_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Day 5 Batch 01 Quality Report",
        "",
        "This report summarizes manually transcribed factual records only. It does not interpret market demand from the small batch.",
        "",
        f"- Total records: {report['total_records']}",
        f"- Valid records: {report['valid_records']}",
        f"- Invalid records: {report['invalid_records']}",
        f"- Analysis as-of date: {report['analysis_as_of_date']}",
        f"- Observation batch date: {report['observation_batch_date']}",
        f"- Temporal classification method: {report['temporal_classification_method']}",
        f"- Duplicate candidates: {len(report['duplicate_candidates'])}",
        f"- Governance failures: {len(report['governance_failures'])}",
        "",
        "## Records by city",
        "",
    ]
    for key, value in report["records_by_city"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Records by source", ""])
    for key, value in report["records_by_source"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Records by category", ""])
    for key, value in report["records_by_category"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Temporal classification", ""])
    for key, value in report["temporal_record_counts"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Warnings", ""])
    for warning in report["warnings"]:
        lines.append(f"- {warning}")
    lines.append("")
    md_path.write_text("\n".join(lines))
