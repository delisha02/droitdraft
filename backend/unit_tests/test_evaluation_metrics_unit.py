from pathlib import Path
import sys


_BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from evaluation import metrics, reporting, schema  # noqa: E402


def test_compute_extraction_metrics_reports_micro_scores_and_exact_match():
    records = [
        schema.EvaluationRecord(
            task_type=schema.EvaluationTaskType.EXTRACTION,
            input_id="extract-1",
            human_corrected=False,
            extraction_fields=[
                schema.ExtractionFieldResult(
                    field_name="person",
                    gold_values=["Ramesh Kumar"],
                    predicted_values=["Ramesh Kumar"],
                    required=True,
                ),
                schema.ExtractionFieldResult(
                    field_name="date",
                    gold_values=["2025-12-12"],
                    predicted_values=["2025-12-12"],
                    required=True,
                ),
            ],
        ),
        schema.EvaluationRecord(
            task_type=schema.EvaluationTaskType.EXTRACTION,
            input_id="extract-2",
            human_corrected=True,
            extraction_fields=[
                schema.ExtractionFieldResult(
                    field_name="person",
                    gold_values=["Sunita Kumar"],
                    predicted_values=["Sunita Kumar"],
                    required=True,
                ),
                schema.ExtractionFieldResult(
                    field_name="location",
                    gold_values=["Pune"],
                    predicted_values=[],
                    required=True,
                ),
            ],
        ),
    ]

    result = metrics.compute_extraction_metrics(records)

    assert result["record_count"] == 2
    assert result["micro_precision"] == 1.0
    assert result["micro_recall"] == 0.75
    assert result["micro_f1"] == 0.8571
    assert result["document_exact_match_rate"] == 0.5
    assert result["required_field_completion_rate"] == 0.75
    assert result["human_correction_rate"] == 0.5


def test_compute_retrieval_metrics_reports_mrr_hits_and_no_answer_accuracy():
    records = [
        schema.EvaluationRecord(
            task_type=schema.EvaluationTaskType.RETRIEVAL,
            input_id="ret-1",
            retrieval_judgment=schema.RetrievalJudgment(
                relevant_source_ids=["act-1", "case-2"],
                retrieved_source_ids=["case-2", "other-1", "act-1"],
                cited_source_ids=["case-2"],
                faithfulness_score=0.9,
            ),
        ),
        schema.EvaluationRecord(
            task_type=schema.EvaluationTaskType.RETRIEVAL,
            input_id="ret-2",
            retrieval_judgment=schema.RetrievalJudgment(
                relevant_source_ids=[],
                retrieved_source_ids=[],
                cited_source_ids=[],
                expected_no_answer=True,
                returned_no_answer=True,
                faithfulness_score=1.0,
            ),
        ),
    ]

    result = metrics.compute_retrieval_metrics(records, k_values=[1, 3])

    assert result["record_count"] == 2
    assert result["ranking_record_count"] == 1
    assert result["negative_record_count"] == 1
    assert result["mrr"] == 1.0
    assert result["citation_precision"] == 1.0
    assert result["no_answer_accuracy"] == 1.0
    assert result["recall_at_k"]["recall@1"] == 0.5
    assert result["hits_at_k"]["hits@3"]["exact"] == 1.0


def test_compute_generation_metrics_reports_clause_field_and_routing_metrics():
    records = [
        schema.EvaluationRecord(
            task_type=schema.EvaluationTaskType.GENERATION,
            input_id="gen-1",
            confidence_score=0.74,
            human_corrected=True,
            validation_report={"passed": False},
            automatic_scores={"bertscore_f1": 0.92, "rouge_l": 0.7},
            generation_fields=[
                schema.FieldMatchResult(field_name="amount", matched=True, category="factual"),
                schema.FieldMatchResult(field_name="date", matched=False, category="factual"),
            ],
            clause_checks=[
                schema.ClauseEvaluation(clause_id="C1", required=True, present=True, requires_citation=True, has_citation=True),
                schema.ClauseEvaluation(clause_id="C2", required=True, present=False, requires_citation=True, has_citation=False),
            ],
        ),
        schema.EvaluationRecord(
            task_type=schema.EvaluationTaskType.GENERATION,
            input_id="gen-2",
            confidence_score=0.9,
            human_corrected=False,
            validation_report={"passed": True},
            automatic_scores={"bertscore_f1": 0.96, "rouge_l": 0.8},
            generation_fields=[
                schema.FieldMatchResult(field_name="amount", matched=True, category="factual"),
                schema.FieldMatchResult(field_name="statute", matched=True, category="factual"),
            ],
            clause_checks=[
                schema.ClauseEvaluation(clause_id="C1", required=True, present=True, requires_citation=True, has_citation=True),
            ],
        ),
    ]

    result = metrics.compute_generation_metrics(records)

    assert result["record_count"] == 2
    assert result["field_accuracy"] == 0.75
    assert result["factual_consistency_rate"] == 0.75
    assert result["required_clause_completion_rate"] == 0.6667
    assert result["citation_coverage"] == 0.6667
    assert result["validation_pass_rate"] == 0.5
    assert result["human_correction_rate"] == 0.5
    assert result["average_bertscore_f1"] == 0.94
    assert result["average_rouge_l"] == 0.75
    assert result["confidence_routing"]["mandatory_review"] == 0.5
    assert result["confidence_routing"]["spot_audit"] == 0.5


def test_build_benchmark_report_loads_configured_k_values_and_formats_markdown():
    records = [
        schema.EvaluationRecord(
            task_type=schema.EvaluationTaskType.GHOST_TYPING,
            input_id="ghost-1",
            latency_ms=200,
            ghost_typing=schema.GhostTypingEvaluation(
                accepted=True,
                false_trigger=False,
                grounded=True,
                helpfulness_score=4.0,
            ),
        )
    ]

    config = schema.BenchmarkConfig(
        name="Test Benchmark",
        summary="summary",
        retrieval_k_values=[1, 5],
    )

    report = reporting.build_benchmark_report(records, config=config)
    markdown = reporting.format_report_markdown(report)

    assert report["benchmark_name"] == "Test Benchmark"
    assert report["tracks"]["ghost_typing"]["acceptance_rate"] == 1.0
    assert "Ghost Typing" in markdown
