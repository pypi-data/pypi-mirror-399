# Academic RAG Example - Quick Reference Guide

This guide demonstrates RAG workflows for academic course syllabi using the International Public Relations course as an example.

## Overview

The academic RAG example shows how to query structured educational documents like course syllabi to extract:
- Course information and objectives
- Learning outcomes (CLOs)
- Content structure and chapters
- Assessment methods and grading
- Course policies and requirements
- Teaching methods and activities

## Setup

### 0. Environment Variables

Ensure your OpenAI API key is set in `local.env`:

```bash
OPENAI_API_KEY=your-api-key-here
```

The examples automatically load this file.

### 1. Start Qdrant

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 2. Enable Qdrant MCP Server

Edit `config/mcp_servers.yaml` and set `enabled: true` for the qdrant server.

**Note:** The MCP server uses the `rag_documents` collection by default to avoid conflicts with any existing `documents` collection you may have.

```yaml
qdrant:
  command: "uvx"
  args: ["mcp-server-qdrant"]
  env:
    QDRANT_URL: "http://localhost:6333"
    COLLECTION_NAME: "rag_documents"  # Separate from your existing data
    EMBEDDING_MODEL: "sentence-transformers/all-MiniLM-L6-v2"
  enabled: true
  priority: 1
```

### 3. Install Dependencies

```bash
uv add qdrant-client sentence-transformers
```

### 4. Populate Knowledge Base

```bash
uv run python examples/setup_qdrant_academic.py
```

This creates 22 documents from the PR course syllabus covering:
- General course information (3 docs)
- Learning outcomes - CLOs (6 docs)
- Course content by chapter (8 docs)
- Assessment and policies (3 docs)
- Course materials and instructors (2 docs)

## Running Queries

```bash
uv run python examples/workflow_rag_academic.py
```

## Sample Queries by Category

### Course Information
```python
"What is the course code, credits, and semester?"
"Who are the instructors for this course?"
"What are the prerequisites?"
"What textbooks are required?"
```

### Learning Outcomes
```python
"What are all the course learning outcomes (CLOs)?"
"What knowledge will students gain? (CLO 1.x)"
"What skills will students develop? (CLO 2.x)"
"What competency levels are expected?"
```

### Course Content
```python
"List all chapters covered in the course"
"What topics are covered in Chapter 5?"
"How many classroom hours vs self-study hours per chapter?"
"Which chapters teach writing skills?"
```

### Assessment
```python
"How are students assessed in this course?"
"What is the grading breakdown by percentage?"
"When is the midterm exam and what does it cover?"
"What are the requirements for the final paper?"
```

### Teaching Methods
```python
"What teaching methods are used? (lecture, discussion, practice)"
"What group work is required?"
"Are there any guest speakers?"
"What practical exercises do students complete?"
```

### Course Policies
```python
"What is the attendance requirement?"
"What happens if a student misses 4 classes?"
"When are grades announced?"
"What are the assignment submission policies?"
```

## Advanced Query Examples

### Multi-hop Reasoning
```python
"""
Trace the complete learning path for PR writing skills:
1. Which chapters introduce writing concepts?
2. What skills build upon each other?
3. How are these skills assessed?
4. What CLOs do they map to?
5. What percentage of the grade do they represent?
"""
```

### Workload Analysis
```python
"""
Analyze student workload:
1. Total classroom hours vs self-study hours
2. Which chapters are most time-intensive?
3. When are major deliverables due?
4. How much group work is required?
5. Is the workload balanced across the semester?
"""
```

### Comparative Analysis
```python
"""
Compare different PR types taught in the course:
1. Internal PR vs Media Relations
2. Topics covered for each
3. Skills required
4. Assessment methods
5. Which chapters cover each type?
"""
```

### CLO Mapping
```python
"""
For CLO 2.2 (writing skills):
1. What is the specific learning outcome?
2. Which chapters develop this outcome?
3. What assignments assess it?
4. What teaching activities support it?
5. What percentage of the grade depends on it?
"""
```

## Document Structure

The academic documents are structured with metadata:

```python
{
    "id": 101,
    "text": "Course content...",
    "metadata": {
        "category": "course_content",  # or learning_outcomes, assessment, etc.
        "topic": "chapter5_media_relations",
        "hours_class": 6,
        "hours_self": 14
    }
}
```

### Categories
- `course_info` - General information, instructors, materials
- `learning_outcomes` - CLOs with competency levels
- `course_content` - Chapters, topics, teaching methods
- `assessment` - Grading breakdown, evaluation criteria
- `course_policies` - Requirements, attendance, deadlines
- `course_materials` - Textbooks, references

## Query Strategies

### 1. Direct Information Retrieval
Best for: Specific facts (course code, credits, instructor names)
```python
"What is the course code and how many credits is it?"
```

### 2. Structured Information Extraction
Best for: Lists, breakdowns, multiple related items
```python
"List all chapters with their time allocations"
```

### 3. Analytical Queries
Best for: Comparisons, trends, relationships
```python
"How does the time allocation vary across chapters?"
```

### 4. Synthesis Queries
Best for: Combining information from multiple sources
```python
"Create a complete assessment guide showing all evaluation components,
their weights, timing, and what CLOs they assess"
```

## Integration Ideas

### Academic Chatbot
```python
async with WorkflowSession(profile="rag_assistant") as session:
    # Student asks about deadlines
    response = await session.execute(
        "When are the major deadlines for this course?"
    )
    # Returns structured information about assignment due dates
```

### Course Comparison System
```python
# Compare multiple courses
for course in ["PR", "Marketing", "Advertising"]:
    response = await session.execute(
        f"What are the learning outcomes for {course}?"
    )
    # Build comparison matrix
```

### Academic Advising Assistant
```python
# Help students plan workload
response = await session.execute(
    "I'm taking 4 courses this semester. How demanding is this PR course
    in terms of time commitment and group work?"
)
```

### Curriculum Analysis
```python
# Analyze course design
response = await session.execute(
    "Analyze the pedagogical approach: what mix of teaching methods
    is used and how does assessment align with learning outcomes?"
)
```

## Customization

### Adding More Courses

1. Extract content from syllabus PDFs
2. Structure into semantic chunks
3. Add appropriate metadata
4. Generate embeddings and upload to Qdrant

```python
COURSE_DOCUMENTS = [
    {
        "id": 201,
        "text": "Marketing course content...",
        "metadata": {
            "course": "marketing",
            "category": "course_info",
            "topic": "general_information"
        }
    },
    # ... more documents
]
```

### Custom Queries

Modify `workflow_rag_academic.py` to add domain-specific queries:

```python
# Query about accreditation
response = await session.execute(
    "What program learning outcomes (PLOs) does this course contribute to?"
)

# Query about prerequisites chains
response = await session.execute(
    "What prior knowledge is assumed for this course?"
)
```

## Best Practices

1. **Chunk Size**: Keep documents focused (100-300 words)
2. **Metadata**: Rich metadata enables better filtering
3. **Semantic Diversity**: Vary phrasing in similar documents
4. **Citation**: Always request source attribution
5. **Verification**: Cross-reference answers with original documents

## Troubleshooting

### Poor Retrieval Quality
- Try broader query terms
- Check if topic is actually in the knowledge base
- Verify embedding model matches (all-MiniLM-L6-v2)

### Missing Information
- Documents may not cover all topics
- Try alternative phrasing
- Check metadata categories

### Slow Performance
- Reduce `max_mcp_calls` in profile
- Use more specific queries
- Pre-filter by metadata when possible

## Next Steps

1. **Expand Knowledge Base**: Add more courses, handbooks, policies
2. **Multi-Collection**: Separate collections per department/program
3. **Temporal Versioning**: Track syllabus changes over semesters
4. **Integration**: Connect to student information systems
5. **Multilingual**: Add Vietnamese-specific embedding models

## Resources

- [Main RAG Examples](RAG_EXAMPLES.md)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Course Syllabus Source](../docs/) - Original PDF document
- [Profile Configuration](../config/profiles/rag_assistant.yaml)
