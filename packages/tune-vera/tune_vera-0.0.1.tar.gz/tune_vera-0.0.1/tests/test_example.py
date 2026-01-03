"""
Test example for VERA (Vector Embedding Retrieval Adaptation)

To run this test, set your API key as environment variable:
    export OPENAI_API_KEY="your-api-key"

Or for DashScope:
    export DASHSCOPE_API_KEY="your-api-key"
"""
import os
import tunevera
from tunetunevera.data import EmbeddingDataset
from tunetunevera.adapter import VeraAdapter, check_embedding_collapse
from tunetunevera.index import VeraIndex


def test_load_data():
    """Test loading data from CSV."""
    path_data = os.path.join(os.path.dirname(__file__), "sample_data.csv")
    data = tunevera.load_data(
        path=path_data,
        question_col="pregunta",
        answer_col="respuesta"
    )
    assert len(data) == 5
    print(f"Loaded {len(data)} samples")


def test_full_pipeline():
    """
    Full pipeline test (requires API key).
    Skip if no API key is set.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Skipping: OPENAI_API_KEY not set")
        return

    # 1. Load data
    path_data = os.path.join(os.path.dirname(__file__), "sample_data.csv")
    data = tunevera.load_data(
        path=path_data,
        question_col="pregunta",
        answer_col="respuesta"
    )

    # 2. Load embedding model
    model_emb = tunevera.embedding.openai(
        api_key=api_key,
        model="text-embedding-3-small"
    )

    # 3. Create embedding dataset
    data_emb = model_emb.emb_dataset(
        data=data,
        train_size=0.8,
        seed=42,
        batch_size=32
    )

    # 4. Create and train VERA adapter
    model_adapter = tunevera.adapter(
        embedding_dim=1536,
        arch_type="adapter",
        bottleneck_dim=64,
        epochs=5,
        batch_size=32,
        loss_type="cosine_margin",
        temperature=0.10,
        device="cpu"
    )
    model_adapter.fit(data_emb)

    # 5. Check for embedding collapse
    original_embs = data_emb.question_embeddings
    transformed_embs = model_adapter.transform_vect(original_embs)
    collapse_check = check_embedding_collapse(original_embs, transformed_embs)
    print(f"Collapse ratio: {collapse_check['collapse_ratio']:.4f}")

    # 6. Create search index
    index = tunevera.index(
        data=data_emb,
        model_adapter=model_adapter,
        model_embedding=model_emb
    )

    # 7. Search
    query = "¿Cuál es el límite del plan Oro?"
    results = index.search(query=query, top_k=3)

    print(f"\nQuery: {query}")
    for i, result in enumerate(results[0]):
        print(f"{i+1}. Score: {result.score:.4f} - {result.answer[:50]}...")


if __name__ == "__main__":
    test_load_data()
    test_full_pipeline()
