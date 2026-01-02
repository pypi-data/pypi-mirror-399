"""Repository interfaces and implementations for conversation persistence.

This module defines the abstract repository interface and concrete implementations
for storing conversation threads and messages (mock and PostgreSQL).
"""

import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime
from typing import Any

from fluxibly.state.models import (
    ChatMessage,
    ChatThread,
    CreateChatMessageRequest,
    CreateChatThreadRequest,
)

logger = logging.getLogger(__name__)


class ConversationRepository(ABC):
    """Abstract interface for conversation persistence."""

    @abstractmethod
    async def create_thread(self, request: CreateChatThreadRequest) -> ChatThread:
        """Create a new conversation thread."""
        pass

    @abstractmethod
    async def get_thread(self, thread_id: str) -> ChatThread | None:
        """Get a thread by ID."""
        pass

    @abstractmethod
    async def update_thread(self, thread_id: str, **kwargs: Any) -> ChatThread | None:
        """Update thread metadata."""
        pass

    @abstractmethod
    async def delete_thread(self, thread_id: str) -> bool:
        """Delete a thread and all its messages."""
        pass

    @abstractmethod
    async def list_threads(
        self, user_id: str | None = None, org_id: str | None = None, limit: int = 100
    ) -> list[ChatThread]:
        """List threads with optional filters."""
        pass

    @abstractmethod
    async def create_message(self, request: CreateChatMessageRequest) -> ChatMessage:
        """Add a message to a thread."""
        pass

    @abstractmethod
    async def get_messages(
        self, thread_id: str, limit: int | None = None, offset: int = 0
    ) -> list[ChatMessage]:
        """Get messages from a thread."""
        pass

    @abstractmethod
    async def delete_message(self, message_id: str) -> bool:
        """Delete a specific message."""
        pass

    @abstractmethod
    async def clear_messages(self, thread_id: str) -> int:
        """Clear all messages from a thread. Returns count of deleted messages."""
        pass


class MockConversationRepository(ConversationRepository):
    """In-memory mock implementation of conversation repository.

    This is useful for development, testing, and running without a database.
    Data is stored in memory and will be lost when the process exits.
    """

    def __init__(self) -> None:
        """Initialize mock repository with in-memory storage."""
        self._threads: dict[str, ChatThread] = {}
        self._messages: dict[str, ChatMessage] = {}
        self._thread_messages: dict[str, list[str]] = defaultdict(list)  # thread_id -> [message_ids]

    async def create_thread(self, request: CreateChatThreadRequest) -> ChatThread:
        """Create a new conversation thread."""
        thread = ChatThread(
            user_id=request.user_id,
            org_id=request.org_id,
            name=request.name,
        )
        self._threads[thread.id] = thread
        self._thread_messages[thread.id] = []
        logger.debug(f"Created thread {thread.id} for user {request.user_id}")
        return thread

    async def get_thread(self, thread_id: str) -> ChatThread | None:
        """Get a thread by ID."""
        thread = self._threads.get(thread_id)
        if thread:
            # Load messages
            message_ids = self._thread_messages.get(thread_id, [])
            thread.chat_messages = [self._messages[mid] for mid in message_ids if mid in self._messages]
        return thread

    async def update_thread(self, thread_id: str, **kwargs: Any) -> ChatThread | None:
        """Update thread metadata."""
        thread = self._threads.get(thread_id)
        if not thread:
            return None

        # Update allowed fields
        for key, value in kwargs.items():
            if key in ("name", "user_id", "org_id"):
                setattr(thread, key, value)

        thread.updated_at = datetime.utcnow()
        logger.debug(f"Updated thread {thread_id}")
        return thread

    async def delete_thread(self, thread_id: str) -> bool:
        """Delete a thread and all its messages."""
        if thread_id not in self._threads:
            return False

        # Delete all messages
        message_ids = self._thread_messages.get(thread_id, [])
        for mid in message_ids:
            self._messages.pop(mid, None)

        # Delete thread
        del self._threads[thread_id]
        del self._thread_messages[thread_id]
        logger.debug(f"Deleted thread {thread_id} and {len(message_ids)} messages")
        return True

    async def list_threads(
        self, user_id: str | None = None, org_id: str | None = None, limit: int = 100
    ) -> list[ChatThread]:
        """List threads with optional filters."""
        threads = list(self._threads.values())

        # Apply filters
        if user_id:
            threads = [t for t in threads if t.user_id == user_id]
        if org_id:
            threads = [t for t in threads if t.org_id == org_id]

        # Sort by updated_at descending
        threads.sort(key=lambda t: t.updated_at, reverse=True)

        # Apply limit
        return threads[:limit]

    async def create_message(self, request: CreateChatMessageRequest) -> ChatMessage:
        """Add a message to a thread."""
        # Check thread exists
        if request.chat_thread_id not in self._threads:
            raise ValueError(f"Thread {request.chat_thread_id} does not exist")

        message = ChatMessage(
            chat_thread_id=request.chat_thread_id,
            sender_id=request.sender_id,
            sender_role=request.sender_role,
            content=request.content,
        )

        self._messages[message.id] = message
        self._thread_messages[request.chat_thread_id].append(message.id)

        # Update thread's updated_at
        thread = self._threads[request.chat_thread_id]
        thread.updated_at = datetime.utcnow()

        logger.debug(f"Created message {message.id} in thread {request.chat_thread_id}")
        return message

    async def get_messages(
        self, thread_id: str, limit: int | None = None, offset: int = 0
    ) -> list[ChatMessage]:
        """Get messages from a thread."""
        message_ids = self._thread_messages.get(thread_id, [])
        messages = [self._messages[mid] for mid in message_ids if mid in self._messages]

        # Sort by created_at ascending
        messages.sort(key=lambda m: m.created_at)

        # Apply offset and limit
        if offset > 0:
            messages = messages[offset:]
        if limit is not None:
            messages = messages[:limit]

        return messages

    async def delete_message(self, message_id: str) -> bool:
        """Delete a specific message."""
        message = self._messages.get(message_id)
        if not message:
            return False

        # Remove from thread's message list
        thread_id = message.chat_thread_id
        if thread_id in self._thread_messages:
            self._thread_messages[thread_id] = [
                mid for mid in self._thread_messages[thread_id] if mid != message_id
            ]

        # Delete message
        del self._messages[message_id]
        logger.debug(f"Deleted message {message_id}")
        return True

    async def clear_messages(self, thread_id: str) -> int:
        """Clear all messages from a thread."""
        message_ids = self._thread_messages.get(thread_id, [])
        count = len(message_ids)

        for mid in message_ids:
            self._messages.pop(mid, None)

        self._thread_messages[thread_id] = []
        logger.debug(f"Cleared {count} messages from thread {thread_id}")
        return count

    def get_stats(self) -> dict[str, int]:
        """Get repository statistics (useful for debugging/monitoring)."""
        return {
            "threads": len(self._threads),
            "messages": len(self._messages),
            "total_thread_messages": sum(len(msgs) for msgs in self._thread_messages.values()),
        }
