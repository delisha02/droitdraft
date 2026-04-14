from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from evaluation.reporting import (  # noqa: E402
    build_benchmark_report,
    format_report_markdown,
    load_config,
    load_records,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the DroitDraft evaluation harness.")
    parser.add_argument("--dataset", required=True, help="Path to a JSON or JSONL evaluation dataset.")
    parser.add_argument(
        "--config",
        default=str(BACKEND_DIR / "evaluation" / "benchmark_config.json"),
        help="Optional benchmark config JSON.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Output format for the generated report.",
    )
    args = parser.parse_args()

    records = load_records(args.dataset)
    config = load_config(args.config) if args.config else None
    report = build_benchmark_report(records, config=config)

    if args.format == "markdown":
        sys.stdout.write(format_report_markdown(report))
    else:
        sys.stdout.write(json.dumps(report, indent=2))
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
