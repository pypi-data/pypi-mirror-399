"""
TurnWise Python SDK

Run LLM conversation evaluations locally while syncing with the TurnWise platform.

Example using custom metric:
    ```python
    import asyncio
    from turnwise import TurnWiseClient, Metric, EvaluationLevel, OutputType

    async def main():
        client = TurnWiseClient(
            turnwise_api_key="tw_xxx",
            openrouter_api_key="sk-xxx"
        )

        metric = Metric(
            name="Helpfulness",
            prompt=\"\"\"Evaluate how helpful this response is.
            USER GOAL: @GOAL
            RESPONSE: @CONTENT
            Score from 0 to 1.\"\"\",
            evaluation_level=EvaluationLevel.MESSAGE,
            output_type=OutputType.PROGRESS,
        )

        results = await client.evaluate(dataset_id=1, metric=metric)
        print(f"Evaluated {len(results)} items")
        await client.close()

    asyncio.run(main())
    ```

Example using pre-built metrics:
    ```python
    from turnwise import TurnWiseClient
    from turnwise.metrics import ResponseQuality, TaskCompletion

    async with TurnWiseClient(...) as client:
        # Use pre-built metrics
        results = await client.evaluate(dataset_id=1, metric=ResponseQuality)
    ```
"""

__version__ = "0.1.0"

# Main client
from .client import TurnWiseClient, create_client

# Models
from .models import (
    # Conversation models
    Agent,
    Conversation,
    Dataset,
    Message,
    MessageStep,
    # Enums
    EvaluationLevel,
    MessageRole,
    OutputType,
    # Evaluation models
    EvaluationConfig,
    EvaluationProgress,
    EvaluationResult,
    Metric,
    Pipeline,
    PipelineNode,
    ProgressCallback,
)

# API
from .api import TurnWiseAPIClient, TurnWiseAPIError

# LLM
from .llm import OpenRouterProvider

# Evaluation components (for advanced usage)
from .evaluation import (
    EvaluationOrchestrator,
    EvaluationAgent,
    GoalAgent,
)

# Utils
from .utils import setup_logging

# Pre-built metrics (import the module, not individual metrics to avoid cluttering namespace)
from . import metrics

__all__ = [
    # Version
    "__version__",
    # Main client
    "TurnWiseClient",
    "create_client",
    # Conversation models
    "Agent",
    "Conversation",
    "Dataset",
    "Message",
    "MessageStep",
    # Enums
    "EvaluationLevel",
    "MessageRole",
    "OutputType",
    # Evaluation models
    "EvaluationConfig",
    "EvaluationProgress",
    "EvaluationResult",
    "Metric",
    "Pipeline",
    "PipelineNode",
    "ProgressCallback",
    # API
    "TurnWiseAPIClient",
    "TurnWiseAPIError",
    # LLM
    "OpenRouterProvider",
    # Evaluation (advanced)
    "EvaluationOrchestrator",
    "EvaluationAgent",
    "GoalAgent",
    # Utils
    "setup_logging",
    # Pre-built metrics module
    "metrics",
]
