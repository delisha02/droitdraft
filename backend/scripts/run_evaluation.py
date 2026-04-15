import argparse
import asyncio
import json
from pathlib import Path
import sys
import os

# Ensure backend root is in path
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Explicitly load .env from the backend directory before importing app modules
try:
    from dotenv import load_dotenv
    load_dotenv(BACKEND_DIR / ".env")
except ImportError:
    pass

from evaluation.reporting import (  # noqa: E402
    build_benchmark_report,
    format_report_markdown,
    load_config,
    load_records,
)
from evaluation.runner import LiveBenchmarkRunner # noqa: E402


async def main() -> int:
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
    parser.add_argument(
        "--execute",
        action="store_true",
        help="If set, executes live inference against the system before reporting.",
    )
    parser.add_argument(
        "--output",
        help="Optional file path to save the generated report.",
    )
    parser.add_argument(
        "--save-results",
        help="Optional file path to save the executed records (with live predictions).",
    )
    args = parser.parse_args()

    records = load_records(args.dataset)
    
    if args.execute:
        print(">>> Starting Live Execution Benchmarking...")
        runner = LiveBenchmarkRunner()
        records = await runner.execute_all(records)
        
        if args.save_results:
            save_path = Path(args.save_results)
            with open(save_path, "w", encoding="utf-8") as f:
                for record in records:
                    f.write(record.model_dump_json() + "\n")
            print(f">>> Executed records saved to {save_path}")

    config = load_config(args.config) if args.config else None
    report = build_benchmark_report(records, config=config)

    output_content = ""
    if args.format == "markdown":
        output_content = format_report_markdown(report)
    else:
        output_content = json.dumps(report, indent=2) + "\n"

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_content)
        print(f">>> Report saved to {output_path}")
    else:
        sys.stdout.write(output_content)

    return 0


if __name__ == "__main__":
    asyncio.run(main())
