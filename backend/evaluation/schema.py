from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EvaluationTaskType(str, Enum):
    EXTRACTION = "extraction"
    RETRIEVAL = "retrieval"
    GENERATION = "generation"
    GHOST_TYPING = "ghost_typing"
    SYSTEM = "system"


class ExtractionFieldResult(BaseModel):
    field_name: str
    gold_values: list[str] = Field(default_factory=list)
    predicted_values: list[str] = Field(default_factory=list)
    required: bool = False
    category: str | None = None


class RetrievalJudgment(BaseModel):
    relevant_source_ids: list[str] = Field(default_factory=list)
    retrieved_source_ids: list[str] = Field(default_factory=list)
    cited_source_ids: list[str] = Field(default_factory=list)
    expected_no_answer: bool = False
    returned_no_answer: bool = False
    faithfulness_score: float | None = Field(default=None, ge=0.0, le=1.0)


class FieldMatchResult(BaseModel):
    field_name: str
    expected_value: Any = None
    predicted_value: Any = None
    matched: bool | None = None
    category: str | None = None
    required: bool = True


class ClauseEvaluation(BaseModel):
    clause_id: str
    required: bool = True
    present: bool = False
    requires_citation: bool = False
    has_citation: bool = False


class GhostTypingEvaluation(BaseModel):
    accepted: bool | None = None
    false_trigger: bool = False
    grounded: bool | None = None
    helpfulness_score: float | None = Field(default=None, ge=0.0, le=5.0)


class OperationalMetrics(BaseModel):
    pages_per_minute: float | None = Field(default=None, ge=0.0)
    throughput_per_minute: float | None = Field(default=None, ge=0.0)
    cost_per_request: float | None = Field(default=None, ge=0.0)
    api_error: bool = False


class EvaluationRecord(BaseModel):
    task_type: EvaluationTaskType
    input_id: str
    document_type: str | None = None
    query_or_prompt: str | None = None
    gold_labels: dict[str, Any] = Field(default_factory=dict)
    prediction: dict[str, Any] = Field(default_factory=dict)
    retrieval_sources: list[dict[str, Any]] = Field(default_factory=list)
    citation_checks: dict[str, Any] = Field(default_factory=dict)
    validation_report: dict[str, Any] = Field(default_factory=dict)
    confidence_score: float | None = Field(default=None, ge=0.0, le=1.0)
    latency_ms: float | None = Field(default=None, ge=0.0)
    review_required: bool = False
    human_corrected: bool | None = None
    human_score: float | None = Field(default=None, ge=0.0, le=5.0)
    pass_fail: bool | None = None
    automatic_scores: dict[str, float] = Field(default_factory=dict)
    extraction_fields: list[ExtractionFieldResult] = Field(default_factory=list)
    retrieval_judgment: RetrievalJudgment | None = None
    generation_fields: list[FieldMatchResult] = Field(default_factory=list)
    clause_checks: list[ClauseEvaluation] = Field(default_factory=list)
    ghost_typing: GhostTypingEvaluation | None = None
    operational_metrics: OperationalMetrics | None = None


class DatasetSplitDefinition(BaseModel):
    train: float
    dev: float
    test: float
    holdout_description: str | None = None


class BenchmarkDatasetDefinition(BaseModel):
    track: EvaluationTaskType
    minimum_samples: int
    categories: list[str] = Field(default_factory=list)
    split: DatasetSplitDefinition | None = None
    notes: str | None = None


class MetricThreshold(BaseModel):
    metric: str
    target: float
    operator: str = ">="
    notes: str | None = None


class BenchmarkTrackConfig(BaseModel):
    thresholds: list[MetricThreshold] = Field(default_factory=list)
    dataset: BenchmarkDatasetDefinition | None = None
    operational_defaults: dict[str, Any] = Field(default_factory=dict)


class BenchmarkConfig(BaseModel):
    name: str
    summary: str
    retrieval_k_values: list[int] = Field(default_factory=lambda: [1, 3, 5, 8, 10])
    tracks: dict[str, BenchmarkTrackConfig] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)
