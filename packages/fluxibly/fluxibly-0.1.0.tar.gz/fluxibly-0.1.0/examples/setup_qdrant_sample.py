"""Setup Qdrant with sample documents for RAG examples.

This script helps you populate a Qdrant collection with sample documents
to test the RAG workflow examples.
"""

import asyncio
from typing import Any

# Note: This is a helper script. You'll need to install qdrant-client:
# uv add qdrant-client sentence-transformers

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, PointStruct, VectorParams
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Error: Required packages not installed.")
    print("Install with: uv add qdrant-client sentence-transformers")
    exit(1)


# Sample documents about machine learning and AI
SAMPLE_DOCUMENTS = [
    {
        "id": 1,
        "text": (
            "Deep learning is a subset of machine learning that uses neural networks with "
            "multiple layers. These networks can automatically learn hierarchical "
            "representations of data, making them particularly effective for tasks like "
            "image recognition, natural language processing, and speech recognition."
        ),
        "metadata": {"topic": "deep_learning", "category": "fundamentals"},
    },
    {
        "id": 2,
        "text": (
            "Neural network architectures include feedforward networks, convolutional neural "
            "networks (CNNs) for image processing, recurrent neural networks (RNNs) for "
            "sequential data, and transformers for natural language understanding. Each "
            "architecture is optimized for specific types of tasks and data."
        ),
        "metadata": {"topic": "neural_networks", "category": "architectures"},
    },
    {
        "id": 3,
        "text": (
            "Supervised learning involves training models on labeled data, where each input "
            "has a corresponding output label. Common supervised learning tasks include "
            "classification (categorizing data) and regression (predicting continuous values). "
            "Examples include email spam detection and house price prediction."
        ),
        "metadata": {"topic": "supervised_learning", "category": "fundamentals"},
    },
    {
        "id": 4,
        "text": (
            "Unsupervised learning works with unlabeled data to discover patterns and "
            "structures. Techniques include clustering (grouping similar items), dimensionality "
            "reduction (simplifying data while preserving important features), and anomaly "
            "detection. It's useful for customer segmentation and data exploration."
        ),
        "metadata": {"topic": "unsupervised_learning", "category": "fundamentals"},
    },
    {
        "id": 5,
        "text": (
            "Training neural networks involves backpropagation and gradient descent. "
            "Backpropagation calculates gradients of the loss function with respect to network "
            "weights, while optimization algorithms like SGD, Adam, and RMSprop adjust weights "
            "to minimize loss. Learning rate, batch size, and regularization are critical "
            "hyperparameters."
        ),
        "metadata": {"topic": "training", "category": "techniques"},
    },
    {
        "id": 6,
        "text": (
            "Computer vision applications of deep learning include object detection, semantic "
            "segmentation, facial recognition, and medical image analysis. CNNs revolutionized "
            "this field, achieving human-level performance on many tasks. Transfer learning "
            "with pre-trained models like ResNet and VGG enables quick deployment."
        ),
        "metadata": {"topic": "computer_vision", "category": "applications"},
    },
    {
        "id": 7,
        "text": (
            "Natural language processing (NLP) uses transformers and attention mechanisms for "
            "tasks like machine translation, sentiment analysis, question answering, and text "
            "generation. Models like BERT, GPT, and T5 have achieved state-of-the-art results "
            "through pre-training on massive text corpora and fine-tuning on specific tasks."
        ),
        "metadata": {"topic": "nlp", "category": "applications"},
    },
    {
        "id": 8,
        "text": (
            "Autonomous vehicles rely on deep learning for perception, planning, and control. "
            "CNNs process camera, LiDAR, and radar data to detect objects, predict trajectories, "
            "and make driving decisions. Challenges include handling edge cases, ensuring safety, "
            "and building robust systems that work in diverse conditions."
        ),
        "metadata": {"topic": "autonomous_vehicles", "category": "applications"},
    },
    {
        "id": 9,
        "text": (
            "AI ethics addresses fairness, transparency, privacy, and accountability in AI "
            "systems. Key concerns include algorithmic bias, data privacy, job displacement, "
            "and the potential misuse of AI. Frameworks like GDPR and ethical AI principles "
            "guide responsible development and deployment of AI technologies."
        ),
        "metadata": {"topic": "ai_ethics", "category": "ethics"},
    },
    {
        "id": 10,
        "text": (
            "Reinforcement learning trains agents to make sequential decisions by interacting "
            "with environments and receiving rewards. Applications include game playing (AlphaGo), "
            "robotics control, recommendation systems, and resource optimization. Key algorithms "
            "include Q-learning, policy gradients, and actor-critic methods."
        ),
        "metadata": {"topic": "reinforcement_learning", "category": "fundamentals"},
    },
    {
        "id": 11,
        "text": (
            "Transformers revolutionized NLP through self-attention mechanisms that capture "
            "long-range dependencies in sequences. Unlike RNNs, transformers process sequences "
            "in parallel, enabling efficient training on massive datasets. The architecture "
            "consists of encoder and decoder blocks with multi-head attention and feedforward layers."
        ),
        "metadata": {"topic": "transformers", "category": "architectures"},
    },
    {
        "id": 12,
        "text": (
            "Transfer learning leverages knowledge from pre-trained models to solve new tasks "
            "with limited data. In computer vision, models pre-trained on ImageNet can be "
            "fine-tuned for specific applications. In NLP, language models pre-trained on vast "
            "text corpora can be adapted for downstream tasks with minimal additional training."
        ),
        "metadata": {"topic": "transfer_learning", "category": "techniques"},
    },
]


async def setup_qdrant_collection() -> None:
    """Create Qdrant collection and populate with sample documents."""
    print("=" * 70)
    print("Setting up Qdrant with Sample Documents for RAG Examples")
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

    # Create collection
    # Using 'rag_documents' to avoid conflicts with existing 'documents' collection
    collection_name = "rag_documents"
    print(f"\n[Step 3] Creating collection '{collection_name}'...")

    # Delete existing collection if it exists
    try:
        client.delete_collection(collection_name=collection_name)
        print(f"  Deleted existing collection '{collection_name}'")
    except Exception:
        pass

    # Create new collection with named vector
    # MCP server expects vector name: "fast-all-minilm-l6-v2"
    vector_name = "fast-all-minilm-l6-v2"
    client.create_collection(
        collection_name=collection_name,
        vectors_config={vector_name: VectorParams(size=embedding_dim, distance=Distance.COSINE)},
    )
    print(f"✓ Created collection '{collection_name}' with vector '{vector_name}'")

    # Generate embeddings and prepare points
    print("\n[Step 4] Generating embeddings for sample documents...")
    points: list[PointStruct] = []

    for doc in SAMPLE_DOCUMENTS:
        # Generate embedding
        embedding = model.encode(doc["text"]).tolist()

        # Create point with named vector
        point = PointStruct(
            id=doc["id"],
            vector={vector_name: embedding},
            payload={"text": doc["text"], **doc["metadata"]},
        )
        points.append(point)

        print(f"  ✓ Document {doc['id']}: {doc['metadata']['topic']}")

    # Upload points to Qdrant
    print(f"\n[Step 5] Uploading {len(points)} documents to Qdrant...")
    client.upsert(collection_name=collection_name, points=points)
    print("✓ Documents uploaded successfully")

    # Verify collection
    print("\n[Step 6] Verifying collection...")
    collection_info = client.get_collection(collection_name=collection_name)
    print(f"✓ Collection contains {collection_info.points_count} documents")

    # Test a sample search
    print("\n[Step 7] Testing semantic search...")
    query = "What is deep learning?"
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
        topic: str = payload.get("topic", "unknown")
        score: float = result.score
        print(f"\n{i}. [Score: {score:.3f}] Topic: {topic}")
        print(f"   {text[:100]}...")

    print("\n" + "=" * 70)
    print("Setup Complete! Your Qdrant collection is ready for RAG examples.")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Run RAG examples: uv run python examples/workflow_rag_basic.py")
    print("2. Try your own queries with the conversational example")
    print("3. Explore advanced patterns with multi-hop reasoning")


if __name__ == "__main__":
    asyncio.run(setup_qdrant_collection())
