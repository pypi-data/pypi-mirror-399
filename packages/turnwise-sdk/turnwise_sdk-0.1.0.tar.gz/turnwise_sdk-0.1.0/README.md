# TurnWise Python SDK

Run LLM conversation evaluations locally using your own API keys, while syncing with the TurnWise platform.

## Installation

```bash
pip install turnwise
```

## Quick Start

```python
import asyncio
from turnwise import TurnWiseClient, Metric, EvaluationLevel, OutputType

async def main():
    # Initialize client with your API keys
    client = TurnWiseClient(
        turnwise_api_key="tw_your_api_key",      # From TurnWise platform
        openrouter_api_key="sk-or-your_key"      # From OpenRouter
    )

    # Verify connection
    await client.verify()

    # Define a custom metric
    metric = Metric(
        name="Response Helpfulness",
        prompt="""Evaluate how helpful this assistant response is.

USER GOAL: @GOAL
RESPONSE TO EVALUATE: @CONTENT

Score from 0.0 to 1.0:
- 0.0: Completely unhelpful
- 0.5: Partially addresses the need
- 1.0: Fully addresses the user's goal""",
        evaluation_level=EvaluationLevel.MESSAGE,
        output_type=OutputType.PROGRESS,
        model_name="openai/gpt-4o-mini",
    )

    # Run evaluation on a dataset
    results = await client.evaluate(
        dataset_id=1,
        metric=metric,
        progress_callback=lambda p: print(f"Progress: {p.completed}/{p.total}")
    )

    # Results are automatically synced to TurnWise
    print(f"Evaluated {len(results)} items")

    # Calculate average score
    scores = [r.get_score() for r in results if r.get_score() is not None]
    if scores:
        print(f"Average score: {sum(scores) / len(scores):.2f}")

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Features

- **Run evaluations locally**: Use your own LLM API keys to run evaluations
- **Pre-built metrics**: 30+ ready-to-use evaluation metrics for common scenarios
- **Automatic goal extraction**: Extracts user goals from conversations for context
- **Multiple evaluation levels**: Evaluate at conversation, message, or step level
- **Structured output**: Support for text, number, checkbox, progress (0-1), and custom JSON schemas
- **Sync with TurnWise**: Results automatically sync to the TurnWise web UI
- **Batch processing**: Evaluate multiple conversations concurrently

## Pre-built Metrics

The SDK includes 30+ pre-built metrics matching the TurnWise platform system templates. Use them directly without writing prompts:

```python
from turnwise import TurnWiseClient
from turnwise.metrics import (
    # Message-level metrics
    ResponseQuality,
    GoalProgress,
    HallucinationDetection,
    ResponseCompleteness,
    ProfessionalTone,

    # Step-level metrics
    ToolSelection,
    ParameterValidity,
    ThinkingQuality,

    # Conversation-level metrics
    TaskCompletion,
    Efficiency,
    UserSatisfactionPrediction,

    # Safety metrics
    SycophancyDetection,
    DeceptionDetection,
    ManipulationDetection,
)

async with TurnWiseClient(...) as client:
    # Use any pre-built metric directly
    results = await client.evaluate(
        dataset_id=1,
        metric=ResponseQuality,
    )
```

### Available Metrics

**Message Level:**
- `ResponseQuality` - Overall response quality
- `GoalProgress` - Progress toward user's goal
- `HallucinationDetection` - Detects fabricated information
- `ResponseCompleteness` - Completeness of information
- `ProfessionalTone` - Tone appropriateness
- `ReAskDetection` - User re-asking detection (JSON output)
- `UserCorrectionDetection` - User correction detection (JSON output)
- `SycophancyDetection` - Detects inappropriate agreement
- `DeceptionDetection` - Detects misleading information
- `SelfPreservationDetection` - Detects resistance to control
- `ManipulationDetection` - Detects manipulative techniques
- `InstructionOverrideAttempt` - Detects instruction bypass

**Step Level:**
- `ToolSelection` - Tool selection quality (TSE)
- `ParameterValidity` - Parameter hallucination detection (PH)
- `ToolResultHandling` - Tool result interpretation
- `ThinkingQuality` - Reasoning quality
- `SelfCorrectionAwareness` - Error recognition (JSON output)
- `StepCorrectness` - Overall step correctness
- `ComprehensiveStepAnalysis` - Multi-dimensional analysis (JSON output)
- `PowerSeekingBehavior` - Detects capability acquisition attempts

**Conversation Level:**
- `ConversationFlow` - Flow and coherence
- `TaskCompletion` - Goal achievement
- `Efficiency` - Execution efficiency (TCI)
- `TrajectoryQuality` - Trajectory analysis (JSON output)
- `UserSatisfactionPrediction` - Predicted satisfaction
- `IntentDrift` - Intent alignment (JSON output)
- `ComprehensiveConversationAnalysis` - Full analysis (JSON output)
- `RewardHackingDetection` - Technical vs genuine completion
- `ComprehensiveSafetyAnalysis` - Overall safety score

### Metric Collections

```python
from turnwise.metrics import (
    MESSAGE_METRICS,      # All message-level metrics
    STEP_METRICS,         # All step-level metrics
    CONVERSATION_METRICS, # All conversation-level metrics
    SAFETY_METRICS,       # All safety-related metrics
    ALL_METRICS,          # All available metrics
)

# Run multiple metrics
for metric in SAFETY_METRICS:
    results = await client.evaluate(dataset_id=1, metric=metric)
```

## Evaluation Levels

### Conversation Level
Evaluate the entire conversation as a whole:

```python
metric = Metric(
    name="Overall Quality",
    prompt="Evaluate the overall quality of this conversation...",
    evaluation_level=EvaluationLevel.CONVERSATION,
    output_type=OutputType.PROGRESS,
)
```

### Message Level
Evaluate each assistant message individually:

```python
metric = Metric(
    name="Message Helpfulness",
    prompt="Evaluate how helpful this response is...",
    evaluation_level=EvaluationLevel.MESSAGE,
    output_type=OutputType.PROGRESS,
)
```

### Step Level
Evaluate each reasoning step within messages:

```python
metric = Metric(
    name="Tool Usage Quality",
    prompt="Evaluate the quality of this tool usage step...",
    evaluation_level=EvaluationLevel.STEP,
    output_type=OutputType.PROGRESS,
)
```

## Template Variables

Use `@VARIABLE` syntax in prompts to dynamically inject conversation context. Variables are automatically resolved based on the evaluation level.

### Conversation Level Variables

| Variable | Description |
|----------|-------------|
| `@HISTORY` | Full formatted conversation history |
| `@GOAL` | User's overall goal/intent (extracted from first message) |
| `@LIST_AGENT` | List of available agents with their tools |
| `@MESSAGES` | All messages formatted |
| `@USER_MESSAGES` | All user messages only |
| `@ASSISTANT_MESSAGES` | All assistant messages only |
| `@FIRST_USER_MSG` | First user message |
| `@LAST_USER_MSG` | Last user message |
| `@LAST_ASSISTANT_MSG` | Last assistant message |

### Message Level Variables

Includes all conversation-level variables, plus:

| Variable | Description |
|----------|-------------|
| `@PREVIOUS_USER_MSG` | Previous user message |
| `@PREVIOUS_ASSISTANT_MSG` | Previous assistant message |
| `@CURRENT_MESSAGE.output` | Current message content |
| `@CURRENT_MESSAGE.role` | Current message role (user/assistant) |
| `@CURRENT_STEPS` | All steps in this message (formatted) |
| `@CURRENT_STEPS_COUNT` | Number of steps in message |

### Step Level Variables

Includes all message-level variables, plus:

| Variable | Description |
|----------|-------------|
| `@PREVIOUS_STEP.thinking` | Previous step's reasoning |
| `@PREVIOUS_STEP.tool_call` | Previous step's tool call (JSON) |
| `@PREVIOUS_STEP.tool_result` | Previous step's tool result (JSON) |
| `@CURRENT_STEP.thinking` | Current step's reasoning |
| `@CURRENT_STEP.tool_call` | Current step's tool call (JSON) |
| `@CURRENT_STEP.tool_result` | Current step's tool result (JSON) |
| `@CURRENT_STEP.output_content` | Current step's output text |
| `@CURRENT_STEP.output_structured` | Current step's structured output (JSON) |
| `@STEP_NUMBER` | Current step position (1-indexed) |

### Example Prompts

**Message-level helpfulness:**
```python
metric = Metric(
    name="Helpfulness",
    prompt="""Evaluate how helpful this response is for the user's goal.

USER GOAL: @GOAL
PREVIOUS USER MESSAGE: @PREVIOUS_USER_MSG
RESPONSE TO EVALUATE: @CURRENT_MESSAGE.output

Score from 0.0 to 1.0.""",
    evaluation_level=EvaluationLevel.MESSAGE,
    output_type=OutputType.PROGRESS,
)
```

**Step-level tool usage:**
```python
metric = Metric(
    name="Tool Usage Correctness",
    prompt="""Evaluate if the tool was called correctly.

USER GOAL: @GOAL
AVAILABLE TOOLS: @LIST_AGENT

TOOL CALL: @CURRENT_STEP.tool_call
TOOL RESULT: @CURRENT_STEP.tool_result
REASONING: @CURRENT_STEP.thinking

Was this tool call appropriate and correct? (true/false)""",
    evaluation_level=EvaluationLevel.STEP,
    output_type=OutputType.CHECKBOX,
)
```

**Conversation-level overall quality:**
```python
metric = Metric(
    name="Conversation Quality",
    prompt="""Evaluate the overall quality of this conversation.

USER GOAL: @GOAL
FULL CONVERSATION:
@HISTORY

Did the conversation achieve the user's goal? Score 0-1.""",
    evaluation_level=EvaluationLevel.CONVERSATION,
    output_type=OutputType.PROGRESS,
)
```

## Output Types

| Type | Description | Output |
|------|-------------|--------|
| `TEXT` | Free-form text | `{"value": "..."}` |
| `NUMBER` | Numeric value | `{"value": 42.0}` |
| `CHECKBOX` | Boolean | `{"value": true}` |
| `PROGRESS` | Score 0-1 | `{"score": 0.85}` |
| `JSON` | Custom schema | Custom object |

### Custom JSON Schema

```python
metric = Metric(
    name="Detailed Analysis",
    prompt="Analyze this response...",
    evaluation_level=EvaluationLevel.MESSAGE,
    output_type=OutputType.JSON,
    output_schema={
        "type": "object",
        "properties": {
            "quality_score": {"type": "number"},
            "issues": {"type": "array"},
            "recommendation": {"type": "string"}
        },
        "required": ["quality_score"]
    }
)
```

## Using Existing Metrics

Fetch and use metrics already configured in TurnWise:

```python
# Get all pipelines for a dataset
pipelines = await client.get_pipelines(dataset_id=1)

for pipeline in pipelines:
    print(f"Pipeline: {pipeline.name}")
    for node in pipeline.nodes:
        print(f"  - {node.name} ({node.evaluation_level})")

# Use an existing metric
existing_metric = Metric(
    name=pipelines[0].nodes[0].name,
    prompt=pipelines[0].nodes[0].prompt,
    evaluation_level=pipelines[0].nodes[0].evaluation_level,
    output_type=pipelines[0].nodes[0].output_type,
    node_id=pipelines[0].nodes[0].id,  # Already registered
    pipeline_id=pipelines[0].id,
)
```

## Advanced Usage

### Manual Orchestration

For more control over the evaluation process:

```python
from turnwise import EvaluationOrchestrator, OpenRouterProvider

# Create provider and orchestrator
provider = OpenRouterProvider(api_key="sk-or-xxx")
orchestrator = EvaluationOrchestrator(
    llm_provider=provider,
    default_model="openai/gpt-4o-mini",
    extract_goals=True,
)

# Get conversations
conversations = await client.get_conversations(dataset_id=1)

# Evaluate single conversation
results = await orchestrator.evaluate_conversation(
    conversation=conversations[0],
    metric=metric,
)

# Manually sync when ready
await client.sync_results(results)
```

### Disable Auto-Sync

Run evaluations without syncing to TurnWise:

```python
results = await client.evaluate(
    dataset_id=1,
    metric=metric,
    auto_sync=False,  # Results stay local
)

# Process results locally
for result in results:
    print(f"Entity {result.entity_id}: {result.result}")

# Sync later if desired
await client.sync_results(results)
```

## API Reference

### TurnWiseClient

Main client for interacting with TurnWise.

```python
client = TurnWiseClient(
    turnwise_api_key="tw_xxx",       # Required
    openrouter_api_key="sk-xxx",     # Required
    turnwise_base_url=None,          # Optional, defaults to production
    default_model="openai/gpt-4o-mini",  # Default model for evaluations
)
```

**Methods:**
- `verify()` - Verify API key
- `list_datasets()` - List user's datasets
- `get_conversations(dataset_id)` - Get conversations for a dataset
- `get_pipelines(dataset_id)` - Get evaluation pipelines
- `register_metric(dataset_id, metric)` - Register a metric
- `evaluate(dataset_id, metric, ...)` - Run evaluation
- `sync_results(results)` - Sync results to TurnWise

### Metric

Definition of an evaluation metric.

```python
metric = Metric(
    name="Metric Name",
    prompt="Evaluation prompt...",
    evaluation_level=EvaluationLevel.MESSAGE,
    output_type=OutputType.PROGRESS,
    description=None,           # Optional
    output_schema=None,         # For JSON output type
    model_name="openai/gpt-4o-mini",
    aggregate_results=False,    # Aggregate to parent level
)
```

## Environment Variables

The SDK supports configuration via environment variables:

```bash
export TURNWISE_API_KEY="tw_xxx"
export OPENROUTER_API_KEY="sk-or-xxx"
```

## Requirements

- Python 3.10+
- TurnWise account with API key
- OpenRouter API key

## License

MIT License
