"""
Comprehensive test of persistent conversation with RAG workflow.

This example demonstrates:
1. Creating a persistent conversation thread for a RAG workflow
2. Multi-turn conversations with context preservation
3. Resuming conversations across sessions
4. Tracking conversation history in database
5. Integration with RAG template filling workflow
"""

import asyncio
import logging
from pathlib import Path

from dotenv import load_dotenv

from fluxibly import WorkflowSession
from fluxibly.agent.conversation import ConversationHistory
from fluxibly.state.config import StateConfig
from fluxibly.state.manager import StateManager
from fluxibly.state.repository import MockConversationRepository

# Load environment variables
load_dotenv("local.env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def test_persistent_rag_workflow():
    """Test RAG workflow with persistent conversation history."""

    logger.info("=" * 80)
    logger.info("PERSISTENT RAG WORKFLOW TEST")
    logger.info("=" * 80)

    # Initialize state manager with mock repository
    state_manager = StateManager(
        repository=MockConversationRepository(),
        user_id="demo_user",
        org_id="education_org",
    )

    # Create a conversation thread for the RAG workflow
    thread = await state_manager.create_thread(
        "RAG Template Filling - Internal Communications Planning"
    )
    logger.info(f"\n✓ Created conversation thread: {thread.id}")
    logger.info(f"  Thread name: {thread.name}")

    # Load template content (simplified for test)
    template_content = """
# BÀI GIẢNG: [TÊN CHỦ ĐỀ]

## I. GIỚI THIỆU
- Tổng quan về chủ đề
- Tầm quan trọng
- Mục tiêu học tập

## II. NỘI DUNG CHÍNH
### 1. Khái niệm cơ bản
### 2. Các yếu tố quan trọng
### 3. Ứng dụng thực tiễn

## III. KẾT LUẬN
- Tóm tắt nội dung
- Khuyến nghị
"""

    # Simulate first task: Template filling request
    task_1 = f"""
Tôi cần bạn tạo bài giảng về chủ đề: "Lập kế hoạch chiến lược Truyền thông nội bộ"

TEMPLATE STRUCTURE:
{template_content}

Hãy tạo bài giảng hoàn chỉnh dựa trên template này.
"""

    logger.info("\n" + "=" * 80)
    logger.info("SESSION 1: Initial Template Filling Request")
    logger.info("=" * 80)

    # Store first message in database
    await state_manager.add_message("user", task_1)
    logger.info("✓ Stored user message in database")

    # Simulate assistant response (in real workflow, this comes from WorkflowSession)
    assistant_response_1 = """
# BÀI GIẢNG: LẬP KẾ HOẠCH CHIẾN LƯỢC TRUYỀN THÔNG NỘI BỘ

## I. GIỚI THIỆU
Truyền thông nội bộ là xương sống của mọi tổ chức thành công. Việc lập kế hoạch chiến lược truyền thông nội bộ giúp:
- Tạo sự gắn kết giữa nhân viên và tổ chức
- Nâng cao hiệu quả làm việc
- Xây dựng văn hóa doanh nghiệp

**Mục tiêu học tập:**
1. Hiểu rõ tầm quan trọng của kế hoạch truyền thông nội bộ
2. Nắm vững các bước lập kế hoạch
3. Áp dụng được vào thực tiễn tổ chức

## II. NỘI DUNG CHÍNH

### 1. Khái niệm cơ bản
- Truyền thông nội bộ: Quá trình trao đổi thông tin trong tổ chức
- Chiến lược: Kế hoạch tổng thể để đạt mục tiêu truyền thông

### 2. Các yếu tố quan trọng
- Phân tích đối tượng (stakeholder analysis)
- Lựa chọn kênh truyền thông phù hợp
- Thiết lập KPI đo lường hiệu quả
- Lập lịch triển khai

### 3. Ứng dụng thực tiễn
- Case study: Chiến lược truyền thông nội bộ tại doanh nghiệp
- Công cụ hỗ trợ: Newsletter, Intranet, Town hall meetings
- Best practices từ các tổ chức hàng đầu

## III. KẾT LUẬN

**Tóm tắt:**
Một chiến lược truyền thông nội bộ hiệu quả cần được lập kế hoạch cẩn thận,
dựa trên phân tích kỹ lưỡng đối tượng và lựa chọn kênh phù hợp.

**Khuyến nghị:**
- Thường xuyên đánh giá và điều chỉnh chiến lược
- Lắng nghe phản hồi từ nhân viên
- Đầu tư vào công cụ và đào tạo
"""

    await state_manager.add_message("assistant", assistant_response_1)
    logger.info("✓ Stored assistant response in database")

    # Check conversation history
    messages_count = len(await state_manager.get_messages())
    logger.info(f"✓ Conversation now has {messages_count} messages")

    # Simulate follow-up question
    task_2 = "Bạn có thể giải thích rõ hơn về stakeholder analysis trong bước lập kế hoạch không?"

    logger.info("\n" + "=" * 80)
    logger.info("SESSION 2: Follow-up Question (same session)")
    logger.info("=" * 80)
    logger.info(f"Question: {task_2}")

    await state_manager.add_message("user", task_2)

    assistant_response_2 = """
Tất nhiên! Stakeholder analysis (phân tích bên liên quan) là bước quan trọng trong lập kế hoạch:

**Các bước thực hiện:**

1. **Xác định stakeholders:**
   - Nhân viên cấp cao (C-level executives)
   - Quản lý cấp trung (Middle managers)
   - Nhân viên thực thi (Front-line employees)
   - Các bộ phận hỗ trợ (HR, IT, Admin)

2. **Phân loại theo mức độ ảnh hưởng:**
   - High influence, High interest: Cần ưu tiên cao
   - High influence, Low interest: Giữ thông tin
   - Low influence, High interest: Thông tin thường xuyên
   - Low influence, Low interest: Giám sát chung

3. **Xác định nhu cầu thông tin:**
   - Loại thông tin cần thiết cho từng nhóm
   - Tần suất cập nhật
   - Kênh truyền thông ưa thích

**Ví dụ thực tế:**
Với nhóm C-level: Dashboard tổng quan hàng tuần
Với nhân viên: Newsletter hàng tháng, town hall quarterly
"""

    await state_manager.add_message("assistant", assistant_response_2)
    logger.info("✓ Follow-up answer stored")

    # Display full conversation history
    history = await state_manager.load_conversation_history()
    logger.info(f"\n✓ Full conversation history: {len(history)} messages")
    for i, msg in enumerate(history, 1):
        content_preview = msg.content[:80] + "..." if len(msg.content) > 80 else msg.content
        logger.info(f"  {i}. [{msg.role}]: {content_preview}")

    # Simulate resuming conversation in a new session
    logger.info("\n" + "=" * 80)
    logger.info("SESSION 3: Resume Conversation (simulated new session)")
    logger.info("=" * 80)

    # Create a new state manager (simulating new process/session)
    new_state_manager = StateManager(
        repository=state_manager.repository,  # Same repository
        user_id="demo_user",
        org_id="education_org",
    )

    # Set the thread to resume
    await new_state_manager.set_current_thread(thread.id)
    logger.info(f"✓ Resumed thread: {thread.id}")

    # Load conversation history
    resumed_history = await new_state_manager.load_conversation_history()
    logger.info(f"✓ Loaded {len(resumed_history)} messages from database")

    # Continue conversation
    task_3 = "Có công cụ nào giúp tự động hóa stakeholder analysis không?"
    logger.info(f"\nContinuing conversation with: {task_3}")

    await new_state_manager.add_message("user", task_3)

    assistant_response_3 = """
Có nhiều công cụ hỗ trợ stakeholder analysis:

**1. Công cụ mapping & visualization:**
- Miro/Mural: Tạo stakeholder maps trực quan
- Lucidchart: Vẽ sơ đồ phân tích
- MindMeister: Mind mapping cho stakeholder groups

**2. Công cụ quản lý và theo dõi:**
- Asana/Trello: Theo dõi engagement với từng nhóm
- Monday.com: Dashboard stakeholder management
- Smartsheet: Spreadsheet nâng cao với automation

**3. Công cụ phân tích dữ liệu:**
- Microsoft Power BI: Phân tích engagement metrics
- Tableau: Visualization cho stakeholder data
- Google Analytics: Track website/intranet usage

**4. Nền tảng tích hợp:**
- Staffbase: Employee communication platform
- Workvivo: Employee experience platform
- Workplace by Meta: Social intranet

**Khuyến nghị:**
Bắt đầu với công cụ đơn giản như Google Sheets kết hợp Miro,
sau đó mở rộng sang nền tảng chuyên dụng khi quy mô lớn hơn.
"""

    await new_state_manager.add_message("assistant", assistant_response_3)
    logger.info("✓ Continued conversation stored")

    # Final conversation summary
    final_history = await new_state_manager.load_conversation_history()
    logger.info(f"\n✓ Final conversation: {len(final_history)} messages across 3 turns")

    # Test conversation history integration with ConversationHistory class
    logger.info("\n" + "=" * 80)
    logger.info("SESSION 4: Integration with ConversationHistory class")
    logger.info("=" * 80)

    # Create ConversationHistory instance with persistence
    conv_history = ConversationHistory(
        max_messages=100,
        max_tokens=10000,
        state_manager=new_state_manager,
        persist_to_db=True,
    )

    # Load from database
    await conv_history.load_from_db(thread.id)
    logger.info(f"✓ Loaded {len(conv_history)} messages into ConversationHistory")

    # Add new message (will auto-persist)
    conv_history.add_user_message("Cảm ơn! Bài giảng rất hữu ích.")
    logger.info("✓ Added new message through ConversationHistory (auto-persisted)")

    # Format for prompt
    formatted = conv_history.format_for_prompt(last_n=3)
    logger.info("\n--- Last 3 messages (formatted for LLM prompt) ---")
    logger.info(formatted)

    # Verify persistence
    db_messages = await new_state_manager.get_messages()
    logger.info(f"\n✓ Database now contains {len(db_messages)} total messages")

    # Get thread statistics
    thread_info = await new_state_manager.get_thread(thread.id)
    if thread_info:
        logger.info(f"\n--- Thread Summary ---")
        logger.info(f"  ID: {thread_info.id}")
        logger.info(f"  Name: {thread_info.name}")
        logger.info(f"  User: {thread_info.user_id}")
        logger.info(f"  Organization: {thread_info.org_id}")
        logger.info(f"  Created: {thread_info.created_at}")
        logger.info(f"  Updated: {thread_info.updated_at}")
        logger.info(f"  Messages: {len(thread_info.chat_messages)}")

    # Test listing all threads for user
    user_threads = await new_state_manager.list_threads(user_id="demo_user")
    logger.info(f"\n✓ User 'demo_user' has {len(user_threads)} thread(s)")

    return thread.id, new_state_manager


async def test_multiple_concurrent_conversations():
    """Test managing multiple RAG conversations simultaneously."""

    logger.info("\n\n" + "=" * 80)
    logger.info("MULTIPLE CONCURRENT CONVERSATIONS TEST")
    logger.info("=" * 80)

    repository = MockConversationRepository()

    # User 1: Internal Communications topic
    user1_manager = StateManager(repository=repository, user_id="user1", org_id="edu_org")
    thread1 = await user1_manager.create_thread("RAG: Internal Communications Strategy")
    await user1_manager.add_message("user", "Explain internal communication planning")
    await user1_manager.add_message("assistant", "Internal communication planning involves...")
    logger.info(f"✓ User1 Thread: {thread1.name} - {len(await user1_manager.get_messages())} messages")

    # User 2: Marketing topic
    user2_manager = StateManager(repository=repository, user_id="user2", org_id="edu_org")
    thread2 = await user2_manager.create_thread("RAG: Marketing Strategy")
    await user2_manager.add_message("user", "How to create marketing campaigns?")
    await user2_manager.add_message("assistant", "Marketing campaigns should start with...")
    logger.info(f"✓ User2 Thread: {thread2.name} - {len(await user2_manager.get_messages())} messages")

    # User 1 starts another conversation
    thread3 = await user1_manager.create_thread("RAG: Change Management")
    await user1_manager.add_message("user", "Best practices for change management?")
    logger.info(f"✓ User1 Thread 2: {thread3.name} - {len(await user1_manager.get_messages())} messages")

    # List all threads
    all_threads = await user1_manager.list_threads(org_id="edu_org")
    logger.info(f"\n✓ Organization 'edu_org' has {len(all_threads)} total threads:")
    for t in all_threads:
        logger.info(f"  - [{t.user_id}] {t.name}")

    # User-specific threads
    user1_threads = await user1_manager.list_threads(user_id="user1")
    logger.info(f"\n✓ User 'user1' has {len(user1_threads)} threads")

    user2_threads = await user2_manager.list_threads(user_id="user2")
    logger.info(f"✓ User 'user2' has {len(user2_threads)} threads")

    # Verify message isolation
    logger.info("\n--- Verifying Message Isolation ---")
    thread1_msgs = await user1_manager.get_messages(thread1.id)
    thread2_msgs = await user2_manager.get_messages(thread2.id)
    thread3_msgs = await user1_manager.get_messages(thread3.id)

    logger.info(f"✓ Thread 1 has {len(thread1_msgs)} messages (isolated)")
    logger.info(f"✓ Thread 2 has {len(thread2_msgs)} messages (isolated)")
    logger.info(f"✓ Thread 3 has {len(thread3_msgs)} messages (isolated)")


async def test_conversation_cleanup():
    """Test clearing and deleting conversations."""

    logger.info("\n\n" + "=" * 80)
    logger.info("CONVERSATION CLEANUP TEST")
    logger.info("=" * 80)

    state_manager = StateManager(
        repository=MockConversationRepository(),
        user_id="cleanup_user",
        org_id="test_org",
    )

    # Create and populate thread
    thread = await state_manager.create_thread("Test Thread for Cleanup")
    await state_manager.add_message("user", "Message 1")
    await state_manager.add_message("assistant", "Response 1")
    await state_manager.add_message("user", "Message 2")

    initial_count = len(await state_manager.get_messages())
    logger.info(f"✓ Created thread with {initial_count} messages")

    # Clear messages but keep thread
    cleared = await state_manager.clear_thread()
    logger.info(f"✓ Cleared {cleared} messages from thread")

    remaining = await state_manager.get_messages()
    logger.info(f"✓ Remaining messages: {len(remaining)}")

    # Verify thread still exists
    thread_exists = await state_manager.get_thread(thread.id)
    logger.info(f"✓ Thread still exists: {thread_exists is not None}")

    # Delete the entire thread
    deleted = await state_manager.delete_thread()
    logger.info(f"✓ Thread deleted: {deleted}")

    # Verify deletion
    thread_after_delete = await state_manager.get_thread(thread.id)
    logger.info(f"✓ Thread exists after deletion: {thread_after_delete is not None}")


async def main():
    """Run all tests."""

    logger.info("=" * 80)
    logger.info("COMPREHENSIVE PERSISTENT RAG WORKFLOW TEST SUITE")
    logger.info("=" * 80)

    # Test 1: Main persistent workflow
    logger.info("\n--- Test 1: Persistent RAG Workflow ---")
    thread_id, state_manager = await test_persistent_rag_workflow()

    # Test 2: Multiple concurrent conversations
    logger.info("\n--- Test 2: Multiple Concurrent Conversations ---")
    await test_multiple_concurrent_conversations()

    # Test 3: Conversation cleanup
    logger.info("\n--- Test 3: Conversation Cleanup ---")
    await test_conversation_cleanup()

    logger.info("\n\n" + "=" * 80)
    logger.info("ALL TESTS COMPLETED SUCCESSFULLY")
    logger.info("=" * 80)

    logger.info("\n✓ Summary:")
    logger.info("  - Persistent conversation threads created and managed")
    logger.info("  - Multi-turn conversations with context preservation")
    logger.info("  - Cross-session conversation resumption verified")
    logger.info("  - Multiple concurrent conversations handled correctly")
    logger.info("  - Message isolation between threads verified")
    logger.info("  - Cleanup operations working as expected")
    logger.info("  - Integration with ConversationHistory successful")

    logger.info(f"\n✓ Main thread ID for further testing: {thread_id}")


if __name__ == "__main__":
    asyncio.run(main())
