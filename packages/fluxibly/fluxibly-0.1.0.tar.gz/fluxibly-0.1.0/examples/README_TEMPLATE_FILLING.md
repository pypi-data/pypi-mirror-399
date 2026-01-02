# RAG Template-Filling Configuration

## Overview

This configuration sets up the RAG assistant to fill structured templates (like lecture outlines) using information retrieved from source documents via query rewriting and strategic search.

## Files Modified

### 1. RAG Assistant Profile
**File**: [config/profiles/rag_assistant.yaml](../config/profiles/rag_assistant.yaml)

**Purpose**: Specialized system prompt for template-filling with strategic search

**Key Features**:
- Task breakdown: Maps template sections to search objectives
- Query rewriting: Creates 3-5 variations per topic
- File-targeted searches: Uses `file_names` parameter strategically
- Iterative refinement: Adjusts `score_threshold` and `limit` based on results
- Academic structure preservation: Maintains 4-part hierarchy

**Workflow**:
1. Analyze template structure (outline.md) and identify gaps
2. Break down into specific search objectives per section
3. Perform multiple searches with query rewriting
4. Use file_names filter when source documents provided
5. Synthesize information to fill template
6. Cite sources with file names and scores

### 2. Test Script
**File**: [examples/test_rag_template_filling.py](test_rag_template_filling.py)

**Purpose**: Demonstrates template-filling with query rewriting

**Tests**:
- `test_simple_search()`: Basic query rewriting with file filtering
- `test_template_filling()`: Full template filling workflow

## Usage

### Basic Example

```python
from fluxibly import WorkflowSession

async with WorkflowSession(profile="rag_assistant") as session:
    task = """
    Tôi cần bạn tạo bài giảng theo template về chủ đề: "Lập kế hoạch Truyền thông"

    Template: outline.md
    Example: example_oneshot.md

    Source documents:
    - "Current Trends in Internal Communication.pdf"
    - "Internal Communications Manual.pdf"

    Yêu cầu:
    1. Tìm kiếm thông tin từ source documents
    2. Sử dụng query rewriting (3-5 variations)
    3. Sử dụng file_names filter
    4. Fill template theo 4 phần chuẩn
    5. Cite sources
    """

    response = await session.execute(task)
    print(response)
```

### Running Tests

```bash
# With venv Python
.venv/bin/python examples/test_rag_template_filling.py

# With uv (if available)
uv run python examples/test_rag_template_filling.py
```

## Search Parameters

The agent uses these parameters strategically:

```json
{
  "query": "string",           // Rewritten 3-5 times per section
  "limit": 10,                 // Increased to 20-30 for comprehensive coverage
  "score_threshold": 0.7,      // Adjusted 0.5-0.9 based on results
  "file_names": ["doc.pdf"]    // Filters specific documents
}
```

## Query Rewriting Strategy

For each template section, the agent creates multiple query variations:

**Example**: For "định nghĩa công chúng nội bộ"
1. Literal: "định nghĩa công chúng nội bộ"
2. Conceptual: "khái niệm internal publics"
3. English: "internal publics definition theory"
4. Contextual: "phân loại nhóm công chúng trong tổ chức"
5. Question-based: "what are internal publics in organizations"

## Template Structure

The agent follows this 4-part academic structure:

1. **Định nghĩa & vai trò** (Definitions & Roles)
   - Concept definitions from multiple sources
   - Importance and role in the field

2. **Khung lý thuyết/mô hình** (Theoretical Framework)
   - Research models and frameworks
   - Current research trends

3. **Phương pháp ứng dụng** (Application Methods)
   - Concrete implementation steps
   - Technical guidelines

4. **Case study** (Case Studies)
   - International and domestic examples
   - Analysis and practical exercises

## File-Targeted Search

When source documents are specified:

```python
# Search each document separately
file_names: ["Current Trends in Internal Communication.pdf"]

# Then search other documents
file_names: ["Internal Communications Manual.pdf"]

# Finally search all documents without filter
file_names: []
```

## Troubleshooting

### MCP Server Connection Issues

If you see `FileNotFoundError: [Errno 2] No such file or directory: 'python'`:

**Problem**: MCP server config uses `python` instead of venv python

**Solution**: Check [config/mcp_servers.yaml](../config/mcp_servers.yaml) and ensure:
```yaml
custom_rag:
  command: python3  # or full path to venv python
  args: ["-m", "mcp_servers.custom_rag.server"]
```

### No Tools Available

If the agent says "I don't have access to files":

1. Check MCP server is running
2. Verify `custom_rag` in enabled_servers
3. Check RAG API is accessible at configured URL

## Architecture

```
User Query
    ↓
WorkflowSession (profile=rag_assistant)
    ↓
OrchestratorAgent
    ↓
Task Breakdown → Search Planning
    ↓
Query Rewriting (3-5 variations)
    ↓
MCP rag-search (with file_names filter)
    ↓
Information Synthesis
    ↓
Template Filling
```

## Next Steps

1. **Fix MCP Server**: Update python path in mcp_servers.yaml
2. **Test with Real Documents**: Add PDFs to Qdrant vector store
3. **Refine Prompts**: Adjust query rewriting strategies based on results
4. **Add Templates**: Create more outline templates for different topics
5. **Optimize Scoring**: Fine-tune score_threshold values per document type
