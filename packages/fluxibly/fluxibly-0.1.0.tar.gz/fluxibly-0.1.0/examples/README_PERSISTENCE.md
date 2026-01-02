# Conversation Persistence Examples

This directory contains examples demonstrating the conversation persistence feature for the Fluxibly framework.

## Overview

The conversation persistence system enables:
- **Database-backed conversation storage** (currently mock in-memory, PostgreSQL support planned)
- **Multi-turn conversations** with full context preservation
- **Cross-session resumption** of conversations
- **Multi-user and multi-organization** support
- **Thread-based organization** of conversations

## Files

### Core Examples

1. **[persistent_conversation_demo.py](persistent_conversation_demo.py)**
   - Basic conversation thread creation and management
   - Multi-thread handling
   - Cross-session conversation resumption
   - Thread management operations (create, list, delete, clear)
   - Configuration-based setup

2. **[workflow_with_persistence.py](workflow_with_persistence.py)**
   - Integration with existing workflow system
   - Persistent stateful conversations
   - Multi-user workflow management
   - Context maintenance across conversation turns

3. **[test_persistent_rag_workflow.py](test_persistent_rag_workflow.py)** ⭐ **Comprehensive Test**
   - Full end-to-end workflow test
   - RAG template filling scenario
   - Multiple concurrent conversations
   - Conversation cleanup operations
   - Integration with ConversationHistory class

## Quick Start

### 1. Basic Conversation Management

```python
import asyncio
from fluxibly.state.manager import StateManager
from fluxibly.state.repository import MockConversationRepository

async def main():
    # Initialize state manager
    state_manager = StateManager(
        repository=MockConversationRepository(),
        user_id="alice",
        org_id="acme_corp"
    )

    # Create a conversation thread
    thread = await state_manager.create_thread("My Conversation")

    # Add messages
    await state_manager.add_message("user", "Hello!")
    await state_manager.add_message("assistant", "Hi there!")

    # Retrieve messages
    messages = await state_manager.get_messages()
    print(f"Conversation has {len(messages)} messages")

asyncio.run(main())
```

### 2. Integration with ConversationHistory

```python
from fluxibly.agent.conversation import ConversationHistory

# Create ConversationHistory with persistence
conv_history = ConversationHistory(
    max_messages=100,
    max_tokens=8000,
    state_manager=state_manager,
    persist_to_db=True  # Enable automatic persistence
)

# Messages are automatically saved to database
conv_history.add_user_message("What's the weather?")
conv_history.add_assistant_message("It's sunny today!")

# Load from database
await conv_history.load_from_db(thread_id)
```

### 3. Multi-turn Conversations

```python
# Session 1: Start conversation
thread = await state_manager.create_thread("Travel Planning")
await state_manager.add_message("user", "Plan a trip to Tokyo")
await state_manager.add_message("assistant", "I'll help you plan...")

# Session 2: Resume conversation (possibly in a new process)
await state_manager.set_current_thread(thread.id)
history = await state_manager.load_conversation_history()
# Continue conversation with full context
await state_manager.add_message("user", "What's the weather like?")
```

## Running the Examples

### Prerequisites

```bash
# Install dependencies (if not already installed)
uv add pydantic langchain

# Set up environment (optional, uses defaults)
cp .env.example .env
```

### Run Examples

```bash
# 1. Basic persistence demo
python examples/persistent_conversation_demo.py

# 2. Workflow integration
python examples/workflow_with_persistence.py

# 3. Comprehensive test (recommended to run first)
python examples/test_persistent_rag_workflow.py
```

## Example Output

When you run `test_persistent_rag_workflow.py`, you'll see:

```
================================================================================
COMPREHENSIVE PERSISTENT RAG WORKFLOW TEST SUITE
================================================================================

--- Test 1: Persistent RAG Workflow ---
✓ Created conversation thread: 91676a3e-d7ef-447c-9fb8-19d71ff7cd83
  Thread name: RAG Template Filling - Internal Communications Planning

SESSION 1: Initial Template Filling Request
✓ Stored user message in database
✓ Stored assistant response in database
✓ Conversation now has 2 messages

SESSION 2: Follow-up Question (same session)
✓ Follow-up answer stored
✓ Full conversation history: 4 messages

SESSION 3: Resume Conversation (simulated new session)
✓ Resumed thread: 91676a3e-d7ef-447c-9fb8-19d71ff7cd83
✓ Loaded 4 messages from database
✓ Final conversation: 6 messages across 3 turns

SESSION 4: Integration with ConversationHistory class
✓ Loaded 6 messages into ConversationHistory
✓ Added new message through ConversationHistory (auto-persisted)
✓ Database now contains 6 total messages

--- Test 2: Multiple Concurrent Conversations ---
✓ Organization 'edu_org' has 3 total threads
✓ User 'user1' has 2 threads
✓ User 'user2' has 1 threads
✓ Message isolation between threads verified

--- Test 3: Conversation Cleanup ---
✓ Cleared 3 messages from thread
✓ Thread deleted: True

ALL TESTS COMPLETED SUCCESSFULLY
```

## Key Features Demonstrated

### 1. Thread Management
- Create named conversation threads
- List threads by user or organization
- Switch between multiple active threads
- Delete threads and clear messages

### 2. Message Persistence
- Automatic storage of user and assistant messages
- Support for metadata and structured content
- Chronological message ordering
- Efficient retrieval with pagination

### 3. Context Preservation
- Multi-turn conversations with full history
- Context maintained across sessions
- Follow-up questions reference previous exchanges
- No information loss during resumption

### 4. Multi-user Support
- User and organization isolation
- Concurrent conversations by different users
- Message isolation between threads
- Flexible filtering and querying

### 5. Integration
- Works with existing ConversationHistory class
- Compatible with WorkflowSession pattern
- Pluggable repository architecture (mock/PostgreSQL)
- Environment-based configuration

## Configuration

### Environment Variables

```bash
# Database backend (mock or postgresql)
DB_BACKEND=mock

# PostgreSQL settings (when DB_BACKEND=postgresql)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fluxibly
DB_USER=postgres
DB_PASSWORD=your_password

# State management
ENABLE_DB_PERSISTENCE=true
DEFAULT_USER_ID=default_user
DEFAULT_ORG_ID=default_org
```

### Configuration in Code

```python
from fluxibly.state.config import StateConfig

# Load from environment
config = StateConfig.from_env()

# Create state manager with config
state_manager = StateManager(
    repository=create_repository(config.database),
    user_id=config.user_id,
    org_id=config.org_id
)
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Application Layer                                        │
│   ├── WorkflowSession                                   │
│   └── ConversationHistory                               │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ State Management Layer                                   │
│   ├── StateManager (High-level API)                     │
│   └── StateConfig (Configuration)                       │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ Repository Layer (Pluggable)                            │
│   ├── ConversationRepository (Interface)                │
│   ├── MockConversationRepository (In-memory)            │
│   └── PostgreSQLConversationRepository (Future)         │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ Database Models                                          │
│   ├── ChatThread (id, user_id, org_id, name, ...)      │
│   └── ChatMessage (id, thread_id, role, content, ...)  │
└─────────────────────────────────────────────────────────┘
```

## Use Cases

### 1. RAG Template Filling (Demonstrated)
- Multi-turn conversation about content creation
- Follow-up questions with context
- Resume work across sessions

### 2. Customer Support
- Maintain conversation history across support sessions
- Multiple concurrent support conversations
- Context-aware responses

### 3. Educational Chatbots
- Track student learning progress
- Multi-session tutoring conversations
- Personalized content delivery

### 4. Research Assistants
- Long-running research conversations
- Document analysis with follow-ups
- Cross-session research continuity

## Best Practices

1. **Thread Naming**: Use descriptive names
   ```python
   # Good
   await state_manager.create_thread("RAG: Internal Comms Planning - User123")

   # Avoid
   await state_manager.create_thread("Thread 1")
   ```

2. **Error Handling**: Always handle missing threads
   ```python
   thread = await state_manager.get_thread(thread_id)
   if not thread:
       logger.error(f"Thread {thread_id} not found")
       return
   ```

3. **Cleanup**: Clear old conversations periodically
   ```python
   # Clear messages but keep thread
   await state_manager.clear_thread(thread_id)

   # Or delete entire thread
   await state_manager.delete_thread(thread_id)
   ```

4. **Pagination**: Use limits for large conversations
   ```python
   # Get last 50 messages
   recent_messages = await state_manager.get_messages(limit=50)
   ```

## Testing

The examples include comprehensive tests covering:
- ✅ Basic CRUD operations
- ✅ Multi-turn conversations
- ✅ Cross-session resumption
- ✅ Multi-user scenarios
- ✅ Message isolation
- ✅ Cleanup operations
- ✅ Integration with existing classes

Run all tests:
```bash
python examples/test_persistent_rag_workflow.py
```

## Next Steps

1. **PostgreSQL Implementation**: Add production-ready database backend
2. **Advanced Queries**: Search, filtering, full-text search
3. **Performance**: Caching, lazy loading, batch operations
4. **Features**: Thread branching, message editing, conversation export

## Documentation

For detailed documentation, see:
- [docs/CONVERSATION_PERSISTENCE.md](../docs/CONVERSATION_PERSISTENCE.md) - Complete feature documentation
- [tests/unit/test_state_persistence.py](../tests/unit/test_state_persistence.py) - Unit tests

## Support

For issues or questions:
1. Check the [documentation](../docs/CONVERSATION_PERSISTENCE.md)
2. Review the [examples](.)
3. Run the [comprehensive test](test_persistent_rag_workflow.py)
4. Open an issue on GitHub

## License

See main project license.
