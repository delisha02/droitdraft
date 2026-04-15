# DroitDraft Recommended Evaluation v1

- Generated at: `2026-04-14T18:07:27.085711+00:00`
- Total records: `150`

## Task Counts
- `extraction`: 30
- `generation`: 30
- `ghost_typing`: 30
- `retrieval`: 30
- `system`: 30

## Track Metrics
### Extraction
- `record_count`: 30
- `micro_precision`: 0.0
- `micro_recall`: 0.0
- `micro_f1`: 0.0
- `document_exact_match_rate`: 0.0
- `required_field_completion_rate`: 0.0
- `human_correction_rate`: 0.0
- `per_field`: {"location": {"precision": 0.0, "recall": 0.0, "f1": 0.0}, "person": {"precision": 0.0, "recall": 0.0, "f1": 0.0}}

### Retrieval
- `record_count`: 30
- `ranking_record_count`: 30
- `negative_record_count`: 0
- `mrr`: 0.0333
- `citation_precision`: 0.0
- `citation_hallucination_rate`: 0.0
- `no_answer_accuracy`: 0.0
- `answer_faithfulness`: 0.95
- `recall_at_k`: {"recall@1": 0.0333, "recall@3": 0.0333, "recall@5": 0.0333, "recall@8": 0.0333, "recall@10": 0.0333}
- `hits_at_k`: {"hits@1": {"exact": 0.0333, "robust": 0.0333, "rate": 0.0333}, "hits@3": {"exact": 0.0333, "robust": 0.0333, "rate": 0.0333}, "hits@5": {"exact": 0.0333, "robust": 0.0333, "rate": 0.0333}, "hits@8": {"exact": 0.0333, "robust": 0.0333, "rate": 0.0333}, "hits@10": {"exact": 0.0333, "robust": 0.0333, "rate": 0.0333}}

### Generation
- `record_count`: 30
- `field_accuracy`: 1.0
- `factual_consistency_rate`: 1.0
- `required_clause_completion_rate`: 0.0
- `citation_coverage`: 0.0
- `validation_pass_rate`: 0.0
- `human_correction_rate`: 0.0
- `average_bertscore_f1`: 0.92
- `average_rouge_l`: 0.75
- `confidence_routing`: {"mandatory_review": 0.0, "recommended_review": 0.0, "spot_audit": 0.0}

### Ghost Typing
- `record_count`: 30
- `acceptance_rate`: 1.0
- `false_trigger_rate`: 0.0
- `groundedness_rate`: 0.0
- `contradiction_rate`: 0.0
- `average_helpfulness_score`: 4.0
- `latency_p50_ms`: 1161.947
- `latency_p95_ms`: 5514.1792

### System
- `record_count`: 150
- `latency_p50_ms`: 1161.947
- `latency_p95_ms`: 11936.7561
- `failure_rate`: 0.0
- `api_error_rate`: 0.0
- `average_pages_per_minute`: 10.0
- `average_throughput_per_minute`: 15.0
- `average_cost_per_request`: 0.0
