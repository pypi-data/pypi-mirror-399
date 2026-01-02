"""
Debug test for RAG template-filling with detailed logging of all steps.

This test logs:
1. Input prompt to the agent
2. Plan generation (all steps)
3. Each tool call (rag-search) with parameters and results
4. Final synthesis prompt
5. Final response

Use this to debug why the output is in English instead of Vietnamese.
"""

import asyncio
import logging
from pathlib import Path

from dotenv import load_dotenv

from fluxibly import WorkflowSession

# Load environment variables
load_dotenv("local.env")

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("debug_template_filling.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Enable DEBUG for all fluxibly components
logging.getLogger("fluxibly").setLevel(logging.DEBUG)


async def test_with_full_debug():
    """Test template filling with comprehensive debug logging."""

    logger.info("=" * 100)
    logger.info("DEBUG TEST: Template Filling with Step-by-Step Logging")
    logger.info("=" * 100)

    # Load template and example files
    template_path = Path("outline.md")
    example_path = Path("example_oneshot.md")

    if not template_path.exists():
        logger.error(f"Template file not found: {template_path}")
        return

    if not example_path.exists():
        logger.error(f"Example file not found: {example_path}")
        return

    with open(template_path, encoding="utf-8") as f:
        template_content = f.read()
        logger.info(f"\n--- TEMPLATE LOADED ({len(template_content)} chars) ---")
        logger.info(f"First 200 chars:\n{template_content[:200]}...")

    with open(example_path, encoding="utf-8") as f:
        example_content = f.read()
        logger.info(f"\n--- EXAMPLE LOADED ({len(example_content)} chars) ---")
        logger.info(f"First 200 chars:\n{example_content[:200]}...")

    # Define the task
    task_description = f"""
BẮT BUỘC: Viết toàn bộ bài giảng bằng tiếng Việt. KHÔNG được dùng tiếng Anh.

Tôi cần bạn tạo bài giảng HOÀN CHỈNH, CHI TIẾT về chủ đề: "Lập kế hoạch, chiến lược Truyền thông nội bộ"

TEMPLATE STRUCTURE:
{template_content}

ONE-SHOT EXAMPLE (ĐÂY LÀ MẪU BẠN CẦN THEO):
{example_content}

QUAN TRỌNG: Output của bạn phải giống CHÍNH XÁC với example về:
- Độ dài (30-40 dòng)
- Phong cách viết (đoạn văn đầy đủ, không phải bullet points)
- Cấu trúc (4 phần như trong template)
- Ngôn ngữ (100% tiếng Việt)

Source documents cần sử dụng:
- "Current Trends and Issues in Internal Communication Theory and Practice (New Perspectives in Organizational Communication).pdf"
- "Internal Communications A Manual for Practitioners.pdf"

Yêu cầu:
1. CHỈ SỬ DỤNG rag-search để tìm kiếm (KHÔNG được dùng rag-index-gcs)
2. Sử dụng kỹ thuật query rewriting (3-5 variations per section)
3. Sử dụng file_names filter để search có mục tiêu
4. Fill vào template với nội dung ĐẦY ĐỦ, CHI TIẾT theo 4 phần
5. Bao gồm pedagogical objectives (=> Mục đích: ...)
6. Cite sources ở cuối: "Thông tin lấy từ Sách: [Document names]"

OUTPUT: Bài giảng HOÀN CHỈNH bằng tiếng Việt, bắt đầu bằng "Bài giảng: Lập kế hoạch, chiến lược Truyền thông nội bộ"
"""

    logger.info("\n" + "=" * 100)
    logger.info("STEP 1: USER PROMPT")
    logger.info("=" * 100)
    logger.info(f"Prompt length: {len(task_description)} characters")
    logger.info(f"Contains template: {'Yes' if 'TEMPLATE STRUCTURE' in task_description else 'No'}")
    logger.info(f"Contains example: {'Yes' if 'ONE-SHOT EXAMPLE' in task_description else 'No'}")
    logger.info(f"Vietnamese requirement: {'Yes' if 'tiếng Việt' in task_description else 'No'}")

    try:
        async with WorkflowSession(profile="rag_assistant") as session:
            logger.info("\n" + "=" * 100)
            logger.info("STEP 2: WORKFLOW SESSION INITIALIZED")
            logger.info("=" * 100)
            logger.info("Profile: rag_assistant")
            agent_type = session.engine.agent_type if hasattr(session.engine, "agent_type") else "unknown"
            logger.info("Agent type: %s", agent_type)

            # Check MCP tools available
            if hasattr(session.engine, "mcp_manager"):
                tools = session.engine.mcp_manager.get_all_tools()
                if isinstance(tools, dict):
                    logger.info(f"Available MCP tools: {list(tools.keys())}")
                elif isinstance(tools, list):
                    logger.info(
                        f"Available MCP tools: {[t.get('name', 'unknown') if isinstance(t, dict) else str(t) for t in tools]}"
                    )
                else:
                    logger.info(f"Available MCP tools: {tools}")

            logger.info("\n" + "=" * 100)
            logger.info("STEP 3: EXECUTING WORKFLOW")
            logger.info("=" * 100)

            # Execute
            response = await session.execute(task_description)

            logger.info("\n" + "=" * 100)
            logger.info("STEP 4: FINAL RESPONSE RECEIVED")
            logger.info("=" * 100)
            logger.info(f"Response length: {len(response)} characters")
            logger.info(
                f"Response language: {'Vietnamese' if any(char in response for char in 'ạảãàáâậầấẩẫăắằẳẵặđèéẹẻẽêềếểễệìíĩỉịòóõọỏôốồổỗộơớờởỡợùúũụủưứừửữựỳýỵỷỹ') else 'English/Other'}"
            )
            logger.info(f"Starts with 'Bài giảng:': {'Yes' if response.strip().startswith('Bài giảng:') else 'No'}")

            logger.info("\n" + "=" * 100)
            logger.info("FINAL RESPONSE:")
            logger.info("=" * 100)
            print(f"\n{response}\n")

            # Save response to file
            with open("debug_response.txt", "w", encoding="utf-8") as f:
                f.write(response)
            logger.info("Response saved to: debug_response.txt")

            # Analyze response
            logger.info("\n" + "=" * 100)
            logger.info("RESPONSE ANALYSIS:")
            logger.info("=" * 100)

            # Check for Vietnamese content
            vietnamese_chars = sum(
                1 for char in response if char in "ạảãàáâậầấẩẫăắằẳẵặđèéẹẻẽêềếểễệìíĩỉịòóõọỏôốồổỗộơớờởỡợùúũụủưứừửữựỳýỵỷỹ"
            )
            logger.info(f"Vietnamese characters count: {vietnamese_chars}")

            # Check structure
            has_section1 = "Định nghĩa" in response or "vai trò" in response
            has_section2 = "Khung lý thuyết" in response or "mô hình" in response
            has_section3 = "Phương pháp" in response or "ứng dụng" in response
            has_section4 = "Case study" in response or "case study" in response.lower()

            logger.info(f"Has Section 1 (Định nghĩa & vai trò): {has_section1}")
            logger.info(f"Has Section 2 (Khung lý thuyết): {has_section2}")
            logger.info(f"Has Section 3 (Phương pháp ứng dụng): {has_section3}")
            logger.info(f"Has Section 4 (Case study): {has_section4}")

            # Check pedagogical objectives
            has_pedagogical = "Mục đích:" in response
            logger.info(f"Has pedagogical objectives (=> Mục đích:): {has_pedagogical}")

            # Check citations
            has_citations = "Thông tin lấy từ" in response or "Sách:" in response
            logger.info(f"Has citations: {has_citations}")

            # Count lines
            lines = [line for line in response.split("\n") if line.strip()]
            logger.info(f"Number of non-empty lines: {len(lines)}")

    except Exception:
        logger.exception("Error during execution")
        raise

    logger.info("\n" + "=" * 100)
    logger.info("DEBUG TEST COMPLETED")
    logger.info("=" * 100)
    logger.info("Check debug_template_filling.log for detailed logs")
    logger.info("Check debug_response.txt for the final response")


async def main():
    """Run debug test."""
    await test_with_full_debug()


if __name__ == "__main__":
    asyncio.run(main())
