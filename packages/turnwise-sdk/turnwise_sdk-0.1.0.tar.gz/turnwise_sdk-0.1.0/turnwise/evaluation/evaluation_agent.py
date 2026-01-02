"""Evaluation Agent for running evaluations locally."""
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from ..llm import OpenRouterProvider
from ..models import EvaluationLevel, MessageRole
from .output_models import get_output_model

logger = logging.getLogger(__name__)


@dataclass
class EvaluationConfig:
    """Configuration for evaluation."""

    conversation_id: int
    node_id: int
    node_prompt: str
    node_model: str
    evaluation_level: EvaluationLevel
    output_schema: Optional[Dict[str, Any]] = None
    output_type: Optional[str] = None


@dataclass
class EvaluationItem:
    """Single item to evaluate."""

    id: int
    content: str
    role: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class EvaluationResultData:
    """Result of single evaluation."""

    item_id: int
    result: Dict[str, Any]
    execution_time: float
    metadata: Optional[Dict[str, Any]] = None


class EvaluationAgent:
    """
    Evaluation agent for running evaluations locally.

    This agent handles evaluation at different levels:
    - CONVERSATION: Single evaluation for entire conversation
    - MESSAGE: One evaluation per assistant message
    - STEP: One evaluation per step in assistant messages
    """

    def __init__(
        self,
        llm_provider: OpenRouterProvider,
        model_name: str = "openai/gpt-4o-mini",
    ):
        """
        Initialize evaluation agent.

        Args:
            llm_provider: OpenRouter provider instance
            model_name: Model name for evaluation
        """
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.llm = llm_provider.get_llm(model_name=model_name, temperature=0)

        logger.info(f"[EvaluationAgent] Initialized with model: {model_name}")

    def create_evaluator(
        self,
        system_prompt: str,
        response_format: Optional[Type[BaseModel]] = None,
    ) -> Any:
        """
        Create evaluator agent with given system prompt and optional structured output.

        Args:
            system_prompt: System prompt for the evaluator
            response_format: Optional Pydantic model for structured output

        Returns:
            LangChain agent configured for evaluation
        """
        kwargs = {"model": self.llm, "system_prompt": system_prompt, "tools": []}
        if response_format:
            kwargs["response_format"] = response_format

        return create_agent(**kwargs)

    def _extract_result(self, result: Any, has_structured_output: bool) -> Dict[str, Any]:
        """Extract structured result from agent response."""
        if isinstance(result, dict):
            if "structured_response" in result:
                structured = result["structured_response"]
                if hasattr(structured, "model_dump"):
                    return structured.model_dump()
                elif isinstance(structured, dict):
                    return structured
                else:
                    return {"value": structured}
            if "messages" in result and len(result) == 1:
                messages = result.get("messages", [])
                if messages:
                    last_msg = messages[-1]
                    content = getattr(last_msg, "content", str(last_msg))
                    return {"raw_response": content}
            return result

        if hasattr(result, "model_dump"):
            return result.model_dump()

        if isinstance(result, str):
            return {"raw_response": result}

        if hasattr(result, "__dict__"):
            return dict(result.__dict__)

        return {"raw_response": str(result)}

    async def evaluate_single(
        self,
        config: EvaluationConfig,
        item: EvaluationItem,
    ) -> EvaluationResultData:
        """
        Evaluate a single item with an already-resolved prompt.

        Args:
            config: Evaluation configuration with resolved prompt
            item: Item being evaluated (for metadata only)

        Returns:
            Single evaluation result
        """
        logger.info(f"[EvaluationAgent] Evaluating single item {item.id}")

        start_time = time.time()

        response_format = get_output_model(config.output_schema, config.output_type)
        if response_format:
            logger.debug(f"[EvaluationAgent] Using structured output: {response_format.__name__}")

        evaluator = self.create_evaluator(config.node_prompt, response_format)

        result = await evaluator.ainvoke({"messages": [HumanMessage(content=config.node_prompt)]})

        execution_time = time.time() - start_time
        structured_result = self._extract_result(result, response_format is not None)
        logger.info(f"[EvaluationAgent] Item {item.id} evaluated in {execution_time:.2f}s")

        return EvaluationResultData(
            item_id=item.id,
            result=structured_result,
            execution_time=execution_time,
            metadata={
                "evaluation_level": config.evaluation_level.value,
                "conversation_id": config.conversation_id,
                "used_structured_output": response_format is not None,
                **(item.metadata or {}),
            },
        )

    async def evaluate_conversation(
        self,
        config: EvaluationConfig,
        conversation_content: str,
        goal: Optional[str] = None,
        historical_context: Optional[str] = None,
    ) -> List[EvaluationResultData]:
        """
        Evaluate entire conversation.

        Args:
            config: Evaluation configuration
            conversation_content: Full conversation content
            goal: Optional goal context
            historical_context: Optional historical context (rolling summary)

        Returns:
            List with single evaluation result
        """
        logger.info(f"[EvaluationAgent] Evaluating conversation {config.conversation_id}")

        start_time = time.time()

        response_format = get_output_model(config.output_schema, config.output_type)
        evaluator = self.create_evaluator(config.node_prompt, response_format)

        user_prompt = self._format_prompt(
            content=conversation_content,
            goal=goal,
            level="conversation",
            historical_context=historical_context,
        )

        result = await evaluator.ainvoke({"messages": [HumanMessage(content=user_prompt)]})

        execution_time = time.time() - start_time
        structured_result = self._extract_result(result, response_format is not None)
        logger.info(f"[EvaluationAgent] Conversation evaluated in {execution_time:.2f}s")

        return [
            EvaluationResultData(
                item_id=config.conversation_id,
                result=structured_result,
                execution_time=execution_time,
                metadata={
                    "evaluation_level": "conversation",
                    "conversation_id": config.conversation_id,
                    "goal_used": goal,
                    "used_structured_output": response_format is not None,
                },
            )
        ]

    async def evaluate_messages(
        self,
        config: EvaluationConfig,
        messages: List[EvaluationItem],
        goal: Optional[str] = None,
        historical_contexts: Optional[Dict[int, str]] = None,
        available_tools: Optional[str] = None,
    ) -> List[EvaluationResultData]:
        """
        Evaluate each message individually.

        Args:
            config: Evaluation configuration
            messages: List of messages to evaluate
            goal: Optional goal context
            historical_contexts: Optional dict mapping message_id to historical context
            available_tools: Optional formatted string of available tools/agents

        Returns:
            List of evaluation results, one per message
        """
        # Filter to assistant messages only
        assistant_messages = [m for m in messages if m.role == MessageRole.ASSISTANT.value]
        logger.info(
            f"[EvaluationAgent] Evaluating {len(assistant_messages)} assistant messages"
        )

        response_format = get_output_model(config.output_schema, config.output_type)
        evaluator = self.create_evaluator(config.node_prompt, response_format)
        results = []
        historical_contexts = historical_contexts or {}

        for message in messages:
            if message.role != MessageRole.ASSISTANT.value:
                continue

            start_time = time.time()
            historical_context = historical_contexts.get(message.id)

            user_prompt = self._format_prompt(
                content=message.content,
                goal=goal,
                level="message",
                message_id=message.id,
                historical_context=historical_context,
                available_tools=available_tools,
            )

            result = await evaluator.ainvoke({"messages": [HumanMessage(content=user_prompt)]})

            execution_time = time.time() - start_time
            structured_result = self._extract_result(result, response_format is not None)
            logger.debug(f"[EvaluationAgent] Message {message.id} evaluated in {execution_time:.2f}s")

            results.append(
                EvaluationResultData(
                    item_id=message.id,
                    result=structured_result,
                    execution_time=execution_time,
                    metadata={
                        "evaluation_level": "message",
                        "conversation_id": config.conversation_id,
                        "message_role": message.role,
                        "goal_used": goal,
                        "used_structured_output": response_format is not None,
                    },
                )
            )

        logger.info(f"[EvaluationAgent] Completed {len(results)} message evaluations")
        return results

    async def evaluate_steps(
        self,
        config: EvaluationConfig,
        steps: List[EvaluationItem],
        goal: Optional[str] = None,
        historical_contexts: Optional[Dict[int, str]] = None,
        available_tools: Optional[str] = None,
    ) -> List[EvaluationResultData]:
        """
        Evaluate each step individually.

        Args:
            config: Evaluation configuration
            steps: List of steps to evaluate
            goal: Optional goal context
            historical_contexts: Optional dict mapping step_id to historical context
            available_tools: Optional formatted string of available tools/agents

        Returns:
            List of evaluation results, one per step
        """
        logger.info(f"[EvaluationAgent] Evaluating {len(steps)} steps")

        response_format = get_output_model(config.output_schema, config.output_type)
        evaluator = self.create_evaluator(config.node_prompt, response_format)
        results = []
        historical_contexts = historical_contexts or {}

        for step in steps:
            start_time = time.time()
            historical_context = historical_contexts.get(step.id)

            user_prompt = self._format_prompt(
                content=step.content,
                goal=goal,
                level="step",
                step_id=step.id,
                historical_context=historical_context,
                available_tools=available_tools,
            )

            result = await evaluator.ainvoke({"messages": [HumanMessage(content=user_prompt)]})

            execution_time = time.time() - start_time
            structured_result = self._extract_result(result, response_format is not None)
            logger.debug(f"[EvaluationAgent] Step {step.id} evaluated in {execution_time:.2f}s")

            results.append(
                EvaluationResultData(
                    item_id=step.id,
                    result=structured_result,
                    execution_time=execution_time,
                    metadata={
                        "evaluation_level": "step",
                        "conversation_id": config.conversation_id,
                        "step_metadata": step.metadata,
                        "goal_used": goal,
                        "used_structured_output": response_format is not None,
                    },
                )
            )

        logger.info(f"[EvaluationAgent] Completed {len(results)} step evaluations")
        return results

    def _format_prompt(
        self,
        content: str,
        goal: Optional[str],
        level: str,
        message_id: Optional[int] = None,
        step_id: Optional[int] = None,
        historical_context: Optional[str] = None,
        available_tools: Optional[str] = None,
    ) -> str:
        """Format user prompt with context."""
        parts = []

        if historical_context:
            parts.append(f"CONVERSATION HISTORY:\n{historical_context}")

        if available_tools and level in ("message", "step"):
            parts.append(available_tools)

        if goal:
            parts.append(f"MAIN USER GOAL/INTENT: {goal}")

        if level == "conversation":
            parts.append(f"CONVERSATION TO EVALUATE:\n{content}")
        elif level == "message":
            parts.append(f"MESSAGE TO EVALUATE (ID: {message_id}):\n{content}")
        elif level == "step":
            parts.append(f"STEP TO EVALUATE (ID: {step_id}):\n{content}")
        else:
            parts.append(f"CONTENT TO EVALUATE:\n{content}")

        return "\n\n".join(parts)
