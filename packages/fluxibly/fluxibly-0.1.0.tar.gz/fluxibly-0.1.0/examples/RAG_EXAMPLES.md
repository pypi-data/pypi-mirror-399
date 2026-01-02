# RAG (Retrieval-Augmented Generation) Examples

This directory contains examples demonstrating RAG workflows using Qdrant MCP for semantic search and knowledge retrieval.

## Overview

RAG combines retrieval from a vector database with LLM generation to provide accurate, grounded responses based on your knowledge base. These examples show how to use Fluxibly with Qdrant for various RAG patterns.

## Prerequisites

### 0. Environment Variables

Ensure you have your OpenAI API key set in `local.env`:

```bash
# Create local.env file in project root
echo "OPENAI_API_KEY=your-api-key-here" > local.env
```

All RAG examples automatically load this file using `python-dotenv`.

### 1. Qdrant Setup

Ensure Qdrant is running locally:

```bash
# Using Docker
docker run -p 6333:6333 qdrant/qdrant

# Or install locally
# See: https://qdrant.tech/documentation/quick-start/
```

### 2. Collection Setup

Your Qdrant instance should have:
- **URL**: `http://localhost:6333`
- **Collection**: `documents`
- **Embedding Model**: `all-MiniLM-L6-v2`

#### Quick Setup with Sample Data

Use the provided setup script to populate Qdrant with sample documents:

```bash
# Install required dependencies
uv add qdrant-client sentence-transformers

# Run setup script
uv run python examples/setup_qdrant_sample.py
```

This will:
- Create a `documents` collection in Qdrant
- Populate it with 12 sample documents about ML/AI topics
- Test semantic search to verify the setup
- Display setup confirmation and next steps

#### Manual Setup

If you have your own documents, you can use the Qdrant client to populate the collection:

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# Connect to Qdrant
client = QdrantClient(host="localhost", port=6333)

# Create collection
client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# Generate embeddings and upload
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# ... add your documents
```

### 3. MCP Server Configuration

The Qdrant MCP server is defined in [`config/mcp_servers.yaml`](../config/mcp_servers.yaml).

**Enable the Qdrant server:**

Edit `config/mcp_servers.yaml` and change the `qdrant` server configuration from `enabled: false` to `enabled: true`:

```yaml
mcp_servers:
  qdrant:
    command: "uvx"
    args: ["mcp-server-qdrant"]
    env:
      QDRANT_URL: "http://localhost:6333"
      COLLECTION_NAME: "documents"
      EMBEDDING_MODEL: "sentence-transformers/all-MiniLM-L6-v2"
    enabled: true  # Change from false to true
    priority: 1
    description: "Qdrant vector database for semantic search and retrieval"
```

**Important Notes:**
- Qdrant MCP server is a **Python package**, run with `uvx` (not `npx`)
- Environment variables: `COLLECTION_NAME` and `EMBEDDING_MODEL` (note the naming)
- The `uvx` command is part of the `uv` tool you're already using
- See the [MCP servers registry](https://mcpservers.org/servers/qdrant/mcp-server-qdrant) for details

The `rag_assistant` profile automatically uses this server through its `enabled_servers: [qdrant]` configuration.

## Examples

### 1. Basic RAG (`workflow_rag_basic.py`)

Simple question-answering with semantic retrieval.

**Features**:
- Direct factual queries
- Specific information lookup
- Comparative analysis

**Run**:
```bash
uv run python examples/workflow_rag_basic.py
```

**Example queries**:
- "What are the key concepts in machine learning?"
- "Find information about neural network architectures"
- "Compare supervised and unsupervised learning"

### 2. Conversational RAG (`workflow_rag_conversational.py`)

Multi-turn conversations with context awareness.

**Features**:
- Maintains conversation history
- Context-aware follow-up queries
- Progressive information drilling
- Session management

**Run**:
```bash
uv run python examples/workflow_rag_conversational.py
```

**Example flow**:
1. Initial broad query about deep learning
2. Follow-up asking for specific training details
3. Drill down into applications
4. Related questions about challenges

### 3. Advanced RAG (`workflow_rag_advanced.py`)

Complex reasoning patterns with multi-hop retrieval.

**Features**:
- Multi-hop reasoning across documents
- Cross-document synthesis
- Source attribution and verification
- Knowledge gap analysis
- Temporal/trend analysis
- Confidence scoring

**Run**:
```bash
uv run python examples/workflow_rag_advanced.py
```

**Advanced patterns**:
- Multi-query retrieval for comprehensive answers
- Comparative analysis across multiple perspectives
- Gap identification in knowledge base
- Evolution of concepts over time

### 4. Hybrid RAG (`workflow_rag_hybrid.py`)

Combining RAG with other tools and advanced orchestration patterns.

**Features**:
- Multi-source information synthesis
- Documentation generation from retrieval
- Code example generation with patterns
- Learning path creation
- Iterative query refinement
- Quality verification loops

**Run**:
```bash
uv run python examples/workflow_rag_hybrid.py
```

**Use cases**:
- Research → documentation generation
- Cross-referencing multiple knowledge sources
- Code pattern extraction and example generation
- Personalized learning path creation
- Comprehensive guide synthesis

### 5. Academic RAG (`workflow_rag_academic.py`)

Domain-specific RAG for academic course syllabi and educational content.

**Features**:
- Course information extraction
- Learning outcome analysis
- Assessment breakdown queries
- Content structure navigation
- Policy and requirement retrieval
- Workload analysis
- Cross-reference learning paths

**Run**:
```bash
# Setup academic documents
uv run python examples/setup_qdrant_academic.py

# Query course syllabus
uv run python examples/workflow_rag_academic.py
```

**Sample queries**:
- "What are the course learning objectives?"
- "How are students assessed and what are the grading percentages?"
- "Which chapters cover PR writing skills?"
- "What is the workload distribution across the semester?"
- "Compare internal PR with media relations topics"

**Use cases**:
- Course information systems
- Academic advising chatbots
- Curriculum analysis
- Student support systems
- Educational content retrieval

## Profile Configuration

The RAG workflow uses the [`rag_assistant`](../config/profiles/rag_assistant.yaml) profile:

```yaml
profile:
  name: "rag_assistant"
  description: "Retrieval-Augmented Generation with Qdrant vector search"

workflow:
  agent_type: "orchestrator"
  execution_mode: "single"
  stateful: true

enabled_servers:
  - qdrant

orchestrator:
  model: "gpt-4-turbo"
  temperature: 0.7
  max_mcp_calls: 15
  mcp_timeout: 30
```

## RAG Workflow Patterns

### 1. Simple Retrieval-Answer
```
User Query → Semantic Search → Retrieved Docs → LLM Generation → Response
```

### 2. Multi-Hop Reasoning
```
Query → Multiple Retrievals → Cross-doc Synthesis → Verification → Response
```

### 3. Conversational Context
```
Query + History → Contextual Retrieval → Update Context → Response
```

### 4. Iterative Refinement
```
Query → Initial Retrieval → Identify Gaps → Additional Retrieval → Synthesis
```

## Best Practices

### Query Formulation
- Be specific about information needs
- Ask for source attribution when accuracy is critical
- Break complex questions into sub-queries
- Use follow-ups to drill down into details

### Retrieval Strategy
- Start with broad queries, then narrow down
- Request multiple perspectives for complex topics
- Ask for confidence levels on uncertain topics
- Verify cross-document consistency

### System Prompts
The orchestrator is configured to:
- Always retrieve context before answering
- Cite sources explicitly
- Distinguish facts from reasoning
- Acknowledge limitations when context is insufficient
- Use multiple retrieval rounds for complex queries

## Customization

### Adjust Retrieval Parameters

Modify the profile in `config/profiles/rag_assistant.yaml`:

```yaml
orchestrator:
  max_mcp_calls: 20  # Increase for more retrieval rounds
  temperature: 0.5   # Lower for more deterministic responses
  max_tokens: 8192   # Larger for long documents
```

### Custom System Prompts

Tailor the retrieval and synthesis behavior:

```yaml
orchestrator:
  system_prompt: |
    You are a domain-specific RAG assistant...
    [Custom instructions for your use case]
```

### Multiple Collections

To use different Qdrant collections, create separate MCP configs:

```yaml
# config/qdrant_technical_docs.yaml
mcp_servers:
  qdrant:
    env:
      COLLECTION_NAME: "technical_docs"
```

## Common Use Cases

### Technical Documentation
```python
response = await session.execute(
    "Search the API documentation for authentication methods. "
    "Provide code examples and best practices."
)
```

### Research Analysis
```python
response = await session.execute(
    "Retrieve papers about transformer architectures. "
    "Summarize key innovations and compare approaches."
)
```

### Customer Support
```python
response = await session.execute(
    "Find troubleshooting guides for error code E401. "
    "Include step-by-step resolution steps."
)
```

### Knowledge Base Q&A
```python
response = await session.execute(
    "What are our company's policies on remote work? "
    "Cite specific policy documents."
)
```

## Troubleshooting

### Qdrant Connection Issues
```bash
# Verify Qdrant is running
curl http://localhost:6333/collections

# Check collection exists
curl http://localhost:6333/collections/documents
```

### MCP Server Issues
```bash
# Test MCP server manually
npx -y @modelcontextprotocol/server-qdrant
```

### No Results Retrieved
- Verify collection has data
- Check embedding model matches indexing model
- Try broader query terms
- Increase `max_mcp_calls` for more retrieval attempts

### Poor Result Quality
- Adjust `temperature` (lower = more deterministic)
- Refine system prompt for domain-specific behavior
- Use more specific queries
- Request source attribution to verify accuracy

## Next Steps

1. **Populate Your Knowledge Base**: Add documents to your Qdrant collection
2. **Customize Profile**: Adjust `rag_assistant.yaml` for your domain
3. **Experiment with Queries**: Try different retrieval patterns
4. **Build Applications**: Integrate RAG workflows into your apps

## Resources

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Fluxibly Documentation](../README.md)
- [Vector Search Best Practices](https://qdrant.tech/documentation/guides/search/)

## Support

For issues or questions:
- Check existing examples in this directory
- Review profile configuration
- Consult Qdrant and MCP documentation
- Open an issue with example code and error messages
