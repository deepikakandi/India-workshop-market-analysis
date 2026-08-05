import csv
import copy
from datetime import date
from pathlib import Path

import pytest

from workshop_market.quality.manual_batch import (
    classify_current_historical,
    find_duplicate_candidates,
    load_manual_csv,
    normalize_csv_row,
    quality_report,
    validate_manual_csv,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BATCH = PROJECT_ROOT / "data" / "manual" / "observations" / "2026-08-05" / "pilot_event_records_batch_01.csv"


def test_manual_csv_loading() -> None:
    rows = load_manual_csv(BATCH)

    assert len(rows) == 12
    assert rows[0]["manual_record_id"] == "d5_b01_001"


def test_blank_cell_normalization() -> None:
    normalized, errors = normalize_csv_row(
        {
            "listed_price_inr": "",
            "sold_out_observed": "false",
            "audience_codes": "adults;young_adults",
        }
    )

    assert errors == []
    assert normalized["listed_price_inr"] is None
    assert normalized["sold_out_observed"] is False
    assert normalized["audience_codes"] == ["adults", "young_adults"]


def test_row_level_validation_errors_for_malformed_price(tmp_path: Path) -> None:
    rows = list(csv.DictReader(BATCH.open(newline="")))
    rows[0]["listed_price_inr"] = "22,026/-"
    bad_csv = tmp_path / "bad.csv"
    with bad_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows[:1])

    result = validate_manual_csv(bad_csv)

    assert result["valid"] is False
    assert "listed_price_inr must be numeric" in " ".join(result["row_results"][0]["errors"])


def test_duplicate_candidate_detection() -> None:
    rows = load_manual_csv(BATCH)
    duplicate = copy.deepcopy(rows[0])
    duplicate["manual_record_id"] = "duplicate_of_first"

    candidates = find_duplicate_candidates([rows[0], duplicate])

    assert candidates
    assert candidates[0]["duplicate_type"] in {"exact_source_record", "likely_same_event"}


def test_current_versus_historical_date_classification() -> None:
    rows = {row["manual_record_id"]: row for row in load_manual_csv(BATCH)}

    assert classify_current_historical(rows["d5_b01_002"], as_of=date(2026, 8, 5)) == "historical"
    assert classify_current_historical(rows["d5_b01_006"], as_of=date(2026, 8, 5)) == "active_or_in_progress"


def test_recurring_products_do_not_need_invented_dates() -> None:
    rows = {row["manual_record_id"]: row for row in load_manual_csv(BATCH)}
    record = rows["d5_b01_003"]

    assert record["event_start_at"] is None
    assert record["recurrence_type"] == "recurring"
    assert classify_current_historical(record, as_of=date(2026, 8, 5)) == "undated_recurring_product"


def test_crust_and_crumble_stale_heading_scenario_uses_actual_date() -> None:
    record = {
        "event_status_code": "available",
        "event_start_at": "2026-07-01T10:00:00+05:30",
        "event_end_at": "2026-07-01T15:00:00+05:30",
        "reviewer_notes": "Source displayed this inside an upcoming section.",
    }

    assert classify_current_historical(record, as_of=date(2026, 8, 5)) == "historical"


def test_registration_closed_is_not_sold_out_in_batch() -> None:
    rows = load_manual_csv(BATCH)

    assert not any(row["event_status_code"] == "registration_closed" and row["sold_out_observed"] for row in rows)


def test_missing_price_handling_passes_for_real_batch() -> None:
    result = validate_manual_csv(BATCH)

    assert result["valid"] is True
    assert any(row["listed_price_inr"] is None for row in load_manual_csv(BATCH))


def test_no_phone_email_customer_or_image_fields() -> None:
    rows = load_manual_csv(BATCH)
    blocked = ["phone", "email", "customer", "image", ".jpg", ".png", "testimonial"]

    for row in rows:
        joined = " ".join(str(value).lower() for value in row.values() if value is not None)
        assert not any(term in joined for term in blocked)


def test_quality_report_totals_match_input_data() -> None:
    report = quality_report(BATCH, as_of_date=date(2026, 8, 5))

    assert report["total_records"] == len(load_manual_csv(BATCH))
    assert report["valid_records"] == 12
    assert report["invalid_records"] == 0
    assert report["analysis_as_of_date"] == "2026-08-05"
    assert report["observation_batch_date"] == "2026-08-05"
    assert "do not invent event dates" in report["temporal_classification_method"]
    assert sum(report["records_by_source"].values()) == report["total_records"]
    assert sum(report["records_by_city"].values()) == report["total_records"]


def test_quality_report_temporal_classification_is_reproducible() -> None:
    first = quality_report(BATCH, as_of_date=date(2026, 8, 5))
    second = quality_report(BATCH, as_of_date=date(2026, 8, 5))

    assert first["temporal_record_counts"] == second["temporal_record_counts"]
    assert first["current_vs_historical_records"] == second["current_vs_historical_records"]
    assert first["temporal_record_counts"] == {
        "active_or_in_progress": 1,
        "historical": 2,
        "undated_course_or_product": 5,
        "undated_recurring_product": 4,
    }


def test_verification_statuses_are_self_checked_not_independent() -> None:
    rows = load_manual_csv(BATCH)
    report = quality_report(BATCH, as_of_date=date(2026, 8, 5))

    assert {row["verification_status"] for row in rows} == {"self_checked"}
    assert report["verification_status_distribution"] == {"self_checked": 12}
    assert not any(row["verification_status"] == "independently_verified" for row in rows)
