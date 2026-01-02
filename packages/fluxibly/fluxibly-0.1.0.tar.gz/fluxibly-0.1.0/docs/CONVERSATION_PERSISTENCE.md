# Conversation Persistence

This document describes the conversation persistence feature that allows storing and retrieving conversation history from a database backend.

## Overview

The conversation persistence system provides:
- **Database-backed conversation storage** (mock in-memory or PostgreSQL)
- **Thread-based conversation management** (multiple conversations per user/org)
- **Seamless integration** with existing ConversationHistory class
- **Cross-session conversation resumption**
- **Multi-user and multi-organization support**

## Architecture

### Core Components

1. **Database Models** (`fluxibly/state/models.py`)
   - `ChatThread`: Represents a conversation thread
   - `ChatMessage`: Individual messages within a thread
   - Request models for creating threads and messages

2. **Repository Interface** (`fluxibly/state/repository.py`)
   - `ConversationRepository`: Abstract interface for persistence
   - `MockConversationRepository`: In-memory implementation for development/testing
   - Future: `PostgreSQLConversationRepository` for production use

3. **State Manager** (`fluxibly/state/manager.py`)
   - Manages conversation threads and messages
   - Provides high-level API for persistence operations
   - Converts between database and conversation message formats

4. **Configuration** (`fluxibly/state/config.py`)
   - `DatabaseConfig`: Database connection settings
   - `StateConfig`: State management configuration
   - Environment variable support

## Database Schema

### ChatThread

```python
id: str              # Unique thread identifier (UUID)
user_id: str         # User who owns this thread
org_id: str          # Organization this thread belongs to
name: str            # Human-readable thread name
created_at: datetime # Thread creation timestamp
updated_at: datetime # Last update timestamp
```

### ChatMessage

```python
id: str              # Unique message identifier (UUID)
chat_thread_id: str  # Reference to parent thread
sender_id: str?      # Optional user ID of sender
sender_role: str     # Role: user, assistant, system, tool
content: dict        # Message content: {'type': 'text', 'text': str, 'metadata': dict}
created_at: datetime # Message creation timestamp
updated_at: datetime # Last update timestamp
```

## Usage

### Basic Usage with StateManager

```python
from fluxibly.state.manager import StateManager
from fluxibly.state.repository import MockConversationRepository

# Initialize state manager
state_manager = StateManager(
    repository=MockConversationRepository(),
    user_id="alice",
    org_id="acme_corp"
)

# Create a conversation thread
thread = await state_manager.create_thread("Product Planning Discussion")

# Add messages
await state_manager.add_message("user", "What features should we prioritize?")
await state_manager.add_message("assistant", "I recommend focusing on...")

# Retrieve messages
messages = await state_manager.get_messages()

# Load as conversation Message objects
history = await state_manager.load_conversation_history()
```

### Integration with ConversationHistory

```python
from fluxibly.agent.conversation import ConversationHistory
from fluxibly.state.manager import StateManager

# Create state manager and thread
state_manager = StateManager(...)
thread = await state_manager.create_thread("My Conversation")

# Create ConversationHistory with persistence
conv_history = ConversationHistory(
    max_messages=100,
    max_tokens=8000,
    state_manager=state_manager,
    persist_to_db=True  # Enable automatic persistence
)

# Add messages (automatically persisted)
conv_history.add_user_message("Hello!")
conv_history.add_assistant_message("Hi there!")

# Load existing conversation
await conv_history.load_from_db(thread_id)
```

### Managing Multiple Threads

```python
# Create multiple threads
thread1 = await state_manager.create_thread("Project Alpha")
thread2 = await state_manager.create_thread("Bug Triage")

# Switch between threads
await state_manager.set_current_thread(thread1.id)
await state_manager.add_message("user", "Message in thread 1")

await state_manager.set_current_thread(thread2.id)
await state_manager.add_message("user", "Message in thread 2")

# List threads
threads = await state_manager.list_threads(user_id="alice")
```

### Resuming Conversations

```python
# Session 1: Start conversation
thread = await state_manager.create_thread("Travel Planning")
thread_id = thread.id
await state_manager.add_message("user", "Plan a trip to Tokyo")
await state_manager.add_message("assistant", "I'll help you plan...")

# Session 2: Resume conversation (possibly in a new process)
new_state_manager = StateManager(repository=same_repository)
await new_state_manager.set_current_thread(thread_id)

# Load history
history = await new_state_manager.load_conversation_history()
# Continue conversation
await new_state_manager.add_message("user", "What's the weather like?")
```

## Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Database backend (mock or postgresql)
DB_BACKEND=mock

# PostgreSQL settings (when DB_BACKEND=postgresql)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fluxibly
DB_USER=postgres
DB_PASSWORD=your_password

# Connection pool
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# State management
ENABLE_DB_PERSISTENCE=true
DEFAULT_USER_ID=default_user
DEFAULT_ORG_ID=default_org
```

### Loading Configuration

```python
from fluxibly.state.config import StateConfig, DatabaseConfig

# Load from environment
config = StateConfig.from_env()

# Use in state manager
state_manager = StateManager(
    repository=create_repository(config.database),
    user_id=config.user_id,
    org_id=config.org_id
)
```

## Mock vs PostgreSQL

### Mock Repository (Development/Testing)

- **Storage**: In-memory (data lost on process exit)
- **Setup**: No external dependencies
- **Use case**: Development, testing, demos
- **Performance**: Very fast

```python
from fluxibly.state.repository import MockConversationRepository

repo = MockConversationRepository()
state_manager = StateManager(repository=repo)
```

### PostgreSQL Repository (Production)

- **Storage**: Persistent database
- **Setup**: Requires PostgreSQL server
- **Use case**: Production deployments
- **Performance**: Network-dependent, supports concurrent access

```python
# TODO: Implement PostgreSQLConversationRepository
from fluxibly.state.repository import PostgreSQLConversationRepository

repo = PostgreSQLConversationRepository(connection_string=...)
state_manager = StateManager(repository=repo)
```

## API Reference

### StateManager Methods

#### Thread Management
- `create_thread(name, user_id, org_id)` - Create new conversation thread
- `get_thread(thread_id)` - Retrieve thread by ID
- `set_current_thread(thread_id)` - Set active thread
- `get_current_thread()` - Get current active thread
- `list_threads(user_id, org_id, limit)` - List threads with filters
- `delete_thread(thread_id)` - Delete thread and messages

#### Message Management
- `add_message(role, content, thread_id, sender_id, metadata)` - Add message
- `get_messages(thread_id, limit, offset)` - Get messages
- `clear_thread(thread_id)` - Clear all messages from thread

#### Conversion
- `convert_to_conversation_messages(chat_messages)` - Convert to Message objects
- `load_conversation_history(thread_id)` - Load as conversation Messages

### ConversationHistory Integration

- `__init__(max_messages, max_tokens, state_manager, persist_to_db)` - Initialize
- `load_from_db(thread_id)` - Load conversation from database

## Examples

See the following example files for complete usage patterns:

- `examples/persistent_conversation_demo.py` - Basic persistence operations
- `examples/workflow_with_persistence.py` - Integration with workflows
- `tests/unit/test_state_persistence.py` - Comprehensive test suite

## Future Enhancements

### Planned Features

1. **PostgreSQL Repository Implementation**
   - SQLAlchemy-based implementation
   - Connection pooling
   - Migration support

2. **Advanced Queries**
   - Search messages by content
   - Filter by date range
   - Full-text search

3. **Performance Optimizations**
   - Message caching
   - Lazy loading
   - Batch operations

4. **Additional Backends**
   - Redis for caching
   - MongoDB for document storage
   - DynamoDB for AWS deployments

5. **Conversation Features**
   - Thread forking/branching
   - Message editing/deletion
   - Conversation summarization
   - Export/import capabilities

## Best Practices

### 1. Thread Naming
Use descriptive thread names that reflect the conversation purpose:
```python
# Good
await state_manager.create_thread("Hotel Search - Tokyo Feb 2025")

# Avoid
await state_manager.create_thread("Thread 1")
```

### 2. User/Org Organization
Use meaningful user and organization IDs:
```python
state_manager = StateManager(
    repository=repo,
    user_id=f"user_{user.email}",
    org_id=f"org_{organization.slug}"
)
```

### 3. Error Handling
Always handle potential errors:
```python
try:
    thread = await state_manager.get_thread(thread_id)
    if thread is None:
        # Handle missing thread
        logger.warning(f"Thread {thread_id} not found")
except Exception:
    logger.exception("Failed to retrieve thread")
```

### 4. Resource Cleanup
Clear threads when no longer needed:
```python
# Clear messages but keep thread
await state_manager.clear_thread()

# Delete entire thread
await state_manager.delete_thread()
```

### 5. Concurrent Access
The mock repository is thread-safe for single-process use. For multi-process or distributed deployments, use a proper database backend (PostgreSQL).

## Troubleshooting

### Issue: Messages not persisting

**Solution**: Ensure `persist_to_db=True` when creating ConversationHistory:
```python
conv_history = ConversationHistory(
    state_manager=state_manager,
    persist_to_db=True  # Required for persistence
)
```

### Issue: Thread not found

**Solution**: Verify thread ID and ensure it exists:
```python
thread = await state_manager.get_thread(thread_id)
if not thread:
    logger.error(f"Thread {thread_id} does not exist")
```

### Issue: Configuration not loading

**Solution**: Check environment variables are set:
```python
import os
print(f"DB_BACKEND: {os.getenv('DB_BACKEND')}")
print(f"ENABLE_DB_PERSISTENCE: {os.getenv('ENABLE_DB_PERSISTENCE')}")
```

## Migration Guide

### From In-Memory to Database Persistence

1. **Update imports**:
```python
from fluxibly.state.manager import StateManager
from fluxibly.state.repository import MockConversationRepository
```

2. **Initialize StateManager**:
```python
# Old: Using ConversationHistory alone
conv_history = ConversationHistory()

# New: With persistence
state_manager = StateManager(repository=MockConversationRepository())
thread = await state_manager.create_thread("My Conversation")
conv_history = ConversationHistory(
    state_manager=state_manager,
    persist_to_db=True
)
```

3. **Update message handling**:
```python
# Messages now automatically persist when persist_to_db=True
conv_history.add_user_message("Hello")
# Message is stored in database
```

4. **Load existing conversations**:
```python
# Retrieve conversation from database
await conv_history.load_from_db(thread_id)
```

## License

See main project license.
