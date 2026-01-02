"""State management for LangGraph-based orchestration.

This module provides state management utilities for the agent execution flow,
including persistent conversation storage via database backends.
"""

import logging
from typing import Any

from fluxibly.agent.conversation import Message
from fluxibly.state.models import (
    ChatMessage,
    ChatThread,
    CreateChatMessageRequest,
    CreateChatThreadRequest,
)
from fluxibly.state.repository import ConversationRepository, MockConversationRepository
from fluxibly.state.schema import AgentState

logger = logging.getLogger(__name__)


class StateManager:
    """Manages agent state and conversation persistence.

    Provides utilities for state initialization, updates, queries,
    and persistent conversation history via database backends.
    """

    def __init__(
        self,
        repository: ConversationRepository | None = None,
        user_id: str = "default_user",
        org_id: str = "default_org",
    ) -> None:
        """Initialize state manager.

        Args:
            repository: Conversation repository (defaults to mock)
            user_id: Default user ID for creating threads
            org_id: Default organization ID for creating threads
        """
        self.repository = repository or MockConversationRepository()
        self.user_id = user_id
        self.org_id = org_id
        self._current_thread_id: str | None = None

    async def create_thread(self, name: str, user_id: str | None = None, org_id: str | None = None) -> ChatThread:
        """Create a new conversation thread.

        Args:
            name: Thread name/title
            user_id: User ID (defaults to instance user_id)
            org_id: Organization ID (defaults to instance org_id)

        Returns:
            Created thread
        """
        request = CreateChatThreadRequest(
            user_id=user_id or self.user_id,
            org_id=org_id or self.org_id,
            name=name,
        )
        thread = await self.repository.create_thread(request)
        self._current_thread_id = thread.id
        logger.info(f"Created conversation thread: {thread.id} - {name}")
        return thread

    async def get_thread(self, thread_id: str) -> ChatThread | None:
        """Get a conversation thread by ID.

        Args:
            thread_id: Thread identifier

        Returns:
            Thread with messages, or None if not found
        """
        return await self.repository.get_thread(thread_id)

    async def set_current_thread(self, thread_id: str) -> None:
        """Set the current active thread.

        Args:
            thread_id: Thread to make active
        """
        thread = await self.repository.get_thread(thread_id)
        if not thread:
            raise ValueError(f"Thread {thread_id} not found")
        self._current_thread_id = thread_id
        logger.debug(f"Set current thread to {thread_id}")

    async def get_current_thread(self) -> ChatThread | None:
        """Get the current active thread.

        Returns:
            Current thread or None
        """
        if not self._current_thread_id:
            return None
        return await self.repository.get_thread(self._current_thread_id)

    async def add_message(
        self,
        role: str,
        content: str | dict[str, Any],
        thread_id: str | None = None,
        sender_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ChatMessage:
        """Add a message to a thread.

        Args:
            role: Message role (user, assistant, system, tool)
            content: Message content (string or dict)
            thread_id: Thread ID (uses current thread if None)
            sender_id: Optional sender user ID
            metadata: Optional message metadata

        Returns:
            Created message

        Raises:
            ValueError: If no thread is active or specified
        """
        target_thread_id = thread_id or self._current_thread_id
        if not target_thread_id:
            raise ValueError("No active thread. Create or set a thread first.")

        # Normalize content to dict format
        if isinstance(content, str):
            content_dict: dict[str, Any] = {"type": "text", "text": content}
        else:
            content_dict = dict(content)

        # Add metadata if provided
        if metadata:
            content_dict["metadata"] = metadata

        request = CreateChatMessageRequest(
            chat_thread_id=target_thread_id,
            sender_id=sender_id,
            sender_role=role,
            content=content_dict,
        )
        message = await self.repository.create_message(request)
        logger.debug(f"Added {role} message to thread {target_thread_id}")
        return message

    async def get_messages(
        self, thread_id: str | None = None, limit: int | None = None, offset: int = 0
    ) -> list[ChatMessage]:
        """Get messages from a thread.

        Args:
            thread_id: Thread ID (uses current thread if None)
            limit: Maximum number of messages to return
            offset: Number of messages to skip

        Returns:
            List of messages

        Raises:
            ValueError: If no thread is active or specified
        """
        target_thread_id = thread_id or self._current_thread_id
        if not target_thread_id:
            raise ValueError("No active thread. Create or set a thread first.")

        return await self.repository.get_messages(target_thread_id, limit=limit, offset=offset)

    async def clear_thread(self, thread_id: str | None = None) -> int:
        """Clear all messages from a thread.

        Args:
            thread_id: Thread ID (uses current thread if None)

        Returns:
            Number of messages deleted

        Raises:
            ValueError: If no thread is active or specified
        """
        target_thread_id = thread_id or self._current_thread_id
        if not target_thread_id:
            raise ValueError("No active thread. Create or set a thread first.")

        count = await self.repository.clear_messages(target_thread_id)
        logger.info(f"Cleared {count} messages from thread {target_thread_id}")
        return count

    async def delete_thread(self, thread_id: str | None = None) -> bool:
        """Delete a thread and all its messages.

        Args:
            thread_id: Thread ID (uses current thread if None)

        Returns:
            True if deleted, False if not found

        Raises:
            ValueError: If no thread is active or specified
        """
        target_thread_id = thread_id or self._current_thread_id
        if not target_thread_id:
            raise ValueError("No active thread. Create or set a thread first.")

        success = await self.repository.delete_thread(target_thread_id)
        if success and target_thread_id == self._current_thread_id:
            self._current_thread_id = None
        return success

    async def list_threads(self, user_id: str | None = None, org_id: str | None = None, limit: int = 100) -> list[ChatThread]:
        """List conversation threads.

        Args:
            user_id: Filter by user ID
            org_id: Filter by organization ID
            limit: Maximum threads to return

        Returns:
            List of threads
        """
        return await self.repository.list_threads(user_id=user_id, org_id=org_id, limit=limit)

    def convert_to_conversation_messages(self, chat_messages: list[ChatMessage]) -> list[Message]:
        """Convert ChatMessage objects to conversation Message objects.

        Args:
            chat_messages: List of database messages

        Returns:
            List of conversation messages
        """
        messages = []
        for msg in chat_messages:
            # Extract text from content
            text = msg.content.get("text", "")
            metadata = msg.content.get("metadata", {})

            messages.append(Message(role=msg.sender_role, content=text, metadata=metadata))
        return messages

    async def load_conversation_history(self, thread_id: str | None = None) -> list[Message]:
        """Load conversation history as Message objects.

        Args:
            thread_id: Thread ID (uses current thread if None)

        Returns:
            List of conversation messages

        Raises:
            ValueError: If no thread is active or specified
        """
        chat_messages = await self.get_messages(thread_id)
        return self.convert_to_conversation_messages(chat_messages)

    def create_initial_state(self, input_data: dict[str, Any]) -> AgentState:
        """Create initial state from input data.

        Args:
            input_data: Input data containing submission information

        Returns:
            Initial agent state
        """
        return AgentState(
            messages=[],
            plan=[],
            context=input_data,
            mcp_results=[],
            metadata={},
            extracted_content=[],
            content_tree={},
            error=None,
        )

    def update_state(self, state: AgentState, updates: dict[str, Any]) -> AgentState:
        """Update agent state with new data.

        Args:
            state: Current agent state
            updates: State updates to apply

        Returns:
            Updated agent state
        """
        for key, value in updates.items():
            if hasattr(state, key):
                setattr(state, key, value)
        return state

    def get_context(self, state: AgentState, key: str) -> Any:
        """Retrieve value from state context.

        Args:
            state: Current agent state
            key: Context key to retrieve

        Returns:
            Context value or None if not found
        """
        return state["context"].get(key) if state.get("context") else None
