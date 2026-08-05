import copy
import json
from pathlib import Path

import pytest
import yaml

from workshop_market.quality.metadata_contracts import (
    MetadataValidationError,
    assert_source_collection_permitted,
    validate_collection_run_metadata,
    validate_raw_response_metadata,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = PROJECT_ROOT / "tests" / "fixtures"
REVIEWS = PROJECT_ROOT / "docs" / "source_register" / "reviews"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def test_valid_raw_response_metadata_passes() -> None:
    validate_raw_response_metadata(load_fixture("raw_response_metadata_valid.json"))


def test_valid_collection_run_metadata_passes() -> None:
    validate_collection_run_metadata(load_fixture("collection_run_metadata_valid.json"))


def test_missing_required_raw_field_fails() -> None:
    record = load_fixture("raw_response_metadata_valid.json")
    record.pop("source_id")

    with pytest.raises(MetadataValidationError, match="source_id"):
        validate_raw_response_metadata(record)


def test_credentials_and_sensitive_headers_fail() -> None:
    record = load_fixture("raw_response_metadata_valid.json")
    record["request_headers_safe"]["Authorization"] = "redacted-sensitive-header-value"

    with pytest.raises(MetadataValidationError, match="sensitive key"):
        validate_raw_response_metadata(record)


def test_sensitive_request_parameters_fail() -> None:
    record = load_fixture("raw_response_metadata_valid.json")
    record["request_parameters_safe"]["api_token"] = "should-not-be-stored"

    with pytest.raises(MetadataValidationError, match="sensitive key"):
        validate_raw_response_metadata(record)


def test_invalid_timestamp_fails() -> None:
    record = load_fixture("raw_response_metadata_valid.json")
    record["collected_at"] = "2026-08-05 12:00:00"

    with pytest.raises(MetadataValidationError, match="timezone"):
        validate_raw_response_metadata(record)


def test_invalid_sha256_fails() -> None:
    record = load_fixture("raw_response_metadata_valid.json")
    record["content_hash_sha256"] = "not-a-sha"

    with pytest.raises(MetadataValidationError, match="SHA-256|does not match"):
        validate_raw_response_metadata(record)


def test_raw_storage_path_outside_data_raw_fails() -> None:
    record = load_fixture("raw_response_metadata_valid.json")
    record["raw_storage_path"] = "data/processed/not_raw.html"

    with pytest.raises(MetadataValidationError, match="data/raw"):
        validate_raw_response_metadata(record)


def test_raw_storage_path_with_parent_traversal_fails() -> None:
    record = load_fixture("raw_response_metadata_valid.json")
    record["raw_storage_path"] = "data/raw/../manual/not_raw.html"

    with pytest.raises(MetadataValidationError, match="parent-directory"):
        validate_raw_response_metadata(record)


def test_pending_source_cannot_be_treated_as_approved() -> None:
    with pytest.raises(MetadataValidationError, match="not approved"):
        assert_source_collection_permitted("district")


def test_manual_approved_source_can_be_resolved_for_future_guardrails() -> None:
    row = assert_source_collection_permitted("mud_effects")

    assert row["collection_decision"] == "approved_manual_collection"
    assert row["automation_permission_status"] == "Automated collection prohibited or unsuitable"


def test_missing_source_cannot_be_treated_as_approved() -> None:
    with pytest.raises(MetadataValidationError, match="not in source register"):
        assert_source_collection_permitted("organizer_websites")


def test_organizer_and_calendar_templates_are_not_approved_concrete_sources() -> None:
    for review_file in [
        REVIEWS / "organizer_websites_template.yml",
        REVIEWS / "public_studio_calendars_template.yml",
    ]:
        review = yaml.safe_load(review_file.read_text())
        assert review["is_template"] is True
        assert review["template_status"] == "not_an_approved_source"
        assert review["source_id"] == "template_only"


def test_district_and_bookmyshow_review_records_disallow_bulk_collection() -> None:
    for review_file in [REVIEWS / "district.yml", REVIEWS / "bookmyshow.yml"]:
        review = yaml.safe_load(review_file.read_text())
        decision = review["decision"]
        assert decision["collection_decision"] == "pending_review"
        assert decision["automated_bulk_extraction_approved"] is False
        assert decision["bulk_extraction_approved"] is False
        assert decision["official_api_or_written_permission_identified"] is False


def test_approved_source_would_require_evidence_and_reviewer(tmp_path: Path) -> None:
    source_register = tmp_path / "source_register.csv"
    source_register.write_text(
        "source_id,collection_decision,review_evidence_url,reviewed_by,reviewed_at,"
        "collection_decision_reason,permitted_use_scope,permitted_fields,prohibited_fields,"
        "terms_url,api_documentation_url\n"
        "example,approved_limited_public_collection,,,,,,,,,\n"
    )

    with pytest.raises(MetadataValidationError, match="missing evidence"):
        assert_source_collection_permitted("example", source_register_path=source_register)


def test_collection_run_invalid_timestamp_fails() -> None:
    record = copy.deepcopy(load_fixture("collection_run_metadata_valid.json"))
    record["started_at"] = "2026-08-05"

    with pytest.raises(MetadataValidationError, match="timezone"):
        validate_collection_run_metadata(record)
