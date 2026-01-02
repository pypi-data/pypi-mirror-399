"""
Test RAG assistant for template-filling task.

This example demonstrates how the RAG assistant uses:
1. Template structure (outline.md)
2. One-shot example (example_oneshot.md)
3. Source documents with file_names filtering
4. Query rewriting strategy for comprehensive retrieval
"""

import asyncio
import logging

from dotenv import load_dotenv

from fluxibly import WorkflowSession

# Load environment variables
load_dotenv("local.env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Enable DEBUG logging for orchestrator to see plan details
orchestrator_logger = logging.getLogger("fluxibly.orchestrator")
orchestrator_logger.setLevel(logging.DEBUG)


async def test_template_filling():
    """Test RAG assistant filling template with source documents."""

    logger.info("=" * 80)
    logger.info("Starting template-filling task with RAG assistant...")
    logger.info("=" * 80)

    # Load template and example files
    with open("./examples/resources/outline.md", encoding="utf-8") as f:
        template_content = f.read()

    with open("./examples/resources/example_oneshot.md", encoding="utf-8") as f:
        example_content = f.read()

    # Define the task with template, example, and source documents
    task_description = f"""
    BẮT BUỘC: Viết toàn bộ bài giảng bằng tiếng Việt. KHÔNG được dùng tiếng Anh.

    Tôi cần bạn tạo bài giảng HOÀN CHỈNH, CHI TIẾT theo template có sẵn về chủ đề: "Lập kế hoạch, chiến lược Truyền thông nội bộ"

    TEMPLATE STRUCTURE:
    {template_content}

    ONE-SHOT EXAMPLE - ĐÂY LÀ MẪU BẠN CẦN THEO:
    {example_content}

    Source documents cần sử dụng:
    - "Current Trends and Issues in Internal Communication Theory and Practice (New Perspectives in Organizational Communication).pdf"
    - "Internal Communications A Manual for Practitioners.pdf"
    """

    logger.info("Topic: Lập kế hoạch, chiến lược Truyền thông nội bộ")
    logger.info(
        "Source documents: "
        "Current Trends and Issues in Internal Communication Theory and Practice, "
        "Internal Communications A Manual for Practitioners"
    )

    try:
        # Execute with RAG assistant profile
        async with WorkflowSession(profile="rag_assistant") as session:
            logger.info("\nExecuting template-filling workflow...")
            response = await session.execute(task_description)

            logger.info("\n" + "=" * 80)
            logger.info("EXECUTION COMPLETED")
            logger.info("=" * 80)
            logger.info(f"\nResponse:\n{response}\n")
            
            follow_up_question = "Hãy cung cấp thêm ví dụ thực tiễn về chiến lược truyền thông nội bộ từ các tài liệu đã cho."
            logger.info(f"\nFollow-up Question: {follow_up_question}")
            follow_up_response = await session.execute(follow_up_question)
            logger.info(f"\nFollow-up Response:\n{follow_up_response}\n")

    except Exception as e:
        logger.exception(f"Error during execution: {e}")
        raise


async def main():
    """Run all tests."""
    logger.info("=" * 80)
    logger.info("RAG ASSISTANT TEMPLATE-FILLING TEST")
    logger.info("=" * 80)

    # Test 2: Full template filling
    logger.info("\n--- Test 2: Full Template Filling ---\n")
    await test_template_filling()

    logger.info("\n" + "=" * 80)
    logger.info("ALL TESTS COMPLETED")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
