"""Evaluation models for TurnWise SDK."""
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel, Field

from .enums import EvaluationLevel, OutputType


class Metric(BaseModel):
    """Definition of an evaluation metric."""

    name: str
    prompt: str
    evaluation_level: EvaluationLevel = EvaluationLevel.MESSAGE
    output_type: OutputType = OutputType.PROGRESS
    description: Optional[str] = None
    output_schema: Optional[Dict[str, Any]] = None
    model_name: str = "openai/gpt-4o-mini"
    aggregate_results: bool = False

    # Set after registration with TurnWise
    pipeline_id: Optional[int] = None
    node_id: Optional[int] = None

    def is_registered(self) -> bool:
        """Check if this metric is registered with TurnWise."""
        return self.node_id is not None


class EvaluationResult(BaseModel):
    """Result of a single evaluation."""

    entity_type: EvaluationLevel
    entity_id: int
    pipeline_node_id: int
    result: Dict[str, Any]
    execution_time: Optional[float] = None
    meta: Optional[Dict[str, Any]] = None

    def get_score(self) -> Optional[float]:
        """Get the score from the result if it exists."""
        if "score" in self.result:
            return float(self.result["score"])
        if "value" in self.result:
            return float(self.result["value"])
        return None


class EvaluationProgress(BaseModel):
    """Progress information during evaluation."""

    completed: int = 0
    total: int = 0
    current_item: Optional[str] = None

    @property
    def percentage(self) -> float:
        """Get completion percentage."""
        if self.total == 0:
            return 0.0
        return (self.completed / self.total) * 100


class EvaluationConfig(BaseModel):
    """Configuration for running evaluations."""

    max_concurrent: int = 3
    timeout_seconds: int = 120
    retry_attempts: int = 2
    extract_goals: bool = True
    create_summaries: bool = True


class PipelineNode(BaseModel):
    """An evaluation pipeline node (metric) from TurnWise."""

    id: int
    pipeline_id: int
    name: str
    description: Optional[str] = None
    prompt: str
    model_name: str
    evaluation_level: EvaluationLevel
    output_type: Optional[OutputType] = None
    output_schema: Optional[Dict[str, Any]] = None
    aggregate_results: bool = False


class Pipeline(BaseModel):
    """An evaluation pipeline from TurnWise."""

    id: int
    name: str
    description: Optional[str] = None
    nodes: List[PipelineNode] = Field(default_factory=list)


# Type alias for progress callback
ProgressCallback = Callable[[EvaluationProgress], None]
