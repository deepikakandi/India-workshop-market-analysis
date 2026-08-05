#!/usr/bin/env python3
"""Validate a manual event-record CSV batch without network access."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from workshop_market.quality.manual_batch import validate_manual_csv


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate manual event-record CSV rows.")
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    args = parser.parse_args()

    result = validate_manual_csv(args.csv_path)
    payload = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n")
    print(payload)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
