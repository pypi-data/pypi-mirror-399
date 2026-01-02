"""Basic evaluation example for TurnWise SDK.

This example demonstrates how to:
1. Initialize the TurnWise client
2. Define a custom metric
3. Run evaluations on a dataset
4. View results
"""

import asyncio
import os
from turnwise import TurnWiseClient, Metric, EvaluationLevel, OutputType, setup_logging


async def main():
    # Set up logging
    setup_logging()

    # Get API keys from environment
    turnwise_api_key = os.environ.get("TURNWISE_API_KEY", "tw_your_key_here")
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY", "sk-or-your_key_here")

    # Initialize client
    async with TurnWiseClient(
        turnwise_api_key=turnwise_api_key,
        openrouter_api_key=openrouter_api_key,
    ) as client:
        # Verify connection
        print("Verifying connection...")
        await client.verify()
        print("Connected!")

        # List available datasets
        print("\nAvailable datasets:")
        datasets = await client.list_datasets()
        for ds in datasets:
            print(f"  - {ds.id}: {ds.name} ({ds.conversation_count} conversations)")

        if not datasets:
            print("No datasets found. Please upload a dataset to TurnWise first.")
            return

        # Select first dataset
        dataset_id = datasets[0].id
        print(f"\nUsing dataset: {datasets[0].name}")

        # Define a helpfulness metric
        helpfulness_metric = Metric(
            name="Response Helpfulness",
            description="Measures how helpful the assistant's response is",
            prompt="""Evaluate how helpful this assistant response is for achieving the user's goal.

MAIN USER GOAL: @GOAL

RESPONSE TO EVALUATE: @CONTENT

Consider:
1. Does the response address the user's need?
2. Is the information accurate and relevant?
3. Is the response clear and actionable?

Score from 0.0 to 1.0:
- 0.0: Completely unhelpful or harmful
- 0.3: Minimally helpful, misses key points
- 0.5: Partially helpful, addresses some needs
- 0.7: Mostly helpful, minor issues
- 1.0: Fully addresses the user's goal""",
            evaluation_level=EvaluationLevel.MESSAGE,
            output_type=OutputType.PROGRESS,
            model_name="openai/gpt-4o-mini",
        )

        # Run evaluation with progress tracking
        print("\nRunning evaluation...")

        def on_progress(progress):
            print(f"  Progress: {progress.completed}/{progress.total} ({progress.percentage:.1f}%)")

        results = await client.evaluate(
            dataset_id=dataset_id,
            metric=helpfulness_metric,
            max_concurrent=3,
            progress_callback=on_progress,
        )

        # Display results
        print(f"\nEvaluation complete! {len(results)} items evaluated.")

        # Calculate statistics
        scores = [r.get_score() for r in results if r.get_score() is not None]
        if scores:
            avg_score = sum(scores) / len(scores)
            min_score = min(scores)
            max_score = max(scores)

            print(f"\nStatistics:")
            print(f"  Average score: {avg_score:.3f}")
            print(f"  Min score: {min_score:.3f}")
            print(f"  Max score: {max_score:.3f}")

        # Show individual results
        print(f"\nSample results:")
        for result in results[:5]:
            score = result.get_score()
            print(f"  Entity {result.entity_id}: {score:.3f}" if score else f"  Entity {result.entity_id}: {result.result}")

        print("\nResults have been synced to TurnWise!")
        print(f"View them at: https://app.turnwise.io/datasets/{dataset_id}")


if __name__ == "__main__":
    asyncio.run(main())
