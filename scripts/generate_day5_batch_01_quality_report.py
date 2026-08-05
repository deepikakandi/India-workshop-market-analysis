#!/usr/bin/env python3
"""Generate the Day 5 Batch 01 quality report without network access."""

from __future__ import annotations

import argparse
from pathlib import Path

from workshop_market.quality.manual_batch import (
    infer_observation_batch_date,
    parse_analysis_date,
    quality_report,
    write_quality_report,
)

CSV_PATH = Path("data/manual/observations/2026-08-05/pilot_event_records_batch_01.csv")
JSON_PATH = Path("reports/exports/day5_batch_01_quality_report.json")
MD_PATH = Path("reports/exports/day5_batch_01_quality_report.md")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Day 5 Batch 01 quality reports.")
    parser.add_argument("--csv-path", type=Path, default=CSV_PATH)
    parser.add_argument("--json-output", type=Path, default=JSON_PATH)
    parser.add_argument("--markdown-output", type=Path, default=MD_PATH)
    parser.add_argument("--as-of-date", required=True, help="Explicit YYYY-MM-DD analysis date")
    parser.add_argument(
        "--observation-batch-date",
        help="Explicit YYYY-MM-DD observation batch date; defaults to the CSV parent folder name",
    )
    args = parser.parse_args()

    as_of_date = parse_analysis_date(args.as_of_date)
    observation_batch_date = args.observation_batch_date or infer_observation_batch_date(args.csv_path)
    parse_analysis_date(observation_batch_date)

    report = quality_report(
        args.csv_path,
        as_of_date=as_of_date,
        observation_batch_date=observation_batch_date,
    )
    write_quality_report(report, args.json_output, args.markdown_output)
    print(f"wrote {args.json_output}")
    print(f"wrote {args.markdown_output}")
    return 0 if report["invalid_records"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
