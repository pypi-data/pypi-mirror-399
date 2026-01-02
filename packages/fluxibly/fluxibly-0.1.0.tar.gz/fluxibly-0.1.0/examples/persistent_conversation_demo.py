"""Example demonstrating persistent conversation history with database backend.

This example shows how to:
1. Create a conversation thread
2. Add messages to the thread
3. Retrieve conversation history
4. Resume conversations across sessions
5. Manage multiple conversation threads
"""

import asyncio

from fluxibly.state.config import StateConfig
from fluxibly.state.manager import StateManager
from fluxibly.state.repository import MockConversationRepository


async def basic_conversation_example():
    """Basic example of creating and managing a conversation thread."""
    print("=== Basic Conversation Example ===\n")

    # Initialize state manager with mock repository
    state_manager = StateManager(
        repository=MockConversationRepository(),
        user_id="alice",
        org_id="acme_corp",
    )

    # Create a new conversation thread
    thread = await state_manager.create_thread("Product Planning Discussion")
    print(f"Created thread: {thread.id} - '{thread.name}'")

    # Add messages to the conversation
    await state_manager.add_message("user", "What features should we prioritize for Q1?")
    await state_manager.add_message(
        "assistant",
        "Based on customer feedback, I recommend: 1) Mobile app, 2) API improvements, 3) Dashboard analytics",
    )
    await state_manager.add_message("user", "Let's focus on the mobile app. What are the key requirements?")

    # Retrieve conversation history
    messages = await state_manager.get_messages()
    print(f"\nConversation has {len(messages)} messages:")
    for msg in messages:
        print(f"  [{msg.sender_role}]: {msg.content['text'][:60]}...")

    # Convert to conversation Message objects
    conv_messages = await state_manager.load_conversation_history()
    print(f"\nLoaded {len(conv_messages)} messages as conversation objects")


async def multi_thread_example():
    """Example of managing multiple conversation threads."""
    print("\n\n=== Multi-Thread Example ===\n")

    state_manager = StateManager(
        repository=MockConversationRepository(),
        user_id="bob",
        org_id="acme_corp",
    )

    # Create multiple threads
    thread1 = await state_manager.create_thread("Project Alpha Planning")
    await state_manager.add_message("user", "What's the timeline for Project Alpha?")
    await state_manager.add_message("assistant", "We're targeting Q2 2025 for the beta release.")

    thread2 = await state_manager.create_thread("Bug Triage Session")
    await state_manager.add_message("user", "What are the critical bugs for this sprint?")
    await state_manager.add_message("assistant", "I found 3 critical bugs in the authentication system.")

    thread3 = await state_manager.create_thread("Feature Brainstorming")
    await state_manager.add_message("user", "Ideas for improving user onboarding?")

    # List all threads
    threads = await state_manager.list_threads(user_id="bob")
    print(f"User 'bob' has {len(threads)} conversation threads:")
    for t in threads:
        print(f"  - {t.name} ({len(t.chat_messages)} messages)")

    # Switch between threads
    await state_manager.set_current_thread(thread1.id)
    await state_manager.add_message("user", "Can we accelerate the timeline?")

    messages = await state_manager.get_messages(thread1.id)
    print(f"\nThread '{thread1.name}' now has {len(messages)} messages")


async def conversation_resumption_example():
    """Example of resuming a conversation across sessions."""
    print("\n\n=== Conversation Resumption Example ===\n")

    # Session 1: Start a conversation
    print("Session 1: Starting conversation...")
    repo = MockConversationRepository()
    state_manager = StateManager(repository=repo, user_id="charlie", org_id="acme_corp")

    thread = await state_manager.create_thread("Travel Planning")
    thread_id = thread.id
    await state_manager.add_message("user", "I want to plan a trip to Tokyo")
    await state_manager.add_message("assistant", "Great! When are you planning to visit?")
    await state_manager.add_message("user", "February 2025, for 7 days")

    print(f"Created thread {thread_id} with 3 messages")

    # Session 2: Resume the conversation
    print("\nSession 2: Resuming conversation...")
    # Simulate a new session with the same repository
    new_state_manager = StateManager(repository=repo, user_id="charlie", org_id="acme_corp")

    await new_state_manager.set_current_thread(thread_id)
    await new_state_manager.add_message("user", "What's the weather like in Tokyo in February?")

    # Load full conversation history
    history = await new_state_manager.load_conversation_history()
    print(f"Resumed conversation with {len(history)} messages:")
    for msg in history:
        print(f"  [{msg.role}]: {msg.content[:50]}...")


async def thread_management_example():
    """Example of thread management operations."""
    print("\n\n=== Thread Management Example ===\n")

    state_manager = StateManager(
        repository=MockConversationRepository(),
        user_id="diana",
        org_id="acme_corp",
    )

    # Create and populate a thread
    thread = await state_manager.create_thread("Test Thread")
    await state_manager.add_message("user", "Message 1")
    await state_manager.add_message("assistant", "Response 1")
    await state_manager.add_message("user", "Message 2")

    print(f"Created thread with {len(await state_manager.get_messages())} messages")

    # Clear messages from thread
    cleared_count = await state_manager.clear_thread()
    print(f"Cleared {cleared_count} messages from thread")

    remaining = await state_manager.get_messages()
    print(f"Remaining messages: {len(remaining)}")

    # Delete the entire thread
    success = await state_manager.delete_thread()
    print(f"Thread deleted: {success}")

    # Verify deletion
    deleted_thread = await state_manager.get_thread(thread.id)
    print(f"Thread exists after deletion: {deleted_thread is not None}")


async def config_based_example():
    """Example using configuration from environment."""
    print("\n\n=== Configuration-Based Example ===\n")

    # Load configuration from environment
    config = StateConfig.from_env()
    print(f"Database backend: {config.database.backend}")
    print(f"Persistence enabled: {config.enable_persistence}")
    print(f"Default user: {config.user_id}")
    print(f"Default org: {config.org_id}")

    # Create state manager with config
    if config.database.backend == "mock":
        repository = MockConversationRepository()
    else:
        # In production, would create PostgreSQL repository here
        print("Note: PostgreSQL repository not implemented in this example")
        repository = MockConversationRepository()

    state_manager = StateManager(
        repository=repository,
        user_id=config.user_id,
        org_id=config.org_id,
    )

    thread = await state_manager.create_thread("Config-based Conversation")
    await state_manager.add_message("user", "This conversation uses environment configuration")

    print(f"\nCreated thread: {thread.name}")


async def main():
    """Run all examples."""
    await basic_conversation_example()
    await multi_thread_example()
    await conversation_resumption_example()
    await thread_management_example()
    await config_based_example()

    print("\n\n=== Examples Complete ===")
    print("\nKey Takeaways:")
    print("1. Use StateManager to manage conversation threads")
    print("2. Threads persist messages in database backend")
    print("3. Multiple threads can be managed per user/org")
    print("4. Conversations can be resumed across sessions")
    print("5. Configuration can be loaded from environment variables")


if __name__ == "__main__":
    asyncio.run(main())
