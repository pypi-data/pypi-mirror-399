"""Conversation history management for agents.

This module provides conversation tracking with automatic memory management
and context window handling, with optional database persistence.
"""

import asyncio
import logging
from collections import deque
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Message(BaseModel):
    """A single message in conversation history.

    Attributes:
        role: Message role ("user", "assistant", "system", "tool")
        content: Message content/text
        metadata: Optional metadata (tool calls, timestamps, etc.)
    """

    role: str = Field(..., description="Message role (user/assistant/system/tool)")
    content: str = Field(..., description="Message content")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Optional metadata")


class ConversationHistory:
    """Manages conversation history with memory and context window management.

    Provides structured storage for conversation turns with automatic truncation
    based on context window limits. Optionally syncs with database backend for persistence.

    Attributes:
        messages: Deque of Message objects (in-memory cache)
        max_messages: Maximum number of messages to keep (None = unlimited)
        max_tokens: Maximum tokens to keep (approximate, None = unlimited)
        state_manager: Optional StateManager for database persistence
        persist_to_db: Whether to persist messages to database
    """

    def __init__(
        self,
        max_messages: int | None = None,
        max_tokens: int | None = None,
        state_manager: Any | None = None,
        persist_to_db: bool = False,
    ) -> None:
        """Initialize conversation history.

        Args:
            max_messages: Maximum messages to retain (oldest removed first)
            max_tokens: Approximate maximum tokens (for context window management)
            state_manager: Optional StateManager for database persistence
            persist_to_db: Whether to automatically persist messages to database
        """
        self.messages: deque[Message] = deque(maxlen=max_messages)
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self.state_manager = state_manager
        self.persist_to_db = persist_to_db

    def add_message(self, role: str, content: str, metadata: dict[str, Any] | None = None) -> None:
        """Add a message to conversation history.

        Args:
            role: Message role ("user", "assistant", "system", "tool")
            content: Message content
            metadata: Optional metadata dictionary
        """
        message = Message(role=role, content=content, metadata=metadata or {})
        self.messages.append(message)

        # Truncate if we exceed token limits (approximate)
        if self.max_tokens is not None:
            self._truncate_to_token_limit()

        # Persist to database if enabled
        if self.persist_to_db and self.state_manager:
            self._persist_message_sync(role, content, metadata)

    def add_user_message(self, content: str, metadata: dict[str, Any] | None = None) -> None:
        """Add a user message to history.

        Args:
            content: User message content
            metadata: Optional metadata
        """
        self.add_message("user", content, metadata)

    def add_assistant_message(self, content: str, metadata: dict[str, Any] | None = None) -> None:
        """Add an assistant message to history.

        Args:
            content: Assistant message content
            metadata: Optional metadata
        """
        self.add_message("assistant", content, metadata)

    def add_system_message(self, content: str, metadata: dict[str, Any] | None = None) -> None:
        """Add a system message to history.

        Args:
            content: System message content
            metadata: Optional metadata
        """
        self.add_message("system", content, metadata)

    def add_tool_result(self, tool_name: str, result: str, metadata: dict[str, Any] | None = None) -> None:
        """Add a tool execution result to history.

        Args:
            tool_name: Name of the tool that was executed
            result: Tool execution result
            metadata: Optional metadata
        """
        meta = metadata or {}
        meta["tool_name"] = tool_name
        self.add_message("tool", result, meta)

    def get_messages(self, last_n: int | None = None) -> list[Message]:
        """Get messages from history.

        Args:
            last_n: Number of most recent messages to retrieve (None = all)

        Returns:
            List of Message objects
        """
        if last_n is None:
            return list(self.messages)
        return list(self.messages)[-last_n:]

    def format_for_prompt(self, include_system: bool = False, last_n: int | None = None) -> str:
        """Format conversation history for inclusion in prompt.

        Args:
            include_system: Whether to include system messages
            last_n: Number of recent messages to include (None = all)

        Returns:
            Formatted string representation of conversation history
        """
        messages = self.get_messages(last_n)

        if not messages:
            return ""

        formatted_lines = []
        for msg in messages:
            if msg.role == "system" and not include_system:
                continue

            if msg.role == "tool":
                tool_name = msg.metadata.get("tool_name", "unknown")
                formatted_lines.append(f"Tool ({tool_name}): {msg.content}")
            elif msg.role == "user":
                formatted_lines.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                formatted_lines.append(f"Assistant: {msg.content}")
            elif msg.role == "system":
                formatted_lines.append(f"System: {msg.content}")

        return "\n".join(formatted_lines)

    def clear(self) -> None:
        """Clear all conversation history."""
        self.messages.clear()

    async def load_from_db(self, thread_id: str | None = None) -> None:
        """Load conversation history from database.

        Args:
            thread_id: Thread ID to load (uses current thread if None)
        """
        if not self.state_manager:
            logger.warning("No state_manager configured, cannot load from database")
            return

        try:
            conversation_messages = await self.state_manager.load_conversation_history(thread_id)
            self.messages.clear()
            for msg in conversation_messages:
                self.messages.append(msg)
            logger.info(f"Loaded {len(conversation_messages)} messages from database")
        except Exception:
            logger.exception("Failed to load conversation history from database")

    def _persist_message_sync(self, role: str, content: str, metadata: dict[str, Any] | None) -> None:
        """Persist message to database synchronously using asyncio.

        Args:
            role: Message role
            content: Message content
            metadata: Optional metadata
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If event loop is running, schedule as a task
                asyncio.create_task(self.state_manager.add_message(role, content, metadata=metadata))
            else:
                # If no event loop, run synchronously
                loop.run_until_complete(self.state_manager.add_message(role, content, metadata=metadata))
        except Exception:
            logger.exception("Failed to persist message to database")

    def _truncate_to_token_limit(self) -> None:
        """Truncate history to fit within token limit (approximate).

        Uses rough estimate of ~4 chars per token.
        """
        if self.max_tokens is None:
            return

        total_chars = sum(len(msg.content) for msg in self.messages)
        estimated_tokens = total_chars / 4  # Rough approximation

        # Remove oldest messages until we're under the limit
        while estimated_tokens > self.max_tokens and len(self.messages) > 1:
            removed = self.messages.popleft()
            total_chars -= len(removed.content)
            estimated_tokens = total_chars / 4

    def __len__(self) -> int:
        """Return number of messages in history."""
        return len(self.messages)

    def __repr__(self) -> str:
        """String representation."""
        return f"ConversationHistory(messages={len(self.messages)}, max_messages={self.max_messages})"
