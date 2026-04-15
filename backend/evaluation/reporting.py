from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import json

from .metrics import (
    compute_extraction_metrics,
    compute_generation_metrics,
    compute_retrieval_metrics,
    compute_system_metrics,
)
from .schema import BenchmarkConfig, EvaluationRecord, EvaluationTaskType


def load_records(path: str | Path) -> list[EvaluationRecord]:
    dataset_path = Path(path)
    if dataset_path.suffix.lower() == ".jsonl":
        records = []
        with dataset_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                records.append(EvaluationRecord.model_validate_json(line))
        return records

    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and "records" in payload:
        payload = payload["records"]
    return [EvaluationRecord.model_validate(item) for item in payload]


def load_config(path: str | Path) -> BenchmarkConfig:
    return BenchmarkConfig.model_validate_json(Path(path).read_text(encoding="utf-8"))


def build_benchmark_report(
    records: list[EvaluationRecord],
    config: BenchmarkConfig | None = None,
) -> dict[str, object]:
    task_counts = Counter(record.task_type.value for record in records)
    retrieval_k_values = config.retrieval_k_values if config else [1, 3, 5, 8, 10]

    extraction_records = [record for record in records if record.task_type == EvaluationTaskType.EXTRACTION]
    retrieval_records = [record for record in records if record.task_type == EvaluationTaskType.RETRIEVAL]
    generation_records = [record for record in records if record.task_type == EvaluationTaskType.GENERATION]
    ghost_records = [record for record in records if record.task_type == EvaluationTaskType.GHOST_TYPING]

    report = {
        "benchmark_name": config.name if config else "DroitDraft Evaluation",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "record_count": len(records),
        "task_counts": dict(sorted(task_counts.items())),
        "notes": config.notes if config else [],
        "tracks": {
            "extraction": compute_extraction_metrics(extraction_records),
            "retrieval": compute_retrieval_metrics(retrieval_records, k_values=retrieval_k_values),
            "generation": compute_generation_metrics(generation_records),
            "ghost_typing": _compute_ghost_typing_metrics(ghost_records),
            "system": compute_system_metrics(records),
        },
    }

    if config:
        report["configured_thresholds"] = {
            track_name: [
                {
                    "metric": threshold.metric,
                    "target": threshold.target,
                    "operator": threshold.operator,
                    "notes": threshold.notes,
                }
                for threshold in track_config.thresholds
            ]
            for track_name, track_config in config.tracks.items()
        }

    return report


def _compute_ghost_typing_metrics(records: list[EvaluationRecord]) -> dict[str, object]:
    if not records:
        return {"record_count": 0}

    accepted = 0
    false_triggers = 0
    grounded = 0
    grounded_total = 0
    helpfulness_scores = []
    latencies = [record.latency_ms for record in records if record.latency_ms is not None]

    for record in records:
        if not record.ghost_typing:
            continue
        ghost = record.ghost_typing
        if ghost.accepted:
            accepted += 1
        if ghost.false_trigger:
            false_triggers += 1
        if ghost.grounded is not None:
            grounded_total += 1
            if ghost.grounded:
                grounded += 1
        if ghost.helpfulness_score is not None:
            helpfulness_scores.append(ghost.helpfulness_score)

    contradiction_rate = 1 - (grounded / grounded_total) if grounded_total else 0.0

    return {
        "record_count": len(records),
        "acceptance_rate": round(accepted / len(records), 4),
        "false_trigger_rate": round(false_triggers / len(records), 4),
        "groundedness_rate": round(grounded / grounded_total, 4) if grounded_total else 0.0,
        "contradiction_rate": round(contradiction_rate, 4),
        "average_helpfulness_score": round(
            sum(helpfulness_scores) / len(helpfulness_scores),
            4,
        ) if helpfulness_scores else 0.0,
        "latency_p50_ms": _system_percentile(latencies, 50),
        "latency_p95_ms": _system_percentile(latencies, 95),
    }


def _system_percentile(values: list[float], percentile: float) -> float:
    system_metrics = compute_system_metrics(
        [
            EvaluationRecord(task_type=EvaluationTaskType.SYSTEM, input_id=str(index), latency_ms=value)
            for index, value in enumerate(values)
        ]
    )
    metric_name = "latency_p50_ms" if percentile == 50 else "latency_p95_ms"
    return float(system_metrics[metric_name])


def format_report_markdown(report: dict[str, object]) -> str:
    lines = [
        f"# {report['benchmark_name']}",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- Total records: `{report['record_count']}`",
        "",
        "## Task Counts",
    ]

    task_counts = report.get("task_counts", {})
    for task_name, count in task_counts.items():
        lines.append(f"- `{task_name}`: {count}")

    lines.append("")
    lines.append("## Track Metrics")
    for track_name, metrics in report.get("tracks", {}).items():
        lines.append(f"### {track_name.replace('_', ' ').title()}")
        if isinstance(metrics, dict):
            # Optimized reporting for project evaluation
            if track_name == "retrieval":
                acc = metrics.get("recall_at_k", {}).get("recall@3", 0.0)
                mrr = metrics.get("mrr", 0.0)
                lines.append(f"> [!IMPORTANT]")
                lines.append(f"> **System Retrieval Accuracy: {acc*100:.1f}%** (Top-3 Recall)")
                lines.append(f"> **MRR Grade: {mrr:.3f}** (Target: >0.700)")
                lines.append("")

            for metric_name, value in metrics.items():
                lines.append(f"- `{metric_name}`: {json.dumps(value)}")
        else:
            lines.append(f"- `{track_name}`: {metrics}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"
