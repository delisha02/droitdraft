import re
from math import ceil, floor

from .schema import EvaluationRecord


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = ((len(ordered) - 1) * percentile) / 100
    lower = floor(position)
    upper = ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * weight


def _normalize_value(value: object) -> str:
    text = "" if value is None else str(value)
    return " ".join(text.strip().lower().split())


def _is_robust_hit(gold: str, retrieved: str) -> bool:
    """Checks if predicted string significantly overlaps with gold string tokens."""
    def tokenize(s):
        return set(re.findall(r'\w+', s.lower()))
    
    g_tokens = tokenize(gold)
    r_tokens = tokenize(retrieved)
    
    if not g_tokens:
        return False
        
    overlap = g_tokens.intersection(r_tokens)
    # 70% overlap threshold for legal naming variations (e.g. BNS vs Bhartiya Nyaya Sanhita)
    return len(overlap) / len(g_tokens) >= 0.7 or g_tokens.issubset(r_tokens) or r_tokens.issubset(g_tokens)


def _normalize_values(values: list[str]) -> set[str]:
    return {normalized for normalized in (_normalize_value(value) for value in values) if normalized}


def compute_precision_recall_f1(tp: int, fp: int, fn: int) -> dict[str, float]:
    precision = _safe_divide(tp, tp + fp)
    recall = _safe_divide(tp, tp + fn)
    f1 = _safe_divide(2 * precision * recall, precision + recall) if precision or recall else 0.0
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def compute_extraction_metrics(records: list[EvaluationRecord]) -> dict[str, object]:
    extraction_records = [record for record in records if record.extraction_fields]
    if not extraction_records:
        return {"record_count": 0}

    total_tp = total_fp = total_fn = 0
    exact_matches = 0
    required_fields_present = 0
    required_fields_total = 0
    corrected_records = 0
    per_field_counts: dict[str, dict[str, int]] = {}

    for record in extraction_records:
        document_exact = True
        if record.human_corrected:
            corrected_records += 1

        for field in record.extraction_fields:
            gold = _normalize_values(field.gold_values)
            predicted = _normalize_values(field.predicted_values)
            tp = len(gold & predicted)
            fp = len(predicted - gold)
            fn = len(gold - predicted)
            total_tp += tp
            total_fp += fp
            total_fn += fn

            if gold != predicted:
                document_exact = False

            if field.required:
                required_fields_total += 1
                if predicted:
                    required_fields_present += 1

            stats = per_field_counts.setdefault(field.field_name, {"tp": 0, "fp": 0, "fn": 0})
            stats["tp"] += tp
            stats["fp"] += fp
            stats["fn"] += fn

        if document_exact:
            exact_matches += 1

    per_field_metrics = {
        field_name: compute_precision_recall_f1(stats["tp"], stats["fp"], stats["fn"])
        for field_name, stats in sorted(per_field_counts.items())
    }
    micro_metrics = compute_precision_recall_f1(total_tp, total_fp, total_fn)

    return {
        "record_count": len(extraction_records),
        "micro_precision": micro_metrics["precision"],
        "micro_recall": micro_metrics["recall"],
        "micro_f1": micro_metrics["f1"],
        "document_exact_match_rate": round(_safe_divide(exact_matches, len(extraction_records)), 4),
        "required_field_completion_rate": round(
            _safe_divide(required_fields_present, required_fields_total),
            4,
        ),
        "human_correction_rate": round(_safe_divide(corrected_records, len(extraction_records)), 4),
        "per_field": per_field_metrics,
    }


def compute_retrieval_metrics(
    records: list[EvaluationRecord],
    *,
    k_values: list[int] | tuple[int, ...] = (1, 3, 5, 8, 10),
) -> dict[str, object]:
    retrieval_records = [record for record in records if record.retrieval_judgment is not None]
    if not retrieval_records:
        return {"record_count": 0}

    ranking_records = []
    negative_records = []
    reciprocal_ranks = []
    citation_tp = citation_fp = 0
    faithfulness_scores = []

    hits: dict[int, dict[str, float]] = {
        k: {"exact_total": 0.0, "robust_total": 0.0, "rate_total": 0.0, "recall_total": 0.0}
        for k in k_values
    }

    for record in retrieval_records:
        judgment = record.retrieval_judgment
        assert judgment is not None
        relevant = [_normalize_value(value) for value in judgment.relevant_source_ids if _normalize_value(value)]
        retrieved = [_normalize_value(value) for value in judgment.retrieved_source_ids if _normalize_value(value)]
        cited = [_normalize_value(value) for value in judgment.cited_source_ids if _normalize_value(value)]

        if judgment.faithfulness_score is not None:
            faithfulness_scores.append(judgment.faithfulness_score)

        relevant_set = set(relevant)
        if not relevant_set and judgment.expected_no_answer:
            negative_records.append(judgment)
        elif relevant_set:
            ranking_records.append(judgment)

            hit_at_rank = 0
            for rank, retrieved_id in enumerate(retrieved, 1):
                is_hit = False
                for r_id in relevant:
                    if r_id == retrieved_id or _is_robust_hit(r_id, retrieved_id):
                        is_hit = True
                        break
                
                if is_hit:
                    hit_at_rank = rank
                    break

            if hit_at_rank > 0:
                reciprocal_ranks.append(1.0 / hit_at_rank)
                for k in k_values:
                    if hit_at_rank <= k:
                        hits[k]["exact_total"] += 1.0
                        hits[k]["robust_total"] += 1.0
                        hits[k]["rate_total"] += 1.0
                        hits[k]["recall_total"] += 1.0
            else:
                reciprocal_ranks.append(0.0)

        for source_id in cited:
            if source_id in relevant_set:
                citation_tp += 1
            else:
                citation_fp += 1

    no_answer_correct = 0
    for judgment in negative_records:
        if judgment.returned_no_answer == judgment.expected_no_answer:
            no_answer_correct += 1

    recall_at_k = {
        f"recall@{k}": round(_safe_divide(bucket["recall_total"], len(ranking_records)), 4)
        for k, bucket in hits.items()
    }
    hits_at_k = {
        f"hits@{k}": {
            "exact": round(_safe_divide(bucket["exact_total"], len(ranking_records)), 4),
            "robust": round(_safe_divide(bucket["robust_total"], len(ranking_records)), 4),
            "rate": round(_safe_divide(bucket["rate_total"], len(ranking_records)), 4),
        }
        for k, bucket in hits.items()
    }

    citation_precision = _safe_divide(citation_tp, citation_tp + citation_fp)

    return {
        "record_count": len(retrieval_records),
        "ranking_record_count": len(ranking_records),
        "negative_record_count": len(negative_records),
        "mrr": round(_safe_divide(sum(reciprocal_ranks), len(ranking_records)), 4),
        "citation_precision": round(citation_precision, 4),
        "citation_hallucination_rate": round(1 - citation_precision, 4) if (citation_tp + citation_fp) else 0.0,
        "no_answer_accuracy": round(_safe_divide(no_answer_correct, len(negative_records)), 4),
        "answer_faithfulness": round(_safe_divide(sum(faithfulness_scores), len(faithfulness_scores)), 4),
        "recall_at_k": recall_at_k,
        "hits_at_k": hits_at_k,
    }


def compute_generation_metrics(records: list[EvaluationRecord]) -> dict[str, object]:
    generation_records = [
        record
        for record in records
        if record.generation_fields or record.clause_checks or record.validation_report
    ]
    if not generation_records:
        return {"record_count": 0}

    matched_fields = total_fields = 0
    matched_factual_fields = total_factual_fields = 0
    required_clauses_present = total_required_clauses = 0
    citation_ready_clauses = total_citation_required_clauses = 0
    validation_passes = validation_total = 0
    corrected_records = 0
    bert_scores = []
    rouge_scores = []

    routing_buckets = {
        "mandatory_review": 0,
        "recommended_review": 0,
        "spot_audit": 0,
    }

    for record in generation_records:
        if record.human_corrected:
            corrected_records += 1

        if record.confidence_score is not None:
            if record.confidence_score < 0.75:
                routing_buckets["mandatory_review"] += 1
            elif record.confidence_score < 0.85:
                routing_buckets["recommended_review"] += 1
            else:
                routing_buckets["spot_audit"] += 1

        if "bertscore_f1" in record.automatic_scores:
            bert_scores.append(record.automatic_scores["bertscore_f1"])
        if "rouge_l" in record.automatic_scores:
            rouge_scores.append(record.automatic_scores["rouge_l"])

        for field in record.generation_fields:
            total_fields += 1
            if field.matched:
                matched_fields += 1

            is_factual = field.category in {None, "factual", "slot"}
            if is_factual:
                total_factual_fields += 1
                if field.matched:
                    matched_factual_fields += 1

        for clause in record.clause_checks:
            if clause.required:
                total_required_clauses += 1
                if clause.present:
                    required_clauses_present += 1
            if clause.requires_citation:
                total_citation_required_clauses += 1
                if clause.has_citation:
                    citation_ready_clauses += 1

        if record.validation_report:
            validation_total += 1
            if record.validation_report.get("passed") is True:
                validation_passes += 1

    return {
        "record_count": len(generation_records),
        "field_accuracy": round(_safe_divide(matched_fields, total_fields), 4),
        "factual_consistency_rate": round(
            _safe_divide(matched_factual_fields, total_factual_fields),
            4,
        ),
        "required_clause_completion_rate": round(
            _safe_divide(required_clauses_present, total_required_clauses),
            4,
        ),
        "citation_coverage": round(
            _safe_divide(citation_ready_clauses, total_citation_required_clauses),
            4,
        ),
        "validation_pass_rate": round(_safe_divide(validation_passes, validation_total), 4),
        "human_correction_rate": round(_safe_divide(corrected_records, len(generation_records)), 4),
        "average_bertscore_f1": round(_safe_divide(sum(bert_scores), len(bert_scores)), 4),
        "average_rouge_l": round(_safe_divide(sum(rouge_scores), len(rouge_scores)), 4),
        "confidence_routing": {
            bucket: round(_safe_divide(count, len(generation_records)), 4)
            for bucket, count in routing_buckets.items()
        },
    }


def compute_system_metrics(records: list[EvaluationRecord]) -> dict[str, object]:
    if not records:
        return {"record_count": 0}

    latencies = [record.latency_ms for record in records if record.latency_ms is not None]
    failure_flags = [record.pass_fail for record in records if record.pass_fail is not None]
    pages_per_minute = []
    throughput = []
    costs = []
    api_errors = 0

    for record in records:
        metrics = record.operational_metrics
        if not metrics:
            continue
        if metrics.pages_per_minute is not None:
            pages_per_minute.append(metrics.pages_per_minute)
        if metrics.throughput_per_minute is not None:
            throughput.append(metrics.throughput_per_minute)
        if metrics.cost_per_request is not None:
            costs.append(metrics.cost_per_request)
        if metrics.api_error:
            api_errors += 1

    passed_count = sum(1 for flag in failure_flags if flag)
    failure_rate = 1 - _safe_divide(passed_count, len(failure_flags)) if failure_flags else 0.0

    return {
        "record_count": len(records),
        "latency_p50_ms": round(_percentile(latencies, 50) or 0.0, 4),
        "latency_p95_ms": round(_percentile(latencies, 95) or 0.0, 4),
        "failure_rate": round(failure_rate, 4),
        "api_error_rate": round(_safe_divide(api_errors, len(records)), 4),
        "average_pages_per_minute": round(_safe_divide(sum(pages_per_minute), len(pages_per_minute)), 4),
        "average_throughput_per_minute": round(_safe_divide(sum(throughput), len(throughput)), 4),
        "average_cost_per_request": round(_safe_divide(sum(costs), len(costs)), 4),
    }
