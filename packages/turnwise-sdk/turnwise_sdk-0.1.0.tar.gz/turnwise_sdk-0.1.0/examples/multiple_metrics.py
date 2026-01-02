"""Multiple metrics evaluation example for TurnWise SDK.

This example demonstrates how to:
1. Use pre-built metrics from turnwise.metrics
2. Run multiple metrics on the same dataset
3. Compare results across metrics
"""

import asyncio
import os
from turnwise import TurnWiseClient, setup_logging
from turnwise.metrics import (
    # Pre-built message-level metrics
    ResponseQuality,
    GoalProgress,
    HallucinationDetection,
    ResponseCompleteness,
    ProfessionalTone,
    # Pre-built conversation-level metrics
    TaskCompletion,
    Efficiency,
)


async def main():
    setup_logging()

    turnwise_api_key = os.environ.get("TURNWISE_API_KEY", "tw_your_key_here")
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY", "sk-or-your_key_here")

    async with TurnWiseClient(
        turnwise_api_key=turnwise_api_key,
        openrouter_api_key=openrouter_api_key,
    ) as client:
        await client.verify()

        # Get first dataset
        datasets = await client.list_datasets()
        if not datasets:
            print("No datasets found.")
            return

        dataset_id = datasets[0].id
        print(f"Using dataset: {datasets[0].name}")

        # Use pre-built message-level metrics
        message_metrics = [
            ResponseQuality,
            GoalProgress,
            HallucinationDetection,
            ResponseCompleteness,
            ProfessionalTone,
        ]

        # Use pre-built conversation-level metrics
        conversation_metrics = [
            TaskCompletion,
            Efficiency,
        ]

        print("\n=== Message-Level Metrics ===")
        for metric in message_metrics:
            print(f"\nRunning: {metric.name}...")
            results = await client.evaluate(
                dataset_id=dataset_id,
                metric=metric,
                max_concurrent=3,
            )

            scores = [r.get_score() for r in results if r.get_score() is not None]
            if scores:
                print(f"  Average: {sum(scores) / len(scores):.3f}")
                print(f"  Min: {min(scores):.3f}, Max: {max(scores):.3f}")

        print("\n=== Conversation-Level Metrics ===")
        for metric in conversation_metrics:
            print(f"\nRunning: {metric.name}...")
            results = await client.evaluate(
                dataset_id=dataset_id,
                metric=metric,
                max_concurrent=3,
            )

            scores = [r.get_score() for r in results if r.get_score() is not None]
            if scores:
                print(f"  Average: {sum(scores) / len(scores):.3f}")
                print(f"  Min: {min(scores):.3f}, Max: {max(scores):.3f}")

        print("\n\nAll metrics complete! Results synced to TurnWise.")


if __name__ == "__main__":
    asyncio.run(main())
