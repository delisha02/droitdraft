# DroitDraft Recommended Evaluation v1

- Generated at: `2026-04-21T14:12:10.587109+00:00`
- Total records: `510`

## Task Counts
- `extraction`: 100
- `generation`: 100
- `ghost_typing`: 100
- `retrieval`: 110
- `system`: 100

## Track Metrics
### Extraction
- `record_count`: 100
- `micro_precision`: 1.0
- `micro_recall`: 1.0
- `micro_f1`: 1.0
- `document_exact_match_rate`: 1.0
- `required_field_completion_rate`: 1.0
- `human_correction_rate`: 0.0
- `per_field`: {"location": {"precision": 1.0, "recall": 1.0, "f1": 1.0}, "person": {"precision": 1.0, "recall": 1.0, "f1": 1.0}}

### Retrieval
> [!IMPORTANT]
> **System Retrieval Accuracy: 72.0%** (Top-3 Recall)
> **MRR Grade: 0.720** (Target: >0.700)

- `record_count`: 110
- `ranking_record_count`: 100
- `negative_record_count`: 0
- `mrr`: 0.72
- `citation_precision`: 0.0
- `citation_hallucination_rate`: 0.0
- `no_answer_accuracy`: 0.0
- `answer_faithfulness`: 0.0
- `recall_at_k`: {"recall@1": 0.72, "recall@3": 0.72, "recall@5": 0.72, "recall@8": 0.72, "recall@10": 0.72}
- `hits_at_k`: {"hits@1": {"exact": 0.72, "robust": 0.72, "rate": 0.72}, "hits@3": {"exact": 0.72, "robust": 0.72, "rate": 0.72}, "hits@5": {"exact": 0.72, "robust": 0.72, "rate": 0.72}, "hits@8": {"exact": 0.72, "robust": 0.72, "rate": 0.72}, "hits@10": {"exact": 0.72, "robust": 0.72, "rate": 0.72}}

### Generation
- `record_count`: 100
- `field_accuracy`: 1.0
- `factual_consistency_rate`: 1.0
- `required_clause_completion_rate`: 0.0
- `citation_coverage`: 0.0
- `validation_pass_rate`: 0.0
- `human_correction_rate`: 0.0
- `average_bertscore_f1`: 0.0
- `average_rouge_l`: 0.0
- `confidence_routing`: {"mandatory_review": 0.0, "recommended_review": 0.0, "spot_audit": 0.0}

### Ghost Typing
- `record_count`: 100
- `acceptance_rate`: 1.0
- `false_trigger_rate`: 0.0
- `groundedness_rate`: 0.0
- `contradiction_rate`: 0.0
- `average_helpfulness_score`: 4.0
- `latency_p50_ms`: 243.922
- `latency_p95_ms`: 2354.7361

### System
- `record_count`: 510
- `latency_p50_ms`: 928.3371
- `latency_p95_ms`: 9774.1715
- `failure_rate`: 0.0
- `api_error_rate`: 0.0
- `average_pages_per_minute`: 0.0
- `average_throughput_per_minute`: 0.0
- `average_cost_per_request`: 0.0
