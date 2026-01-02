"""Simple debug test for Vietnamese output."""

import asyncio
import logging
from pathlib import Path

from dotenv import load_dotenv

from fluxibly import WorkflowSession

load_dotenv("local.env")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """Test with full debug logging."""

    # Load files
    template_path = Path("outline.md")
    example_path = Path("example_oneshot.md")

    with open(template_path, encoding="utf-8") as f:
        template = f.read()

    with open(example_path, encoding="utf-8") as f:
        example = f.read()

    # Task with embedded template and example
    task = f"""
BẮT BUỘC: Viết toàn bộ bằng tiếng Việt. KHÔNG dùng tiếng Anh.

Tạo bài giảng về: "Lập kế hoạch, chiến lược Truyền thông nội bộ"

TEMPLATE:
{template}

MẪU (THEO CHÍNH XÁC):
{example}

YÊU CẦU:
- Output 100% tiếng Việt
- 30-40 dòng như mẫu
- 4 phần như template
- Bắt đầu: "Bài giảng: ..."

Source documents:
- "Current Trends and Issues in Internal Communication Theory and Practice.pdf"
- "Internal Communications A Manual for Practitioners.pdf"

CHỈ dùng rag-search. KHÔNG dùng rag-index-gcs.
"""

    logger.info("=" * 80)
    logger.info("Starting debug test")
    logger.info("=" * 80)

    async with WorkflowSession(profile="rag_assistant") as session:
        response = await session.execute(task)

        logger.info("=" * 80)
        logger.info("RESPONSE:")
        logger.info("=" * 80)
        print(response)

        # Analysis
        is_vietnamese = any(c in response for c in "ạảãàáâậầấẩẫăắằẳẵặđèéẹẻẽêềếểễệ")
        starts_correct = response.strip().startswith("Bài giảng:")

        logger.info("=" * 80)
        logger.info("ANALYSIS:")
        logger.info("Vietnamese detected: %s", is_vietnamese)
        logger.info("Starts with 'Bài giảng:': %s", starts_correct)
        logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
