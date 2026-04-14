# DroitDraft Evaluation Toolkit

This folder contains a standalone benchmark harness for the DroitDraft evaluation plan.

## What is included

- `schema.py`: Pydantic models for benchmark records and benchmark config
- `metrics.py`: Metric calculators for extraction, retrieval, generation, ghost typing, and system benchmarks
- `reporting.py`: Dataset loading and report generation helpers
- `benchmark_config.json`: The recommended thresholds and dataset parameters from the evaluation plan
- `sample_records.jsonl`: A small example dataset to smoke-test the harness

## Dataset format

The harness accepts either:

- `JSONL`: one `EvaluationRecord` per line
- `JSON`: a list of records or an object with a top-level `records` array

Core record fields:

- `task_type`
- `input_id`
- `document_type`
- `query_or_prompt`
- `gold_labels`
- `prediction`
- `retrieval_sources`
- `citation_checks`
- `validation_report`
- `confidence_score`
- `latency_ms`
- `review_required`
- `human_score`
- `pass_fail`

Track-specific fields:

- `extraction_fields`
- `retrieval_judgment`
- `generation_fields`
- `clause_checks`
- `ghost_typing`
- `operational_metrics`

## Running the benchmark

From the repo root:

```powershell
.\.venv\Scripts\python.exe backend\scripts\run_evaluation.py `
  --dataset backend\evaluation\sample_records.jsonl `
  --config backend\evaluation\benchmark_config.json `
  --format markdown
```

## Recommended use

1. Build a labeled benchmark dataset for each track.
2. Export runtime outputs from extraction, research, generation, and ghost typing into `EvaluationRecord` format.
3. Run the benchmark after major retrieval, prompting, or validation changes.
4. Track the report over time to watch regression in legal grounding, citation behavior, and latency.
