"""Hybrid RAG workflow combining multiple MCP servers.

This example demonstrates advanced integration patterns where RAG retrieval
is combined with other tools like filesystem access, code execution, or
external APIs for comprehensive task completion.
"""

import asyncio

from dotenv import load_dotenv

from fluxibly import WorkflowSession

# Load environment variables from local.env
load_dotenv("local.env")


async def main() -> None:
    """Run hybrid RAG workflow combining multiple tools."""
    print("=" * 70)
    print("Hybrid RAG - Combining Vector Search with Other Tools")
    print("=" * 70)

    # Example: Combining Qdrant with filesystem for code documentation
    async with WorkflowSession(profile="rag_assistant") as session:
        # Scenario 1: Research + Documentation Generation
        print("\n[Scenario 1] Research and synthesize documentation")
        response1 = await session.execute(
            """
            Task: Create a comprehensive guide on implementing REST APIs.

            Steps:
            1. Search the knowledge base for REST API best practices
            2. Retrieve examples and design patterns
            3. Find information on common pitfalls and security considerations
            4. Synthesize all information into a structured guide with:
               - Overview and key concepts
               - Step-by-step implementation guide
               - Best practices and common patterns
               - Security considerations
               - Testing strategies
               - Sources cited for each section
            """
        )
        print(f"Response: {response1}\n")

        # Scenario 2: Multi-source information gathering
        print("[Scenario 2] Cross-reference multiple sources")
        response2 = await session.execute(
            """
            Question: What are the differences between microservices and monolithic
            architectures, and when should each be used?

            Approach:
            1. Retrieve documents about microservices architecture
            2. Retrieve documents about monolithic architecture
            3. Cross-reference best practices from multiple sources
            4. Identify use cases where each excels
            5. Provide decision framework with trade-offs
            6. Include real-world examples if available
            7. Cite all sources used
            """
        )
        print(f"Response: {response2}\n")

        # Scenario 3: Contextual code example generation
        print("[Scenario 3] Generate examples from retrieved patterns")
        response3 = await session.execute(
            """
            Task: Create Python code examples for authentication implementation.

            Process:
            1. Search for authentication patterns in the knowledge base
            2. Retrieve OAuth2, JWT, and session-based auth information
            3. Extract code patterns and best practices
            4. Generate clean, working code examples for each approach
            5. Include comments explaining security considerations
            6. Add usage examples and testing strategies
            7. Reference source documents for each pattern
            """
        )
        print(f"Response: {response3}\n")

        # Scenario 4: Learning path generation
        print("[Scenario 4] Create personalized learning path")
        response4 = await session.execute(
            """
            Goal: Design a learning path for becoming proficient in machine learning.

            Requirements:
            1. Search knowledge base for ML fundamentals, tools, and techniques
            2. Retrieve information on learning progression and prerequisites
            3. Identify key topics and their dependencies
            4. Structure a logical learning sequence from beginner to advanced
            5. Recommend resources for each stage (from retrieved docs)
            6. Include practical projects and milestones
            7. Estimate time commitments based on retrieved information
            8. Cite sources for each recommendation
            """
        )
        print(f"Response: {response4}\n")

    print("=" * 70)
    print("Hybrid RAG workflows complete!")


async def advanced_rag_patterns() -> None:
    """Demonstrate advanced RAG patterns with error handling and iterations."""
    print("\n" + "=" * 70)
    print("Advanced Pattern: Iterative Refinement with Verification")
    print("=" * 70)

    async with WorkflowSession(profile="rag_assistant") as session:
        # Pattern: Iterative query refinement
        print("\n[Pattern] Iterative refinement based on result quality")
        response = await session.execute(
            """
            Complex query: Explain how distributed systems achieve consistency.

            Iterative approach:
            1. Initial retrieval: Search for "distributed systems consistency"
            2. Evaluate results: Check if CAP theorem is covered
            3. If gaps exist: Additional search for "CAP theorem"
            4. Cross-reference: Search for "eventual consistency" and "strong consistency"
            5. Verify completeness: Ensure ACID vs BASE is covered
            6. Additional retrieval if needed: Consensus algorithms (Paxos, Raft)
            7. Synthesize comprehensive answer with:
               - Core concepts clearly explained
               - Trade-offs between consistency models
               - Real-world examples and use cases
               - Detailed source attribution

            Meta-requirement: After synthesizing, identify any knowledge gaps
            that weren't adequately covered by retrieved documents and note them.
            """
        )
        print(f"Response: {response}\n")

    print("=" * 70)


if __name__ == "__main__":
    # Run main hybrid workflows
    asyncio.run(main())

    # Run advanced pattern demonstration
    asyncio.run(advanced_rag_patterns())
