"""Conversation models for TurnWise SDK."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .enums import MessageRole


class MessageStep(BaseModel):
    """A single reasoning step within a message."""

    id: int
    step_order: int
    model_name: Optional[str] = None
    thinking: Optional[str] = None
    tool_call: Optional[Dict[str, Any]] = None
    tool_result: Optional[Dict[str, Any]] = None
    output_structured: Optional[Dict[str, Any]] = None
    output_content: Optional[str] = None

    def get_content(self) -> str:
        """Get the content of this step for evaluation."""
        parts = []
        if self.thinking:
            parts.append(f"Thinking: {self.thinking}")
        if self.tool_call:
            parts.append(f"Tool Call: {self.tool_call}")
        if self.tool_result:
            parts.append(f"Tool Result: {self.tool_result}")
        if self.output_content:
            parts.append(f"Output: {self.output_content}")
        return "\n".join(parts) if parts else ""


class Message(BaseModel):
    """A single message in a conversation."""

    id: int
    role: MessageRole
    content: str
    sequence_number: int
    steps: List[MessageStep] = Field(default_factory=list)

    @property
    def output(self) -> str:
        """Alias for content (backward compatibility)."""
        return self.content

    def is_assistant(self) -> bool:
        """Check if this is an assistant message."""
        return self.role == MessageRole.ASSISTANT

    def is_user(self) -> bool:
        """Check if this is a user message."""
        return self.role == MessageRole.USER


class Agent(BaseModel):
    """An agent/tool available in a conversation."""

    name: str
    description: Optional[str] = None
    tools: Optional[Dict[str, Any]] = None


class Conversation(BaseModel):
    """A full conversation with messages and metadata."""

    id: int
    dataset_id: int
    name: Optional[str] = None
    description: Optional[str] = None
    messages: List[Message] = Field(default_factory=list)
    agents: List[Agent] = Field(default_factory=list)

    def get_messages_by_role(self, role: MessageRole) -> List[Message]:
        """Get all messages with a specific role."""
        return [m for m in self.messages if m.role == role]

    def get_assistant_messages(self) -> List[Message]:
        """Get all assistant messages."""
        return self.get_messages_by_role(MessageRole.ASSISTANT)

    def get_user_messages(self) -> List[Message]:
        """Get all user messages."""
        return self.get_messages_by_role(MessageRole.USER)

    def get_all_steps(self) -> List[MessageStep]:
        """Get all steps from all messages."""
        steps = []
        for message in self.messages:
            steps.extend(message.steps)
        return steps

    def get_first_user_message(self) -> Optional[Message]:
        """Get the first user message in the conversation."""
        user_messages = self.get_user_messages()
        return user_messages[0] if user_messages else None


class Dataset(BaseModel):
    """A dataset containing conversations."""

    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    conversation_count: int = 0
    created_at: Optional[str] = None
