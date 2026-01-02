"""Advanced RAG workflow with multi-hop reasoning.

This example demonstrates complex RAG patterns:
- Multi-query retrieval for comprehensive answers
- Cross-document synthesis
- Source attribution and verification
- Confidence scoring
"""

import asyncio

from dotenv import load_dotenv

from fluxibly import WorkflowSession

# Load environment variables from local.env
load_dotenv("local.env")


async def main() -> None:
    """Run advanced RAG workflows with complex reasoning."""
    print("=" * 70)
    print("Advanced RAG - Multi-hop Reasoning and Synthesis")
    print("=" * 70)

    async with WorkflowSession(profile="rag_assistant") as session:
        # Example 1: Multi-hop reasoning
        print("\n[Query 1] Multi-hop reasoning")
        response1 = await session.execute(
            """
            Question: How has deep learning impacted computer vision, and what are
            the implications for autonomous vehicles?

            This requires:
            1. Retrieve information about deep learning in computer vision
            2. Retrieve information about autonomous vehicle technology
            3. Synthesize the connection between these domains
            4. Cite specific sources for each claim
            """
        )
        print(f"Response: {response1}\n")

        # Example 2: Comparative synthesis
        print("[Query 2] Comparative synthesis across documents")
        response2 = await session.execute(
            """
            Compare different perspectives on AI ethics found in the knowledge base.
            Retrieve multiple viewpoints and synthesize:
            - Common themes across sources
            - Points of disagreement
            - Evolution of thinking over time
            - Cite each perspective with source attribution
            """
        )
        print(f"Response: {response2}\n")

        # Example 3: Gap analysis
        print("[Query 3] Knowledge gap identification")
        response3 = await session.execute(
            """
            Based on the available documents, analyze:
            1. What information exists about reinforcement learning?
            2. What important topics or applications are well-covered?
            3. What gaps or missing information do you notice?
            4. Rate your confidence in the completeness of retrieved information
            """
        )
        print(f"Response: {response3}\n")

        # Example 4: Temporal analysis
        print("[Query 4] Temporal/trend analysis")
        response4 = await session.execute(
            """
            Analyze how the understanding of transformers in NLP has evolved.
            If documents have timestamps or date metadata:
            1. Retrieve documents across different time periods
            2. Identify how concepts, techniques, or applications changed
            3. Highlight major breakthroughs or shifts in thinking
            """
        )
        print(f"Response: {response4}\n")

    print("=" * 70)
    print("Advanced RAG workflows complete!")


if __name__ == "__main__":
    asyncio.run(main())
