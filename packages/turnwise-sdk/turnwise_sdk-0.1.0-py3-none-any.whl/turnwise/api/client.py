"""TurnWise API Client.

HTTP client for communicating with the TurnWise backend API.
"""
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

from ..models import (
    Conversation,
    Dataset,
    EvaluationLevel,
    EvaluationResult,
    Metric,
    OutputType,
    Pipeline,
    PipelineNode,
)


class AuthVerifyResponse(BaseModel):
    """Response from auth verification."""

    valid: bool
    user_id: str


class MetricCreateResponse(BaseModel):
    """Response from metric creation."""

    pipeline_id: int
    node_id: int
    name: str


class SyncResponse(BaseModel):
    """Response from evaluation sync."""

    synced_count: int
    execution_id: int


class TurnWiseAPIError(Exception):
    """Exception raised for TurnWise API errors."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"TurnWise API Error ({status_code}): {message}")


class TurnWiseAPIClient:
    """HTTP client for TurnWise API."""

    DEFAULT_BASE_URL = "https://turnwise-production.up.railway.app"

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """
        Initialize the API client.

        Args:
            api_key: TurnWise API key (starts with 'tw_')
            base_url: Base URL for the API (defaults to production)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an API request."""
        response = await self._client.request(
            method=method,
            url=path,
            json=json,
            params=params,
        )

        if response.status_code >= 400:
            try:
                error_detail = response.json().get("detail", response.text)
            except Exception:
                error_detail = response.text
            raise TurnWiseAPIError(response.status_code, error_detail)

        if response.status_code == 204:
            return {}

        return response.json()

    # ==================== Auth ====================

    async def verify_auth(self) -> AuthVerifyResponse:
        """Verify the API key and get user info."""
        data = await self._request("POST", "/sdk/auth/verify")
        return AuthVerifyResponse(**data)

    # ==================== Datasets ====================

    async def list_datasets(self) -> List[Dataset]:
        """List all datasets for the authenticated user."""
        data = await self._request("GET", "/sdk/datasets")
        return [Dataset(**d) for d in data]

    async def get_conversations(self, dataset_id: int) -> List[Conversation]:
        """Get all conversations for a dataset with full details."""
        data = await self._request("GET", f"/sdk/datasets/{dataset_id}/conversations")
        return [Conversation(**c) for c in data]

    # ==================== Pipelines ====================

    async def get_pipelines(self, dataset_id: int) -> List[Pipeline]:
        """Get all evaluation pipelines for a dataset."""
        data = await self._request("GET", f"/sdk/datasets/{dataset_id}/pipelines")
        pipelines = []
        for p in data:
            nodes = [
                PipelineNode(
                    id=n["id"],
                    pipeline_id=n["pipeline_id"],
                    name=n["name"],
                    description=n.get("description"),
                    prompt=n["prompt"],
                    model_name=n["model_name"],
                    evaluation_level=EvaluationLevel(n["evaluation_level"]),
                    output_type=OutputType(n["output_type"]) if n.get("output_type") else None,
                    output_schema=n.get("output_schema"),
                    aggregate_results=n.get("aggregate_results", False),
                )
                for n in p.get("nodes", [])
            ]
            pipelines.append(
                Pipeline(
                    id=p["id"],
                    name=p["name"],
                    description=p.get("description"),
                    nodes=nodes,
                )
            )
        return pipelines

    # ==================== Metrics ====================

    async def create_metric(
        self,
        dataset_id: int,
        metric: Metric,
    ) -> MetricCreateResponse:
        """
        Create a new metric for a dataset.

        If the metric doesn't exist, it will be created in a pipeline named "SDK Metrics".
        """
        data = await self._request(
            "POST",
            "/sdk/metrics",
            json={
                "dataset_id": dataset_id,
                "name": metric.name,
                "description": metric.description,
                "prompt": metric.prompt,
                "evaluation_level": metric.evaluation_level.value,
                "output_type": metric.output_type.value,
                "output_schema": metric.output_schema,
                "model_name": metric.model_name,
                "aggregate_results": metric.aggregate_results,
            },
        )
        return MetricCreateResponse(**data)

    # ==================== Evaluations ====================

    async def sync_results(self, results: List[EvaluationResult]) -> SyncResponse:
        """Sync evaluation results to TurnWise."""
        data = await self._request(
            "POST",
            "/sdk/evaluations/sync",
            json={
                "results": [
                    {
                        "pipeline_node_id": r.pipeline_node_id,
                        "entity_type": r.entity_type.value,
                        "entity_id": r.entity_id,
                        "result": r.result,
                        "execution_time": r.execution_time,
                        "meta": r.meta,
                    }
                    for r in results
                ]
            },
        )
        return SyncResponse(**data)
