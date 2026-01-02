"""Tests for state management and database persistence."""

import pytest

from fluxibly.state.manager import StateManager
from fluxibly.state.models import CreateChatMessageRequest, CreateChatThreadRequest
from fluxibly.state.repository import MockConversationRepository


@pytest.fixture
def mock_repository():
    """Create a mock repository for testing."""
    return MockConversationRepository()


@pytest.fixture
def state_manager(mock_repository):
    """Create a state manager with mock repository."""
    return StateManager(
        repository=mock_repository,
        user_id="test_user",
        org_id="test_org",
    )


class TestMockConversationRepository:
    """Tests for MockConversationRepository."""

    @pytest.mark.anyio
    async def test_create_thread(self, mock_repository):
        """Test creating a conversation thread."""
        request = CreateChatThreadRequest(
            user_id="user123",
            org_id="org456",
            name="Test Conversation",
        )
        thread = await mock_repository.create_thread(request)

        assert thread.id is not None
        assert thread.user_id == "user123"
        assert thread.org_id == "org456"
        assert thread.name == "Test Conversation"
        assert thread.created_at is not None
        assert thread.updated_at is not None
        assert len(thread.chat_messages) == 0

    @pytest.mark.anyio
    async def test_get_thread(self, mock_repository):
        """Test retrieving a thread by ID."""
        request = CreateChatThreadRequest(
            user_id="user123",
            org_id="org456",
            name="Test Conversation",
        )
        created_thread = await mock_repository.create_thread(request)

        retrieved_thread = await mock_repository.get_thread(created_thread.id)
        assert retrieved_thread is not None
        assert retrieved_thread.id == created_thread.id
        assert retrieved_thread.name == "Test Conversation"

    @pytest.mark.anyio
    async def test_get_nonexistent_thread(self, mock_repository):
        """Test retrieving a thread that doesn't exist."""
        thread = await mock_repository.get_thread("nonexistent_id")
        assert thread is None

    @pytest.mark.anyio
    async def test_update_thread(self, mock_repository):
        """Test updating thread metadata."""
        request = CreateChatThreadRequest(
            user_id="user123",
            org_id="org456",
            name="Original Name",
        )
        thread = await mock_repository.create_thread(request)

        updated_thread = await mock_repository.update_thread(thread.id, name="Updated Name")
        assert updated_thread is not None
        assert updated_thread.name == "Updated Name"

    @pytest.mark.anyio
    async def test_delete_thread(self, mock_repository):
        """Test deleting a thread."""
        request = CreateChatThreadRequest(
            user_id="user123",
            org_id="org456",
            name="Test Conversation",
        )
        thread = await mock_repository.create_thread(request)

        success = await mock_repository.delete_thread(thread.id)
        assert success is True

        retrieved = await mock_repository.get_thread(thread.id)
        assert retrieved is None

    @pytest.mark.anyio
    async def test_list_threads(self, mock_repository):
        """Test listing threads with filters."""
        # Create threads for different users and orgs
        await mock_repository.create_thread(
            CreateChatThreadRequest(user_id="user1", org_id="org1", name="Thread 1")
        )
        await mock_repository.create_thread(
            CreateChatThreadRequest(user_id="user1", org_id="org2", name="Thread 2")
        )
        await mock_repository.create_thread(
            CreateChatThreadRequest(user_id="user2", org_id="org1", name="Thread 3")
        )

        # List all threads
        all_threads = await mock_repository.list_threads()
        assert len(all_threads) == 3

        # Filter by user
        user1_threads = await mock_repository.list_threads(user_id="user1")
        assert len(user1_threads) == 2

        # Filter by org
        org1_threads = await mock_repository.list_threads(org_id="org1")
        assert len(org1_threads) == 2

        # Filter by both
        specific_threads = await mock_repository.list_threads(user_id="user1", org_id="org1")
        assert len(specific_threads) == 1

    @pytest.mark.anyio
    async def test_create_message(self, mock_repository):
        """Test creating a message in a thread."""
        thread = await mock_repository.create_thread(
            CreateChatThreadRequest(user_id="user1", org_id="org1", name="Test")
        )

        request = CreateChatMessageRequest(
            chat_thread_id=thread.id,
            sender_id="user1",
            sender_role="user",
            content={"type": "text", "text": "Hello, world!"},
        )
        message = await mock_repository.create_message(request)

        assert message.id is not None
        assert message.chat_thread_id == thread.id
        assert message.sender_role == "user"
        assert message.content["text"] == "Hello, world!"

    @pytest.mark.anyio
    async def test_create_message_invalid_thread(self, mock_repository):
        """Test creating a message in a non-existent thread."""
        request = CreateChatMessageRequest(
            chat_thread_id="invalid_thread_id",
            sender_role="user",
            content={"type": "text", "text": "Hello"},
        )

        with pytest.raises(ValueError, match="Thread .* does not exist"):
            await mock_repository.create_message(request)

    @pytest.mark.anyio
    async def test_get_messages(self, mock_repository):
        """Test retrieving messages from a thread."""
        thread = await mock_repository.create_thread(
            CreateChatThreadRequest(user_id="user1", org_id="org1", name="Test")
        )

        # Add messages
        for i in range(5):
            await mock_repository.create_message(
                CreateChatMessageRequest(
                    chat_thread_id=thread.id,
                    sender_role="user" if i % 2 == 0 else "assistant",
                    content={"type": "text", "text": f"Message {i}"},
                )
            )

        # Get all messages
        messages = await mock_repository.get_messages(thread.id)
        assert len(messages) == 5

        # Get limited messages
        limited = await mock_repository.get_messages(thread.id, limit=3)
        assert len(limited) == 3

        # Get with offset
        offset_messages = await mock_repository.get_messages(thread.id, offset=2)
        assert len(offset_messages) == 3

    @pytest.mark.anyio
    async def test_clear_messages(self, mock_repository):
        """Test clearing all messages from a thread."""
        thread = await mock_repository.create_thread(
            CreateChatThreadRequest(user_id="user1", org_id="org1", name="Test")
        )

        # Add messages
        for i in range(3):
            await mock_repository.create_message(
                CreateChatMessageRequest(
                    chat_thread_id=thread.id,
                    sender_role="user",
                    content={"type": "text", "text": f"Message {i}"},
                )
            )

        count = await mock_repository.clear_messages(thread.id)
        assert count == 3

        messages = await mock_repository.get_messages(thread.id)
        assert len(messages) == 0


class TestStateManager:
    """Tests for StateManager with database persistence."""

    @pytest.mark.anyio
    async def test_create_thread(self, state_manager):
        """Test creating a thread via StateManager."""
        thread = await state_manager.create_thread("Test Conversation")

        assert thread.id is not None
        assert thread.name == "Test Conversation"
        assert thread.user_id == "test_user"
        assert thread.org_id == "test_org"
        assert state_manager._current_thread_id == thread.id

    @pytest.mark.anyio
    async def test_add_message(self, state_manager):
        """Test adding messages to a thread."""
        thread = await state_manager.create_thread("Test")

        message = await state_manager.add_message("user", "Hello, world!")
        assert message.sender_role == "user"
        assert message.content["text"] == "Hello, world!"
        assert message.chat_thread_id == thread.id

    @pytest.mark.anyio
    async def test_add_message_no_thread(self, state_manager):
        """Test adding message without active thread."""
        with pytest.raises(ValueError, match="No active thread"):
            await state_manager.add_message("user", "Hello")

    @pytest.mark.anyio
    async def test_get_messages(self, state_manager):
        """Test retrieving messages from current thread."""
        await state_manager.create_thread("Test")

        await state_manager.add_message("user", "Message 1")
        await state_manager.add_message("assistant", "Message 2")

        messages = await state_manager.get_messages()
        assert len(messages) == 2
        assert messages[0].sender_role == "user"
        assert messages[1].sender_role == "assistant"

    @pytest.mark.anyio
    async def test_clear_thread(self, state_manager):
        """Test clearing messages from thread."""
        await state_manager.create_thread("Test")

        await state_manager.add_message("user", "Message 1")
        await state_manager.add_message("user", "Message 2")

        count = await state_manager.clear_thread()
        assert count == 2

        messages = await state_manager.get_messages()
        assert len(messages) == 0

    @pytest.mark.anyio
    async def test_convert_to_conversation_messages(self, state_manager):
        """Test converting ChatMessage to Message objects."""
        await state_manager.create_thread("Test")

        await state_manager.add_message("user", "Hello", metadata={"source": "test"})

        chat_messages = await state_manager.get_messages()
        conv_messages = state_manager.convert_to_conversation_messages(chat_messages)

        assert len(conv_messages) == 1
        assert conv_messages[0].role == "user"
        assert conv_messages[0].content == "Hello"
        assert conv_messages[0].metadata.get("source") == "test"

    @pytest.mark.anyio
    async def test_load_conversation_history(self, state_manager):
        """Test loading conversation history as Message objects."""
        await state_manager.create_thread("Test")

        await state_manager.add_message("user", "Question")
        await state_manager.add_message("assistant", "Answer")

        history = await state_manager.load_conversation_history()

        assert len(history) == 2
        assert history[0].role == "user"
        assert history[0].content == "Question"
        assert history[1].role == "assistant"
        assert history[1].content == "Answer"

    @pytest.mark.anyio
    async def test_set_current_thread(self, state_manager):
        """Test switching between threads."""
        thread1 = await state_manager.create_thread("Thread 1")
        thread2 = await state_manager.create_thread("Thread 2")

        await state_manager.set_current_thread(thread1.id)
        assert state_manager._current_thread_id == thread1.id

        await state_manager.add_message("user", "In thread 1")

        await state_manager.set_current_thread(thread2.id)
        await state_manager.add_message("user", "In thread 2")

        # Check thread 1 messages
        messages1 = await state_manager.get_messages(thread1.id)
        assert len(messages1) == 1
        assert messages1[0].content["text"] == "In thread 1"

        # Check thread 2 messages
        messages2 = await state_manager.get_messages(thread2.id)
        assert len(messages2) == 1
        assert messages2[0].content["text"] == "In thread 2"
