"""Enums for TurnWise SDK."""
from enum import Enum


class EvaluationLevel(str, Enum):
    """Level at which evaluation is performed."""

    CONVERSATION = "conversation"
    MESSAGE = "message"
    STEP = "step"


class OutputType(str, Enum):
    """Type of output from evaluation."""

    TEXT = "text"
    NUMBER = "number"
    CHECKBOX = "checkbox"
    PROGRESS = "progress"  # 0-1 score
    JSON = "json"


class MessageRole(str, Enum):
    """Role of a message in a conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"
