"""Setup Qdrant with academic course syllabus content.

This script populates Qdrant with content from an International Public
Relations course syllabus for RAG queries.
"""

import asyncio
from typing import Any

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, PointStruct, VectorParams
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Error: Required packages not installed.")
    print("Install with: uv add qdrant-client sentence-transformers")
    exit(1)


# Academic document content from International Public Relations course
ACADEMIC_DOCUMENTS = [
    {
        "id": 101,
        "text": (
            "Course: Introduction to International Public Relations (Đại cương Quan hệ "
            "công chúng quốc tế). Course code: IC.043.03. Credits: 3. Type: Required "
            "(Bắt buộc). Semester: 2/Year 1. Prerequisites: None. Department: Faculty "
            "of International Communication and Foreign Cultural Affairs."
        ),
        "metadata": {"category": "course_info", "topic": "general_information", "language": "bilingual"},
    },
    {
        "id": 102,
        "text": (
            "Course objectives: Provide students with foundational knowledge about "
            "international public relations including: basic concepts, historical "
            "development, PR ethics, role in organizations, organizational models, "
            "PR processes, and skills in media relations, internal PR, and community "
            "relations. Develop skills in organizing press conferences, writing press "
            "releases and company profiles in English, bilingual communication, and "
            "PR campaign analysis."
        ),
        "metadata": {"category": "course_info", "topic": "learning_objectives", "language": "vietnamese"},
    },
    {
        "id": 103,
        "text": (
            "Learning Outcomes - Knowledge (CLO 1.1): Recognize basic PR terminology, "
            "fundamental PR activities, types of PR (internal PR, media relations, "
            "community relations, government relations, investor relations), and PR "
            "processes. Competency level: 2/6."
        ),
        "metadata": {"category": "learning_outcomes", "topic": "knowledge_clo1.1", "competency_level": "2/6"},
    },
    {
        "id": 104,
        "text": (
            "Learning Outcomes - Knowledge (CLO 1.2): Understand the role of PR for "
            "organizations and enterprises; organizational models and PR processes "
            "domestically and internationally; historical development of public relations. "
            "Competency level: 3/6."
        ),
        "metadata": {"category": "learning_outcomes", "topic": "knowledge_clo1.2", "competency_level": "3/6"},
    },
    {
        "id": 105,
        "text": (
            "Learning Outcomes - Knowledge (CLO 1.3): Classify concepts and characteristics "
            "of PR skills with media relations versus internal PR and community relations. "
            "Competency level: 4/6."
        ),
        "metadata": {"category": "learning_outcomes", "topic": "knowledge_clo1.3", "competency_level": "4/6"},
    },
    {
        "id": 106,
        "text": (
            "Learning Outcomes - Skills (CLO 2.1): Collect, analyze and evaluate information "
            "to organize a press conference. Competency level: 3/5."
        ),
        "metadata": {"category": "learning_outcomes", "topic": "skills_clo2.1", "competency_level": "3/5"},
    },
    {
        "id": 107,
        "text": (
            "Learning Outcomes - Skills (CLO 2.2): Proficiently use writing and research "
            "skills to complete company profiles and write press releases. Competency "
            "level: 3/5."
        ),
        "metadata": {"category": "learning_outcomes", "topic": "skills_clo2.2", "competency_level": "3/5"},
    },
    {
        "id": 108,
        "text": (
            "Learning Outcomes - Autonomy and Responsibility (CLO 3.1): Develop independent "
            "research spirit, creativity, critical thinking, teamwork skills, and "
            "presentation skills in public relations. Competency level: 4/5."
        ),
        "metadata": {"category": "learning_outcomes", "topic": "autonomy_clo3.1", "competency_level": "4/5"},
    },
    {
        "id": 109,
        "text": (
            "Learning Outcomes - Autonomy and Responsibility (CLO 3.2): Form good ethical "
            "qualities and professional work consciousness in communication and public "
            "relations. Competency level: 5/5."
        ),
        "metadata": {"category": "learning_outcomes", "topic": "autonomy_clo3.2", "competency_level": "5/5"},
    },
    {
        "id": 110,
        "text": (
            "Chapter 1: Overview of International Public Relations. Topics: PR concepts, "
            "basic stakeholder groups, distinguishing PR from other fields (marketing, "
            "advertising), ethics and professionalism in international PR. Time allocation: "
            "6 classroom hours, 14 self-study hours. Teaching methods: Lecture on PR "
            "concepts and stakeholder groups, discussion on differences between PR, "
            "marketing, and advertising, practical exercises analyzing PR, marketing, "
            "and advertising activities. Contributes to CLO 1.1."
        ),
        "metadata": {"category": "course_content", "topic": "chapter1_overview", "hours_class": 6, "hours_self": 14},
    },
    {
        "id": 111,
        "text": (
            "Chapter 2: History of PR Formation and Development Worldwide. Topics: Origins "
            "of PR, formation of basic PR functions in history, notable figures in PR "
            "history, PR formation and development in various countries, recent PR "
            "development, PR in Vietnam. Time: 6 classroom hours, 14 self-study hours. "
            "Activities: Lecture on global PR formation and development, discussion on "
            "post-2000 PR characteristics, presentation of PR models by historical period. "
            "Contributes to CLO 1.2 and CLO 3.2."
        ),
        "metadata": {"category": "course_content", "topic": "chapter2_history", "hours_class": 6, "hours_self": 14},
    },
    {
        "id": 112,
        "text": (
            "Chapter 3: PR Organizational Models and Activities Domestically and "
            "Internationally. Topics: In-house PR department models domestically and "
            "globally, PR agencies/firms domestically and internationally. Time: 6 "
            "classroom hours, 14 self-study hours. Activities: Lecture on organizational "
            "models and PR operations globally, discussion on differences between "
            "corporate PR and agency PR. Contributes to CLO 1.1 and CLO 1.2."
        ),
        "metadata": {"category": "course_content", "topic": "chapter3_models", "hours_class": 6, "hours_self": 14},
    },
    {
        "id": 113,
        "text": (
            "Chapter 4: PR Process in Organizations Domestically and Internationally. "
            "Topics: General concepts, basic steps in PR process, analysis of PR "
            "activities in Vietnamese and international enterprises. Time: 3 classroom "
            "hours, 7 self-study hours. Activities: Lecture on PR process in organizations, "
            "discussion on differences between corporate and government PR, analysis "
            "of corporate and government PR activities. Contributes to CLO 1.1 and CLO 1.2."
        ),
        "metadata": {"category": "course_content", "topic": "chapter4_process", "hours_class": 3, "hours_self": 7},
    },
    {
        "id": 114,
        "text": (
            "Chapter 5: Media Relations Domestically and Internationally. Topics: Concept "
            "and role of international communication in PR, main techniques for building "
            "media relations, bilingual press release writing skills. Subtopics include: "
            "press release concepts, studying press releases from various countries, "
            "bilingual press release writing techniques, organizing press conferences. "
            "Time: 6 classroom hours (sessions 8+9), 14 self-study hours. Contributes "
            "to CLO 1.1, 1.2, 1.3, 3.1, and 3.2."
        ),
        "metadata": {
            "category": "course_content",
            "topic": "chapter5_media_relations",
            "hours_class": 6,
            "hours_self": 14,
        },
    },
    {
        "id": 115,
        "text": (
            "Chapter 6: Internal Public Relations. Topics: Definition of internal publics "
            "and internal PR, role of internal PR in organizational PR activities, main "
            "internal PR activities, internal communication, building organizational "
            "culture. Time: 6 classroom hours (sessions 10+11), 14 self-study hours. "
            "Activities include lecture on internal PR, discussion questions, and "
            "group homework. Contributes to CLO 1.1 and CLO 1.3."
        ),
        "metadata": {"category": "course_content", "topic": "chapter6_internal_pr", "hours_class": 6, "hours_self": 14},
    },
    {
        "id": 116,
        "text": (
            "Chapter 6.2: Building and Writing Company Profiles (Bilingual). Topics: "
            "Profile concept, distinguishing profiles from advertising materials "
            "(brochures and catalogues), methods for building and writing organizational "
            "profiles. Time: 3 classroom hours (session 12), 7 self-study hours. "
            "Activities: Lecture on building and writing profiles, discussion questions, "
            "analysis of company profiles and corporate culture. Contributes to CLO 2.2."
        ),
        "metadata": {
            "category": "course_content",
            "topic": "chapter6_profile_writing",
            "hours_class": 3,
            "hours_self": 7,
        },
    },
    {
        "id": 117,
        "text": (
            "Session 13: Risk Prediction and Crisis Management Skills. Guest speaker "
            "invited. Time: 3 classroom hours, 7 self-study hours. Activities: Lecture "
            "and discussion questions. Contributes to CLO 3.2."
        ),
        "metadata": {"category": "course_content", "topic": "crisis_management", "hours_class": 3, "hours_self": 7},
    },
    {
        "id": 118,
        "text": (
            "Chapter 8: Community Relations. Topics: Community and role of community PR, "
            "main community PR activities, successful Vietnamese community PR cases. "
            "Time: 3 classroom hours (session 14), 7 self-study hours. Activities: "
            "Lecture on community relations, discussion on CSR roles, analysis of "
            "Vinamilk's CSR activities. Contributes to CLO 1.3."
        ),
        "metadata": {
            "category": "course_content",
            "topic": "chapter8_community_relations",
            "hours_class": 3,
            "hours_self": 7,
        },
    },
    {
        "id": 119,
        "text": (
            "Assessment breakdown: Assignments (Bài tập) 10% - evaluates completion "
            "of individual and group assignments, understanding of readings, group "
            "member role distribution, presentation quality. Attendance and participation "
            "(Chuyên cần) 15% - evaluates preparation, attendance, and quality of "
            "class participation. Midterm presentation (Thuyết trình) 15% - covers "
            "Chapter 6, evaluates individual/group completion, content understanding, "
            "presentation, and role distribution. Final paper (Viết) 60% - covers "
            "Chapter 7, comprehensive assessment of all CLOs."
        ),
        "metadata": {"category": "assessment", "topic": "grading_breakdown", "assessment_components": 4},
    },
    {
        "id": 120,
        "text": (
            "Student requirements: Minimum 80% attendance for theory sessions, punctual "
            "arrival/departure. Complete assigned individual and group homework weekly. "
            "Group presentations: 4-5 students per group, all members must present "
            "and answer questions. Absences: 4 absences = cannot take final exam; "
            "absence during midterm without valid reason = score 0. Assignments must "
            "be submitted on time with proper content and format. Results announced "
            "at course end; final exam submitted 2 weeks after class ends; final "
            "grades announced 2 weeks after submission."
        ),
        "metadata": {"category": "course_policies", "topic": "student_requirements", "attendance_minimum": "80%"},
    },
    {
        "id": 121,
        "text": (
            "Required textbook: PR Lý luận và ứng dụng (PR Theory and Application) by "
            "Dr. Đinh Thị Thuý Hằng (2014), published by Lao Động, Xã hội. Reference "
            "book: Effective Public Relations (10th edition, 2008) by Glen M. Broom, "
            "published by Pearson Education International."
        ),
        "metadata": {"category": "course_materials", "topic": "textbooks", "required_count": 1, "reference_count": 1},
    },
    {
        "id": 122,
        "text": (
            "Teaching language: English/Vietnamese (Tiếng Anh/Tiếng Việt). Instructors: "
            "ThS. Trần Thu Thuỷ (course coordinator), TS. Nguyễn Thị Hồng Nam, "
            "TS. Đỗ Huyền Trang, ThS. Nguyễn Huyền Trang - all from Học viện Ngoại giao "
            "(Diplomatic Academy of Vietnam)."
        ),
        "metadata": {"category": "course_info", "topic": "instructors", "language": "bilingual"},
    },
]


async def setup_academic_collection() -> None:
    """Create Qdrant collection and populate with academic documents."""
    print("=" * 70)
    print("Setting up Qdrant with Academic Course Syllabus")
    print("=" * 70)

    # Initialize Qdrant client
    print("\n[Step 1] Connecting to Qdrant...")
    client = QdrantClient(host="localhost", port=6333)
    print("✓ Connected to Qdrant at localhost:6333")

    # Initialize embedding model
    print("\n[Step 2] Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embedding_dim = model.get_sentence_embedding_dimension()
    print(f"✓ Loaded all-MiniLM-L6-v2 (dimension: {embedding_dim})")

    # Create or recreate collection
    # Using 'rag_documents' to avoid conflicts with existing 'documents' collection
    collection_name = "rag_documents"
    print(f"\n[Step 3] Setting up collection '{collection_name}'...")

    try:
        client.delete_collection(collection_name=collection_name)
        print(f"  Deleted existing collection '{collection_name}'")
    except Exception:
        pass

    # Use named vector to match MCP server expectations
    # MCP server expects vector name: "fast-all-minilm-l6-v2"
    vector_name = "fast-all-minilm-l6-v2"
    client.create_collection(
        collection_name=collection_name,
        vectors_config={vector_name: VectorParams(size=embedding_dim, distance=Distance.COSINE)},
    )
    print(f"✓ Created collection '{collection_name}' with vector '{vector_name}'")

    # Generate embeddings and prepare points
    print("\n[Step 4] Generating embeddings for academic documents...")
    points: list[PointStruct] = []

    for doc in ACADEMIC_DOCUMENTS:
        # Generate embedding
        embedding = model.encode(doc["text"]).tolist()

        # Create point with named vector
        point = PointStruct(
            id=doc["id"],
            vector={vector_name: embedding},
            payload={"text": doc["text"], **doc["metadata"]},
        )
        points.append(point)

        category = doc["metadata"].get("category", "unknown")
        topic = doc["metadata"].get("topic", "unknown")
        print(f"  ✓ Document {doc['id']}: {category}/{topic}")

    # Upload points to Qdrant
    print(f"\n[Step 5] Uploading {len(points)} documents to Qdrant...")
    client.upsert(collection_name=collection_name, points=points)
    print("✓ Documents uploaded successfully")

    # Verify collection
    print("\n[Step 6] Verifying collection...")
    collection_info = client.get_collection(collection_name=collection_name)
    print(f"✓ Collection contains {collection_info.points_count} documents")

    # Test semantic search with academic query
    print("\n[Step 7] Testing semantic search with academic query...")
    query = "What are the learning outcomes for PR writing skills?"
    query_embedding = model.encode(query).tolist()

    search_results = client.search(
        collection_name=collection_name,
        query_vector=(vector_name, query_embedding),
        limit=3,
    )

    print(f"\nQuery: '{query}'")
    print("Top 3 results:")
    for i, result in enumerate(search_results, 1):
        payload: dict[str, Any] = result.payload or {}
        text: str = payload.get("text", "")
        category: str = payload.get("category", "unknown")
        topic: str = payload.get("topic", "unknown")
        score: float = result.score
        print(f"\n{i}. [Score: {score:.3f}] {category}/{topic}")
        print(f"   {text[:150]}...")

    print("\n" + "=" * 70)
    print("Setup Complete! Academic syllabus ready for RAG queries.")
    print("=" * 70)
    print("\nDocument categories loaded:")
    categories = set(doc["metadata"]["category"] for doc in ACADEMIC_DOCUMENTS)
    for cat in sorted(categories):
        count = sum(1 for doc in ACADEMIC_DOCUMENTS if doc["metadata"]["category"] == cat)
        print(f"  - {cat}: {count} documents")

    print("\nNext steps:")
    print("1. Run: uv run python examples/workflow_rag_academic.py")
    print("2. Try custom queries about the PR course")
    print("3. Analyze course structure, learning outcomes, and assessments")


if __name__ == "__main__":
    asyncio.run(setup_academic_collection())
