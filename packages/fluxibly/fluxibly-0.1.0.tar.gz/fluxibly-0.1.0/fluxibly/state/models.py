"""Database models for conversation history persistence.

This module defines the data models for storing conversation threads and messages
in a database backend (PostgreSQL or mock in-memory store).
"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Represents a single message in a conversation thread.

    Attributes:
        id: Unique message identifier
        chat_thread_id: Reference to parent thread
        sender_id: Optional user ID of sender
        sender_role: Role of sender (user, assistant, system, tool)
        content: Message content as JSON (type and text fields)
        created_at: Message creation timestamp
        updated_at: Last update timestamp
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    chat_thread_id: str
    sender_id: str | None = None
    sender_role: str  # user, assistant, system, tool
    content: dict[str, Any]  # {'type': 'text', 'text': str}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class ChatThread(BaseModel):
    """Represents a conversation thread with metadata.

    Attributes:
        id: Unique thread identifier
        user_id: ID of user who owns this thread
        org_id: ID of organization this thread belongs to
        name: Human-readable thread name
        created_at: Thread creation timestamp
        updated_at: Last update timestamp
        chat_messages: List of messages in this thread
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    org_id: str
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    chat_messages: list[ChatMessage] = Field(default_factory=list)

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class CreateChatThreadRequest(BaseModel):
    """Request model for creating a new chat thread."""

    user_id: str
    org_id: str
    name: str


class CreateChatMessageRequest(BaseModel):
    """Request model for creating a new chat message."""

    chat_thread_id: str
    sender_id: str | None = None
    sender_role: str
    content: dict[str, Any]
