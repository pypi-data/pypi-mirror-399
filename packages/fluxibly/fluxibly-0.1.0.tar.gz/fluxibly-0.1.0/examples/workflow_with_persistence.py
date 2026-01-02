"""Example demonstrating workflow integration with persistent conversation history.

This example shows how to integrate the database persistence layer
with the existing workflow system for stateful conversations.
"""

import asyncio

from fluxibly.agent.conversation import ConversationHistory
from fluxibly.state.manager import StateManager
from fluxibly.state.repository import MockConversationRepository


async def workflow_persistence_example():
    """Example of using persistent storage with workflow conversations."""
    print("=== Workflow with Persistence Example ===\n")

    # Setup state manager
    state_manager = StateManager(
        repository=MockConversationRepository(),
        user_id="workflow_user",
        org_id="demo_org",
    )

    # Create a conversation thread
    thread = await state_manager.create_thread("Travel Assistant Session")
    print(f"Created conversation thread: {thread.id}\n")

    # Create ConversationHistory with database persistence
    conv_history = ConversationHistory(
        max_messages=100,
        max_tokens=8000,
        state_manager=state_manager,
        persist_to_db=True,
    )

    # Simulate a multi-turn conversation
    print("Turn 1: User asks about Tokyo hotels")
    conv_history.add_user_message("Find me hotels in Tokyo for February 2025")

    # Simulate assistant response
    assistant_response = """Found 5 hotels in Tokyo:
1. Park Hyatt Tokyo - $450/night
2. Aman Tokyo - $800/night
3. Hotel Gracery Shinjuku - $120/night
4. Shibuya Excel Hotel - $100/night
5. Tokyo Station Hotel - $200/night"""
    conv_history.add_assistant_message(assistant_response)

    print("Turn 2: Follow-up question")
    conv_history.add_user_message("Which one is closest to Shibuya Station?")
    conv_history.add_assistant_message(
        "The Shibuya Excel Hotel is closest to Shibuya Station, just a 5-minute walk away."
    )

    print("Turn 3: Another follow-up")
    conv_history.add_user_message("Does it have good reviews?")
    conv_history.add_assistant_message(
        "Yes, Shibuya Excel Hotel has 4.2/5 stars with 1,250 reviews. "
        "Guests praise its location and cleanliness."
    )

    # Display conversation
    print("\n--- Conversation History ---")
    print(conv_history.format_for_prompt())

    # Verify messages were persisted
    persisted_messages = await state_manager.get_messages()
    print(f"\n{len(persisted_messages)} messages persisted to database")

    return thread.id, state_manager


async def resume_workflow_example(thread_id: str, state_manager: StateManager):
    """Example of resuming a workflow conversation from database."""
    print("\n\n=== Resuming Workflow Conversation ===\n")

    # Set the thread
    await state_manager.set_current_thread(thread_id)

    # Load conversation history from database
    conv_history = ConversationHistory(max_messages=100)

    # Manually load from database
    loaded_messages = await state_manager.load_conversation_history()
    for msg in loaded_messages:
        conv_history.messages.append(msg)

    print(f"Loaded {len(loaded_messages)} messages from database\n")

    # Continue the conversation
    print("Continuing conversation...")
    conv_history.add_user_message("Book the Shibuya Excel Hotel for 3 nights")

    # With persistence enabled, this would save to DB
    conv_history_with_db = ConversationHistory(
        max_messages=100,
        state_manager=state_manager,
        persist_to_db=True,
    )
    # Load existing messages
    for msg in loaded_messages:
        conv_history_with_db.messages.append(msg)

    # Add new message (will persist)
    conv_history_with_db.add_assistant_message(
        "I've initiated the booking for Shibuya Excel Hotel for 3 nights in February 2025. "
        "Please provide your payment details to confirm."
    )

    print("\n--- Updated Conversation ---")
    print(conv_history_with_db.format_for_prompt())

    # Verify persistence
    all_messages = await state_manager.get_messages()
    print(f"\n{len(all_messages)} total messages in database")


async def multi_user_workflows():
    """Example of managing workflows for multiple users."""
    print("\n\n=== Multi-User Workflow Example ===\n")

    repo = MockConversationRepository()

    # User 1: Travel planning
    user1_manager = StateManager(repository=repo, user_id="user1", org_id="travel_org")
    thread1 = await user1_manager.create_thread("Paris Trip Planning")
    await user1_manager.add_message("user", "Plan a 5-day trip to Paris")
    await user1_manager.add_message("assistant", "I'll help you plan your Paris trip!")

    # User 2: Hotel search
    user2_manager = StateManager(repository=repo, user_id="user2", org_id="travel_org")
    thread2 = await user2_manager.create_thread("London Hotel Search")
    await user2_manager.add_message("user", "Find hotels in London under $200/night")
    await user2_manager.add_message("assistant", "Searching for affordable hotels in London...")

    # User 3: Multiple threads
    user3_manager = StateManager(repository=repo, user_id="user3", org_id="travel_org")
    thread3a = await user3_manager.create_thread("Rome Itinerary")
    await user3_manager.add_message("user", "Create a 3-day Rome itinerary")

    thread3b = await user3_manager.create_thread("Venice Restaurant Recommendations")
    await user3_manager.add_message("user", "Best restaurants in Venice?")

    # List threads by organization
    org_threads = await user1_manager.list_threads(org_id="travel_org")
    print(f"Organization 'travel_org' has {len(org_threads)} total threads:")
    for t in org_threads:
        print(f"  - User {t.user_id}: {t.name}")

    # List threads by user
    user3_threads = await user3_manager.list_threads(user_id="user3")
    print(f"\nUser 'user3' has {len(user3_threads)} threads:")
    for t in user3_threads:
        print(f"  - {t.name}")


async def conversation_history_with_context():
    """Example showing how context is maintained across turns."""
    print("\n\n=== Context Maintenance Example ===\n")

    state_manager = StateManager(
        repository=MockConversationRepository(),
        user_id="context_user",
        org_id="demo_org",
    )

    thread = await state_manager.create_thread("Restaurant Search with Context")

    # Build conversation with context
    turns = [
        ("user", "Find Italian restaurants in New York"),
        ("assistant", "I found 10 Italian restaurants in New York. Here are the top 5..."),
        ("user", "Which ones have outdoor seating?"),  # Refers to previous results
        (
            "assistant",
            "Of the restaurants I mentioned, 3 have outdoor seating: Carbone, L'Artusi, and Don Angie.",
        ),
        ("user", "What about the first one?"),  # Refers to Carbone
        ("assistant", "Carbone has a beautiful outdoor patio in Greenwich Village..."),
        ("user", "Make a reservation there"),  # Clear context dependency
        ("assistant", "I'll make a reservation at Carbone for you..."),
    ]

    for role, content in turns:
        await state_manager.add_message(role, content)

    # Load full history
    history = await state_manager.load_conversation_history()

    print("Conversation demonstrates context maintenance:")
    for i, msg in enumerate(history, 1):
        content_preview = msg.content[:60] + "..." if len(msg.content) > 60 else msg.content
        print(f"{i}. [{msg.role}]: {content_preview}")

    print("\nNote: Later messages reference earlier context without re-stating details")


async def main():
    """Run all examples."""
    # Example 1: Basic workflow with persistence
    thread_id, state_manager = await workflow_persistence_example()

    # Example 2: Resume workflow
    await resume_workflow_example(thread_id, state_manager)

    # Example 3: Multi-user workflows
    await multi_user_workflows()

    # Example 4: Context maintenance
    await conversation_history_with_context()

    print("\n\n=== All Examples Complete ===")
    print("\nIntegration Points:")
    print("1. ConversationHistory can be configured with state_manager for persistence")
    print("2. Set persist_to_db=True to automatically save messages")
    print("3. Use load_conversation_history() to restore conversations")
    print("4. StateManager handles thread creation and message storage")
    print("5. Multiple users/threads can be managed concurrently")


if __name__ == "__main__":
    asyncio.run(main())
