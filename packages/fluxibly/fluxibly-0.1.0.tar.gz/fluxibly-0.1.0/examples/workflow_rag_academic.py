"""Academic document RAG example using course syllabus.

This example demonstrates RAG queries against an academic course syllabus
document (International Public Relations) stored in Qdrant.
"""

import asyncio

from dotenv import load_dotenv

from fluxibly import WorkflowSession

# Load environment variables from local.env
load_dotenv("local.env")


async def main() -> None:
    """Run RAG queries against academic course syllabus."""
    print("=" * 70)
    print("Academic RAG Example - Course Syllabus Analysis")
    print("=" * 70)

    async with WorkflowSession(profile="rag_assistant") as session:
        # Query 1: Course overview and objectives
        print("\n[Query 1] Course overview and learning objectives")
        response1 = await session.execute(
            """
            Search the knowledge base for information about the International
            Public Relations course (IC.043.03).

            Please provide:
            1. Course name and code
            2. Number of credits
            3. Main learning objectives (kiến thức, kỹ năng, mức độ tự chủ)
            4. Target semester
            5. Prerequisites

            Cite the source document.
            """
        )
        print(f"Response: {response1}\n")

        # Query 2: Course structure and chapters
        print("[Query 2] Course content structure")
        response2 = await session.execute(
            """
            Find information about the course structure and main chapters
            (Chương) covered in the International Public Relations course.

            List all chapters with their main topics and provide:
            - Chapter number and title
            - Key topics covered in each chapter
            - Time allocation (classroom hours and self-study hours)
            """
        )
        print(f"Response: {response2}\n")

        # Query 3: Assessment methods
        print("[Query 3] Assessment and grading breakdown")
        response3 = await session.execute(
            """
            Retrieve information about how students are assessed in this course.

            Please explain:
            1. Assessment methods (hình thức đánh giá)
            2. Weight/percentage for each component (tỷ lệ %)
            3. Timing of assessments (giữa kỳ, cuối kỳ)
            4. What each assessment evaluates (CLO mapping)
            """
        )
        print(f"Response: {response3}\n")

        # Query 4: Learning outcomes (CLO)
        print("[Query 4] Course learning outcomes")
        response4 = await session.execute(
            """
            Search for course learning outcomes (Chuẩn đầu ra - CLO).

            Organize by category:
            1. Knowledge outcomes (Kiến thức - CLO 1.x)
            2. Skills outcomes (Kỹ năng - CLO 2.x)
            3. Autonomy and responsibility (Mức tự chủ và trách nhiệm - CLO 3.x)

            For each CLO, provide the competency level (Trình độ năng lực).
            """
        )
        print(f"Response: {response4}\n")

        # Query 5: Teaching methods and activities
        print("[Query 5] Teaching methods and learning activities")
        response5 = await session.execute(
            """
            Find information about teaching methods used in this course.

            Identify:
            1. Lecture activities (L - Thuyết giảng)
            2. Discussion activities (D - Thảo luận)
            3. Practice activities (P - Thực hành)
            4. Group assignments (Bài tập nhóm)

            Provide examples from specific chapters.
            """
        )
        print(f"Response: {response5}\n")

        # Query 6: Specific skill - Press release writing
        print("[Query 6] Specific skill: Writing press releases")
        response6 = await session.execute(
            """
            Search for information about press release writing skills
            (Kỹ năng viết thông cáo báo chí) taught in this course.

            Find:
            1. Which chapter covers this topic?
            2. What are the learning objectives for this skill?
            3. What language(s) are students expected to write in?
            4. What related skills are taught (e.g., press conferences)?
            """
        )
        print(f"Response: {response6}\n")

        # Query 7: Course policies and requirements
        print("[Query 7] Course policies and student requirements")
        response7 = await session.execute(
            """
            Retrieve course policies and requirements for students
            (Chính sách đối với học phần và các yêu cầu đối với sinh viên).

            Summarize:
            1. Attendance requirements
            2. Assignment submission policies
            3. Group work expectations
            4. Consequences for absences
            5. Grade publication timeline
            """
        )
        print(f"Response: {response7}\n")

        # Query 8: Compare PR with related fields
        print("[Query 8] Distinguishing PR from related fields")
        response8 = await session.execute(
            """
            Find information about how Public Relations is distinguished from
            other related fields in this course.

            Look for:
            1. Differences between PR and Marketing
            2. Differences between PR and Advertising (Quảng cáo)
            3. Which chapter discusses these distinctions?
            4. What learning activities help students understand differences?
            """
        )
        print(f"Response: {response8}\n")

    print("=" * 70)
    print("Academic RAG workflow complete!")


async def advanced_academic_queries() -> None:
    """Demonstrate advanced queries combining multiple aspects."""
    print("\n" + "=" * 70)
    print("Advanced Academic Queries - Cross-reference Analysis")
    print("=" * 70)

    async with WorkflowSession(profile="rag_assistant") as session:
        # Complex query: Complete skill development path
        print("\n[Complex Query] Complete learning path for PR writing skills")
        response = await session.execute(
            """
            Analyze the complete learning path for PR writing skills throughout
            the course:

            1. Identify all chapters that teach writing skills
            2. Map the progression: what's taught first, what builds on it
            3. List specific deliverables (press releases, profiles, etc.)
            4. Show how these skills are assessed (which CLOs, assessment %)
            5. Identify prerequisite knowledge needed for each skill

            Create a structured learning roadmap showing the skill progression
            from basic concepts to final assessments.
            """
        )
        print(f"Response: {response}\n")

        # Analysis query: Workload distribution
        print("[Analysis Query] Student workload analysis")
        response2 = await session.execute(
            """
            Analyze the student workload distribution across the semester:

            1. Total classroom hours vs. self-study hours
            2. Distribution across chapters (which chapters are most intensive?)
            3. Assessment timing (when are major deliverables due?)
            4. Group work requirements (how many group assignments?)
            5. Calculate total workload and compare to the 3-credit allocation

            Provide insights on the workload balance and peak periods.
            """
        )
        print(f"Response: {response2}\n")

    print("=" * 70)


if __name__ == "__main__":
    # Run basic academic queries
    asyncio.run(main())

    # Run advanced analysis
    asyncio.run(advanced_academic_queries())
