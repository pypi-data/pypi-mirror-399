# VERA - Vector Embedding Retrieval Adaptation

Adapt embeddings to your personalized data using ResNet with bottleneck blocks.

## Installation

```bash
pip install tune-vera
```

With optional dependencies:

```bash
pip install tune-vera[openai]        # OpenAI support
pip install tune-vera[huggingface]   # HuggingFace/Sentence-Transformers
pip install tune-vera[faiss-cpu]     # FAISS index (CPU)
pip install tune-vera[all]           # Everything
```

## Quick Start

```python
import tunevera

# 1. Load your Q&A data
data = tunevera.load_data(
    path="my_data.csv",
    question_col="question",
    answer_col="answer"
)

# 2. Create embedding model
model_emb = tunevera.embedding.openai(
    api_key="sk-...",
    model="text-embedding-3-small"
)

# 3. Generate embeddings dataset
data_emb = model_emb.emb_dataset(data, train_size=0.8, seed=42)

# 4. Create and train the adapter
model_adapter = tunevera.adapter(
    embedding_dim=1536,
    bottleneck_dim=256,
    num_blocks=5,
    epochs=10,
    batch_size=32
)
model_adapter.fit(data_emb)

# 5. Create search index
index = tunevera.index(
    embeddings=data_emb,
    model_adapter=model_adapter,
    model_embedding=model_emb
)

# 6. Search
results = index.search("How do I reset my password?", top_k=5)
for r in results:
    print(f"{r.score:.3f}: {r.answer}")
```

## How It Works

VERA trains a ResNet with bottleneck blocks to transform embeddings. The bottleneck architecture significantly reduces parameters:

```
Standard:   1536 x 1536 = 2,359,296 params per layer
Bottleneck: 1536 x 256 + 256 x 1536 = 786,432 params (~66% reduction)
```

The model learns to transform question embeddings to be similar to their corresponding answer embeddings using cosine similarity loss.

## Embedding Providers

### OpenAI
```python
model_emb = tunevera.embedding.openai(api_key="...", model="text-embedding-3-small")
```

### HuggingFace
```python
model_emb = tunevera.embedding.huggingface(
    model="sentence-transformers/all-MiniLM-L6-v2",
    device="cuda"
)
```

### Custom API
```python
model_emb = tunevera.embedding.custom(
    base_url="https://my-api.com/embed",
    api_key="..."
)
```

## Data Augmentation

Generate paraphrases to augment your training data:

```python
model_text = tunevera.llm.openai(api_key="...", model="gpt-4o-mini")

data_emb = model_emb.emb_dataset(
    data,
    augmentation=True,
    n_augmentations=5,
    model_text=model_text
)
```

## License

MIT
