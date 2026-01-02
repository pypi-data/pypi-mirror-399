"""Evaluation Orchestrator for TurnWise SDK.

Orchestrates the evaluation process: goal extraction, context building, and evaluation execution.
"""
import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional

from ..llm import OpenRouterProvider
from ..models import (
    Conversation,
    EvaluationLevel,
    EvaluationProgress,
    EvaluationResult,
    Message,
    MessageRole,
    Metric,
)
from .evaluation_agent import EvaluationAgent, EvaluationConfig, EvaluationItem
from .goal_agent import GoalAgent

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[EvaluationProgress], None]


class EvaluationOrchestrator:
    """
    Orchestrates the evaluation process for conversations.

    This orchestrator:
    1. Extracts user goals from conversations
    2. Builds historical context for each item
    3. Runs evaluations using the evaluation agent
    4. Collects and returns results
    """

    def __init__(
        self,
        llm_provider: OpenRouterProvider,
        default_model: str = "openai/gpt-4o-mini",
        extract_goals: bool = True,
    ):
        """
        Initialize the orchestrator.

        Args:
            llm_provider: OpenRouter provider for LLM calls
            default_model: Default model for evaluations
            extract_goals: Whether to extract goals from conversations
        """
        self.llm_provider = llm_provider
        self.default_model = default_model
        self.extract_goals = extract_goals

        # Initialize agents
        self.goal_agent = GoalAgent(llm_provider, model_name=default_model)

        logger.info(f"[Orchestrator] Initialized with model: {default_model}")

    async def evaluate_conversation(
        self,
        conversation: Conversation,
        metric: Metric,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> List[EvaluationResult]:
        """
        Evaluate a single conversation with a metric.

        Args:
            conversation: Conversation to evaluate
            metric: Metric to use for evaluation
            progress_callback: Optional callback for progress updates

        Returns:
            List of evaluation results
        """
        logger.info(f"[Orchestrator] Evaluating conversation {conversation.id} with metric '{metric.name}'")

        # Extract goal if enabled
        goal = None
        if self.extract_goals:
            goal = await self._extract_conversation_goal(conversation)
            logger.debug(f"[Orchestrator] Extracted goal: {goal}")

        # Create evaluation agent with metric's model
        eval_agent = EvaluationAgent(
            llm_provider=self.llm_provider,
            model_name=metric.model_name,
        )

        # Build evaluation config
        config = EvaluationConfig(
            conversation_id=conversation.id,
            node_id=metric.node_id or 0,
            node_prompt=metric.prompt,
            node_model=metric.model_name,
            evaluation_level=metric.evaluation_level,
            output_schema=metric.output_schema,
            output_type=metric.output_type.value if metric.output_type else None,
        )

        results = []

        if metric.evaluation_level == EvaluationLevel.CONVERSATION:
            results = await self._evaluate_at_conversation_level(
                conversation, config, eval_agent, goal
            )
        elif metric.evaluation_level == EvaluationLevel.MESSAGE:
            results = await self._evaluate_at_message_level(
                conversation, config, eval_agent, goal, progress_callback
            )
        elif metric.evaluation_level == EvaluationLevel.STEP:
            results = await self._evaluate_at_step_level(
                conversation, config, eval_agent, goal, progress_callback
            )

        # Convert to SDK result format
        sdk_results = [
            EvaluationResult(
                entity_type=metric.evaluation_level,
                entity_id=r.item_id,
                pipeline_node_id=metric.node_id or 0,
                result=r.result,
                execution_time=r.execution_time,
                meta=r.metadata,
            )
            for r in results
        ]

        logger.info(f"[Orchestrator] Completed {len(sdk_results)} evaluations for conversation {conversation.id}")
        return sdk_results

    async def evaluate_batch(
        self,
        conversations: List[Conversation],
        metric: Metric,
        max_concurrent: int = 3,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> List[EvaluationResult]:
        """
        Evaluate multiple conversations with a metric.

        Args:
            conversations: List of conversations to evaluate
            metric: Metric to use for evaluation
            max_concurrent: Maximum concurrent evaluations
            progress_callback: Optional callback for progress updates

        Returns:
            List of all evaluation results
        """
        logger.info(f"[Orchestrator] Evaluating {len(conversations)} conversations with metric '{metric.name}'")

        all_results = []
        total = len(conversations)
        completed = 0

        # Process in batches
        semaphore = asyncio.Semaphore(max_concurrent)

        async def evaluate_with_semaphore(conv: Conversation) -> List[EvaluationResult]:
            async with semaphore:
                return await self.evaluate_conversation(conv, metric)

        tasks = [evaluate_with_semaphore(conv) for conv in conversations]

        for coro in asyncio.as_completed(tasks):
            results = await coro
            all_results.extend(results)
            completed += 1

            if progress_callback:
                progress_callback(
                    EvaluationProgress(
                        completed=completed,
                        total=total,
                        current_item=f"Conversation {completed}/{total}",
                    )
                )

        logger.info(f"[Orchestrator] Completed batch evaluation: {len(all_results)} total results")
        return all_results

    async def _extract_conversation_goal(self, conversation: Conversation) -> Optional[str]:
        """Extract the main user goal from a conversation."""
        first_user_msg = conversation.get_first_user_message()
        if first_user_msg:
            return await self.goal_agent.extract_goal(first_user_msg.content)
        return None

    async def _evaluate_at_conversation_level(
        self,
        conversation: Conversation,
        config: EvaluationConfig,
        eval_agent: EvaluationAgent,
        goal: Optional[str],
    ):
        """Evaluate at conversation level."""
        # Format full conversation
        conversation_content = self._format_conversation(conversation)

        return await eval_agent.evaluate_conversation(
            config=config,
            conversation_content=conversation_content,
            goal=goal,
        )

    async def _evaluate_at_message_level(
        self,
        conversation: Conversation,
        config: EvaluationConfig,
        eval_agent: EvaluationAgent,
        goal: Optional[str],
        progress_callback: Optional[ProgressCallback],
    ):
        """Evaluate at message level."""
        # Convert messages to evaluation items
        items = [
            EvaluationItem(
                id=msg.id,
                content=msg.content,
                role=msg.role.value,
            )
            for msg in conversation.messages
        ]

        # Build historical contexts for each message
        historical_contexts = self._build_message_contexts(conversation)

        # Format available tools
        available_tools = self._format_available_tools(conversation)

        return await eval_agent.evaluate_messages(
            config=config,
            messages=items,
            goal=goal,
            historical_contexts=historical_contexts,
            available_tools=available_tools,
        )

    async def _evaluate_at_step_level(
        self,
        conversation: Conversation,
        config: EvaluationConfig,
        eval_agent: EvaluationAgent,
        goal: Optional[str],
        progress_callback: Optional[ProgressCallback],
    ):
        """Evaluate at step level."""
        # Collect all steps from assistant messages
        items = []
        for msg in conversation.messages:
            if msg.role == MessageRole.ASSISTANT:
                for step in msg.steps:
                    items.append(
                        EvaluationItem(
                            id=step.id,
                            content=step.get_content(),
                            role="step",
                            metadata={
                                "message_id": msg.id,
                                "step_order": step.step_order,
                            },
                        )
                    )

        if not items:
            logger.warning(f"[Orchestrator] No steps found in conversation {conversation.id}")
            return []

        # Build historical contexts for each step
        historical_contexts = self._build_step_contexts(conversation)

        # Format available tools
        available_tools = self._format_available_tools(conversation)

        return await eval_agent.evaluate_steps(
            config=config,
            steps=items,
            goal=goal,
            historical_contexts=historical_contexts,
            available_tools=available_tools,
        )

    def _format_conversation(self, conversation: Conversation) -> str:
        """Format conversation for evaluation."""
        lines = []
        for msg in sorted(conversation.messages, key=lambda m: m.sequence_number):
            role = msg.role.value.upper()
            lines.append(f"[{role}]: {msg.content}")
        return "\n\n".join(lines)

    def _build_message_contexts(self, conversation: Conversation) -> Dict[int, str]:
        """Build historical context for each message."""
        contexts = {}
        history = []

        for msg in sorted(conversation.messages, key=lambda m: m.sequence_number):
            # Context for this message is everything before it
            if history:
                contexts[msg.id] = "\n".join(history)

            # Add this message to history for next iteration
            role = msg.role.value.upper()
            history.append(f"[{role}]: {msg.content[:500]}...")  # Truncate for context

        return contexts

    def _build_step_contexts(self, conversation: Conversation) -> Dict[int, str]:
        """Build historical context for each step."""
        contexts = {}
        history = []

        for msg in sorted(conversation.messages, key=lambda m: m.sequence_number):
            for step in sorted(msg.steps, key=lambda s: s.step_order):
                # Context for this step is everything before it
                if history:
                    contexts[step.id] = "\n".join(history)

                # Add this step to history
                step_summary = step.get_content()[:200]
                history.append(f"[Step {step.step_order}]: {step_summary}...")

        return contexts

    def _format_available_tools(self, conversation: Conversation) -> Optional[str]:
        """Format available tools/agents for context."""
        if not conversation.agents:
            return None

        lines = ["AVAILABLE TOOLS/AGENTS:"]
        for agent in conversation.agents:
            lines.append(f"- {agent.name}: {agent.description or 'No description'}")
            if agent.tools:
                for tool_name, tool_info in agent.tools.items():
                    desc = tool_info.get("description", "") if isinstance(tool_info, dict) else str(tool_info)
                    lines.append(f"  - {tool_name}: {desc}")

        return "\n".join(lines)
