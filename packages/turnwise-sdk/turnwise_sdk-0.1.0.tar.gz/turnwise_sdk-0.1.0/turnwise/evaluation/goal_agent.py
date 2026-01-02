"""Goal extraction agent for conversation evaluation."""
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Literal, Optional

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from ..llm import OpenRouterProvider

logger = logging.getLogger(__name__)


# ==================== Prompts ====================

SYSTEM_PROMPT = """You are a goal tracking agent that identifies what users want to accomplish in customer service conversations.

Your job is to extract the user's ACTIONABLE GOAL - what they want the assistant to DO for them.

IMPORTANT RULES:
1. Goals should be action-oriented: "Get a refund", "Track order status", "Cancel subscription"
2. NOT a goal: greetings, thank yous, confirmations, pleasantries
3. Goals should be from the USER's perspective, not instructions to yourself
4. Be concise: 5-15 words max
5. If the message has no actionable goal, output: "No actionable goal in this message"

Examples of GOOD goal extractions:
- "Get a refund for undelivered order"
- "Check status of order #12345"
- "Cancel my subscription"
- "Report a damaged product and get replacement"

Examples of BAD goal extractions:
- "Extract the user's core goal from the message" (this is an instruction, not a goal)
- "The user wants to know about their order" (too vague)
- "Thank the assistant" (not actionable)
- "Provide order ID information" (this is what user is doing, not what they want)"""

USER_EXTRACT_GOAL_TEMPLATE = """What does this user want to accomplish? Extract their actionable goal.

RULES:
- Output the goal from the user's perspective (what they want DONE for them)
- Be concise: 5-15 words
- If this is just a greeting, thank you, confirmation, or provides info without a new request, output: "No actionable goal in this message"
- Do NOT output instructions to yourself
- Do NOT just rephrase the message

User Message:
{user_message}

What is the user's actionable goal?"""

USER_CLASSIFY_INTENT_TEMPLATE = """Classify the user's intent in this message relative to their current goal.

Current Goal: {current_goal}

User Message: {user_message}

Conversation History:
{conversation_history}

Classification options:
- "same_goal": User is continuing with the same goal (providing requested info, follow-up questions, clarifications about the current task)
- "goal_clarification": User is refining what they want (e.g., "Actually I want X instead", "I mean...")
- "new_goal": User has a completely new, different request

IMPORTANT: If the user is just providing information the assistant asked for (like an order ID), that's "same_goal" - they're still working toward their original objective.

Provide:
1. Classification type
2. The goal text (keep current goal if same_goal, extract new/refined goal otherwise)
3. Brief reason"""


# ==================== Structured Output Models ====================


class GoalExtraction(BaseModel):
    """Structured output for goal extraction."""

    goal_text: str = Field(
        ...,
        description="The core goal or objective extracted from the user message.",
    )


class IntentClassification(BaseModel):
    """Structured output for intent classification."""

    classification: Literal["same_goal", "goal_clarification", "new_goal"] = Field(
        ...,
        description="Classification of user intent.",
    )
    new_goal_text: str = Field(
        ...,
        description="The goal text to use.",
    )
    reason: str = Field(
        ...,
        description="Brief explanation of why this classification was chosen.",
    )


# ==================== Enums and Data Classes ====================


class GoalChangeType(str, Enum):
    """Goal change type enumeration."""

    SAME_GOAL = "same_goal"
    GOAL_CLARIFICATION = "goal_clarification"
    NEW_GOAL = "new_goal"


@dataclass
class GoalResult:
    """Goal tracking result."""

    conversation_id: int
    current_goal: str
    goal_changed: bool
    change_type: Optional[GoalChangeType] = None
    previous_goal: Optional[str] = None
    reason: Optional[str] = None


# ==================== Agent ====================


class GoalAgent:
    """
    Goal extraction and tracking agent.

    Extracts user goals from messages and tracks goal changes.
    """

    def __init__(
        self,
        llm_provider: OpenRouterProvider,
        model_name: str = "openai/gpt-4o-mini",
    ):
        """
        Initialize goal agent.

        Args:
            llm_provider: OpenRouter provider instance
            model_name: Model name for goal extraction
        """
        self.llm_provider = llm_provider
        self.model_name = model_name

        # Initialize LLM
        self.base_llm = llm_provider.get_llm(model_name=model_name, temperature=0)

        # Create agents
        self.goal_extraction_agent = create_agent(
            model=self.base_llm,
            response_format=GoalExtraction,
            system_prompt="You are an expert at extracting the core goal or objective from user messages. Extract the main intent, ignoring pleasantries and focusing on what the user wants to accomplish.",
        )

        self.intent_classification_agent = create_agent(
            model=self.base_llm,
            response_format=IntentClassification,
            system_prompt=SYSTEM_PROMPT,
        )

        logger.info(f"[GoalAgent] Initialized with model: {model_name}")

    async def extract_goal(self, user_message: str) -> str:
        """
        Extract goal from user message.

        Args:
            user_message: User message to extract goal from

        Returns:
            Extracted goal text
        """
        if not user_message or not user_message.strip():
            return ""

        try:
            logger.debug("[GoalAgent] Extracting goal from user message")
            prompt = USER_EXTRACT_GOAL_TEMPLATE.format(user_message=user_message.strip())

            result = await self.goal_extraction_agent.ainvoke(
                {"messages": [HumanMessage(content=prompt)]}
            )

            structured_response = result.get("structured_response")

            if structured_response and isinstance(structured_response, GoalExtraction):
                return structured_response.goal_text.strip()
            elif isinstance(structured_response, dict):
                return structured_response.get("goal_text", user_message.strip())
            else:
                logger.warning(f"Unexpected response format: {type(structured_response)}")
                return user_message.strip()
        except Exception as e:
            logger.error(f"Failed to extract goal: {e}")
            return user_message.strip()

    async def classify_intent(
        self,
        current_goal: str,
        user_message: str,
        conversation_history: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Classify user intent relative to current goal.

        Args:
            current_goal: Current goal text
            user_message: User message to classify
            conversation_history: Optional conversation history

        Returns:
            Classification result with keys: classification, new_goal_text, reason
        """
        if not user_message or not user_message.strip():
            return {
                "classification": "same_goal",
                "new_goal_text": current_goal,
                "reason": "Empty message, maintaining current goal",
            }

        try:
            logger.debug("[GoalAgent] Classifying user intent")
            history_text = conversation_history or "No previous conversation history available."
            prompt = USER_CLASSIFY_INTENT_TEMPLATE.format(
                current_goal=current_goal,
                user_message=user_message.strip(),
                conversation_history=history_text,
            )

            result = await self.intent_classification_agent.ainvoke(
                {"messages": [HumanMessage(content=prompt)]}
            )

            structured_response = result.get("structured_response")

            if structured_response and isinstance(structured_response, IntentClassification):
                return {
                    "classification": structured_response.classification,
                    "new_goal_text": structured_response.new_goal_text.strip(),
                    "reason": structured_response.reason,
                }
            elif isinstance(structured_response, dict):
                return {
                    "classification": structured_response.get("classification", "same_goal"),
                    "new_goal_text": structured_response.get("new_goal_text", current_goal).strip(),
                    "reason": structured_response.get("reason", "LLM classification"),
                }
            else:
                logger.warning(f"Unexpected response format: {type(structured_response)}")
                return self._classify_intent_fallback(current_goal, user_message)
        except Exception as e:
            logger.error(f"Failed to classify intent: {e}")
            return self._classify_intent_fallback(current_goal, user_message)

    def _classify_intent_fallback(
        self,
        current_goal: str,
        user_message: str,
    ) -> Dict[str, Any]:
        """Fallback heuristic classification."""
        user_lower = user_message.lower()

        follow_up_indicators = [
            "also",
            "and",
            "what about",
            "can you",
            "could you",
            "please",
            "?",
            "more",
        ]
        clarification_indicators = ["i mean", "actually", "i meant", "clarify", "better"]

        has_follow_up = any(indicator in user_lower for indicator in follow_up_indicators)
        has_clarification = any(indicator in user_lower for indicator in clarification_indicators)

        if has_clarification:
            return {
                "classification": "goal_clarification",
                "new_goal_text": user_message.strip(),
                "reason": "User is clarifying or refining their goal (heuristic fallback)",
            }
        elif has_follow_up or len(user_message) < 100:
            return {
                "classification": "same_goal",
                "new_goal_text": current_goal,
                "reason": "User is providing follow-up information (heuristic fallback)",
            }
        else:
            return {
                "classification": "new_goal",
                "new_goal_text": user_message.strip(),
                "reason": "User appears to be asking a new question (heuristic fallback)",
            }

    async def track_goal(
        self,
        conversation_id: int,
        user_message: str,
        current_goal: Optional[str] = None,
        conversation_history: Optional[str] = None,
    ) -> GoalResult:
        """
        Track goal for a message.

        Args:
            conversation_id: Conversation ID
            user_message: User message
            current_goal: Current goal text (None for first message)
            conversation_history: Optional conversation history

        Returns:
            Goal tracking result
        """
        logger.debug(f"[GoalAgent] Tracking goal for conversation {conversation_id}")

        previous_goal = current_goal or ""
        goal_changed = False
        change_type = None
        reason = None
        new_goal = previous_goal

        if current_goal is None:
            # First message - extract initial goal
            new_goal = await self.extract_goal(user_message)
            goal_changed = True
            change_type = GoalChangeType.NEW_GOAL
            reason = "Initial goal extraction"
        else:
            # Classify intent and update if needed
            classification = await self.classify_intent(
                current_goal=current_goal,
                user_message=user_message,
                conversation_history=conversation_history,
            )

            change_type = GoalChangeType(classification["classification"])

            if change_type in [GoalChangeType.GOAL_CLARIFICATION, GoalChangeType.NEW_GOAL]:
                new_goal = classification["new_goal_text"]
                goal_changed = True
                reason = classification["reason"]

        return GoalResult(
            conversation_id=conversation_id,
            current_goal=new_goal,
            goal_changed=goal_changed,
            change_type=change_type,
            previous_goal=previous_goal,
            reason=reason,
        )
