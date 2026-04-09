# DroitDraft Evaluation Framework

This document operationalizes the recommended evaluation plan for DroitDraft as a benchmark harness plus dataset definition.

## Evaluation tracks

1. **Document extraction and fact structuring**
2. **Legal retrieval and research**
3. **Draft generation quality**
4. **Ghost typing and UX performance**
5. **System and operational quality**

## Implemented artifacts

- Standalone benchmark package: `backend/evaluation`
- Benchmark config with thresholds and dataset guidance: `backend/evaluation/benchmark_config.json`
- Sample benchmark dataset: `backend/evaluation/sample_records.jsonl`
- CLI runner: `backend/scripts/run_evaluation.py`
- Reproducible backend env template: `backend/.env.example`

## Metric mapping

### Extraction

- Field-level `precision`, `recall`, `F1`
- Document exact match rate
- Required-field completion rate
- Human correction rate

### Retrieval

- `MRR`
- `Recall@k`
- `Hits@k Exact`
- `Hits@k Robust`
- `Hits@k Rate`
- Citation precision
- Citation hallucination rate
- No-answer accuracy
- Faithfulness score

### Generation

- Required clause completion rate
- Field accuracy
- Factual consistency rate
- Citation coverage
- Validation pass rate
- Human correction rate
- Average `BERTScore F1`
- Average `ROUGE-L`
- Confidence routing distribution

### Ghost typing

- Acceptance rate
- False-trigger rate
- Groundedness rate
- Contradiction rate
- Helpfulness score
- Latency `p50` and `p95`

### System

- Latency `p50` and `p95`
- Failure rate
- API error rate
- Average pages per minute
- Average throughput per minute
- Average cost per request

## How to use it

1. Export benchmark cases in the `EvaluationRecord` format.
2. Run the evaluation CLI against the dataset.
3. Compare the report against the configured thresholds.
4. Keep the benchmark under version control so retrieval, prompting, and validation changes can be regression-tested.

## Current design choice

The benchmark package is intentionally outside `backend/app` so it can run without importing the full FastAPI runtime or requiring production environment settings during simple offline evaluation.
