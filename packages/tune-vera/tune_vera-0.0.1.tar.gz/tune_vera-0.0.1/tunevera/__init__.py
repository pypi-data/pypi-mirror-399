"""
VERA - Vector Embedding Retrieval Adaptation

A library for adapting embeddings to personalized data using ResNet with bottleneck blocks.

Example usage:
    import vera

    # Load data
    data = vera.load_data("data.csv", question_col="q", answer_col="a")

    # Create embedding model
    model_emb = vera.embedding.openai(api_key="...", model="text-embedding-3-small")

    # Create embedding dataset
    data_emb = model_emb.emb_dataset(data, train_size=0.8)

    # Create and train adapter
    model_adapter = vera.adapter(embedding_dim=1536, bottleneck_dim=256, num_blocks=5)
    model_adapter.fit(data_emb)

    # Create search index
    idx = vera.index(embeddings=data_emb, model_adapter=model_adapter, model_embedding=model_emb)

    # Search
    results = idx.search("my query", top_k=5)
"""

__version__ = "0.1.0"
__author__ = "VERA"

# Data loading
from .data import load_data, VeraData, EmbeddingDataset

# Embedding and LLM modules
from . import embedding
from . import llm

# Adapter
from .adapter import adapter, VeraAdapter, VeraAdapterModel, BottleneckBlock

# Index
from .index import index, VeraIndex, SearchResult

__all__ = [
    # Version
    "__version__",
    # Data
    "load_data",
    "VeraData",
    "EmbeddingDataset",
    # Modules
    "embedding",
    "llm",
    # Adapter
    "adapter",
    "VeraAdapter",
    "VeraAdapterModel",
    "BottleneckBlock",
    # Index
    "index",
    "VeraIndex",
    "SearchResult",
]
