"""TurnWise Client - Main entry point for the SDK.

This is the primary interface for using TurnWise evaluations locally.
"""
import logging
from typing import List, Optional

from .api import TurnWiseAPIClient, TurnWiseAPIError
from .evaluation import EvaluationOrchestrator
from .llm import OpenRouterProvider
from .models import (
    Conversation,
    Dataset,
    EvaluationConfig,
    EvaluationLevel,
    EvaluationProgress,
    EvaluationResult,
    Metric,
    OutputType,
    Pipeline,
    ProgressCallback,
)

logger = logging.getLogger(__name__)


class TurnWiseClient:
    """
    TurnWise SDK Client.

    Main interface for running LLM evaluations locally while syncing with TurnWise platform.

    Example:
        ```python
        from turnwise import TurnWiseClient, Metric, EvaluationLevel, OutputType

        # Initialize
        client = TurnWiseClient(
            turnwise_api_key="tw_xxx",
            openrouter_api_key="sk-xxx"
        )

        # Define a metric
        metric = Metric(
            name="Helpfulness",
            prompt="Evaluate helpfulness... @GOAL @CONTENT",
            evaluation_level=EvaluationLevel.MESSAGE,
            output_type=OutputType.PROGRESS,
        )

        # Run evaluation
        results = await client.evaluate(
            dataset_id=1,
            metric=metric
        )
        ```
    """

    def __init__(
        self,
        turnwise_api_key: str,
        openrouter_api_key: str,
        turnwise_base_url: Optional[str] = None,
        default_model: str = "openai/gpt-4o-mini",
    ):
        """
        Initialize the TurnWise client.

        Args:
            turnwise_api_key: API key for TurnWise platform (starts with 'tw_')
            openrouter_api_key: API key for OpenRouter (for LLM calls)
            turnwise_base_url: Optional base URL for TurnWise API
            default_model: Default model for evaluations
        """
        self.turnwise_api_key = turnwise_api_key
        self.openrouter_api_key = openrouter_api_key
        self.default_model = default_model

        # Initialize components
        self._api_client = TurnWiseAPIClient(
            api_key=turnwise_api_key,
            base_url=turnwise_base_url,
        )
        self._llm_provider = OpenRouterProvider(api_key=openrouter_api_key)
        self._orchestrator = EvaluationOrchestrator(
            llm_provider=self._llm_provider,
            default_model=default_model,
        )

        self._verified = False
        logger.info("[TurnWiseClient] Initialized")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close the client and release resources."""
        await self._api_client.close()

    async def verify(self) -> bool:
        """
        Verify connection to TurnWise platform.

        Returns:
            True if verification successful

        Raises:
            TurnWiseAPIError: If verification fails
        """
        response = await self._api_client.verify_auth()
        self._verified = response.valid
        logger.info(f"[TurnWiseClient] Verified as user: {response.user_id}")
        return self._verified

    # ==================== Datasets ====================

    async def list_datasets(self) -> List[Dataset]:
        """
        List all datasets for the authenticated user.

        Returns:
            List of datasets
        """
        return await self._api_client.list_datasets()

    async def get_conversations(self, dataset_id: int) -> List[Conversation]:
        """
        Get all conversations for a dataset.

        Args:
            dataset_id: Dataset ID

        Returns:
            List of conversations with full details
        """
        return await self._api_client.get_conversations(dataset_id)

    # ==================== Pipelines & Metrics ====================

    async def get_pipelines(self, dataset_id: int) -> List[Pipeline]:
        """
        Get all evaluation pipelines for a dataset.

        Args:
            dataset_id: Dataset ID

        Returns:
            List of pipelines with their metric nodes
        """
        return await self._api_client.get_pipelines(dataset_id)

    async def register_metric(self, dataset_id: int, metric: Metric) -> Metric:
        """
        Register a metric with TurnWise platform.

        If the metric doesn't exist, it will be created in a pipeline named "SDK Metrics".
        The metric object is updated with the assigned pipeline_id and node_id.

        Args:
            dataset_id: Dataset ID to register the metric for
            metric: Metric definition

        Returns:
            Updated metric with pipeline_id and node_id set
        """
        response = await self._api_client.create_metric(dataset_id, metric)
        metric.pipeline_id = response.pipeline_id
        metric.node_id = response.node_id
        logger.info(f"[TurnWiseClient] Registered metric '{metric.name}' as node {metric.node_id}")
        return metric

    # ==================== Evaluation ====================

    async def evaluate(
        self,
        dataset_id: int,
        metric: Metric,
        conversation_ids: Optional[List[int]] = None,
        max_concurrent: int = 3,
        progress_callback: Optional[ProgressCallback] = None,
        auto_sync: bool = True,
    ) -> List[EvaluationResult]:
        """
        Run evaluation on a dataset with a metric.

        This is the main method for running evaluations. It:
        1. Registers the metric if not already registered
        2. Fetches conversations from TurnWise
        3. Runs evaluations locally using your LLM API key
        4. Syncs results back to TurnWise (if auto_sync=True)

        Args:
            dataset_id: Dataset ID to evaluate
            metric: Metric to use for evaluation
            conversation_ids: Optional list of specific conversation IDs (None = all)
            max_concurrent: Maximum concurrent evaluations
            progress_callback: Optional callback for progress updates
            auto_sync: Whether to automatically sync results to TurnWise

        Returns:
            List of evaluation results
        """
        # Register metric if needed
        if not metric.is_registered():
            metric = await self.register_metric(dataset_id, metric)

        # Fetch conversations
        conversations = await self.get_conversations(dataset_id)

        # Filter to specific conversations if requested
        if conversation_ids:
            conversations = [c for c in conversations if c.id in conversation_ids]

        if not conversations:
            logger.warning(f"[TurnWiseClient] No conversations found for dataset {dataset_id}")
            return []

        logger.info(f"[TurnWiseClient] Evaluating {len(conversations)} conversations")

        # Run evaluations
        results = await self._orchestrator.evaluate_batch(
            conversations=conversations,
            metric=metric,
            max_concurrent=max_concurrent,
            progress_callback=progress_callback,
        )

        # Sync results if requested
        if auto_sync and results:
            await self.sync_results(results)

        return results

    async def evaluate_conversation(
        self,
        conversation: Conversation,
        metric: Metric,
        auto_sync: bool = True,
    ) -> List[EvaluationResult]:
        """
        Evaluate a single conversation with a metric.

        Args:
            conversation: Conversation to evaluate
            metric: Metric to use
            auto_sync: Whether to sync results to TurnWise

        Returns:
            List of evaluation results
        """
        results = await self._orchestrator.evaluate_conversation(
            conversation=conversation,
            metric=metric,
        )

        if auto_sync and results and metric.is_registered():
            await self.sync_results(results)

        return results

    # ==================== Results ====================

    async def sync_results(self, results: List[EvaluationResult]) -> int:
        """
        Sync evaluation results to TurnWise platform.

        Args:
            results: List of evaluation results to sync

        Returns:
            Number of results synced
        """
        if not results:
            return 0

        response = await self._api_client.sync_results(results)
        logger.info(f"[TurnWiseClient] Synced {response.synced_count} results (execution_id: {response.execution_id})")
        return response.synced_count


# Convenience function for quick initialization
def create_client(
    turnwise_api_key: str,
    openrouter_api_key: str,
    **kwargs,
) -> TurnWiseClient:
    """
    Create a TurnWise client.

    Convenience function for creating a client without importing the class.

    Args:
        turnwise_api_key: API key for TurnWise platform
        openrouter_api_key: API key for OpenRouter
        **kwargs: Additional arguments passed to TurnWiseClient

    Returns:
        Configured TurnWiseClient
    """
    return TurnWiseClient(
        turnwise_api_key=turnwise_api_key,
        openrouter_api_key=openrouter_api_key,
        **kwargs,
    )
