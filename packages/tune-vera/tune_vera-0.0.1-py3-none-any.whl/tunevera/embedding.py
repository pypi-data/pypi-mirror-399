"""
VERA - Embedding model wrappers
"""
import numpy as np
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union
from tqdm import tqdm

from .data import VeraData, EmbeddingDataset, train_val_split


class BaseEmbeddingModel(ABC):
    """Base class for embedding models"""

    @abstractmethod
    def embed(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of strings to embed

        Returns:
            np.ndarray of shape (len(texts), embedding_dim)
        """
        pass

    @property
    @abstractmethod
    def dim(self) -> int:
        """Return the embedding dimension"""
        pass

    def embed_query(self, texts: List[str]) -> np.ndarray:
        """
        Embed queries (questions). Override for asymmetric models.
        Default: same as embed()
        """
        return self.embed(texts)

    def embed_document(self, texts: List[str]) -> np.ndarray:
        """
        Embed documents (answers). Override for asymmetric models.
        Default: same as embed()
        """
        return self.embed(texts)

    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = True,
        embed_type: str = "default"
    ) -> np.ndarray:
        """
        Generate embeddings in batches.

        Args:
            texts: List of strings to embed
            batch_size: Number of texts per batch
            show_progress: Show progress bar
            embed_type: "default", "query" or "document" (for asymmetric models)

        Returns:
            np.ndarray of shape (len(texts), embedding_dim)
        """
        # Select embedding function based on type
        if embed_type == "query":
            embed_fn = self.embed_query
        elif embed_type == "document":
            embed_fn = self.embed_document
        else:
            embed_fn = self.embed

        embeddings = []
        iterator = range(0, len(texts), batch_size)

        if show_progress:
            iterator = tqdm(iterator, desc="Generating embeddings")

        for i in iterator:
            batch = texts[i:i + batch_size]
            batch_emb = embed_fn(batch)
            embeddings.append(batch_emb)

            # Clear CUDA memory after each batch
            self._clear_cuda_cache()

        return np.vstack(embeddings)

    def _clear_cuda_cache(self):
        """Clear CUDA memory cache if available."""
        import gc
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass

    def _reload_model_if_needed(self):
        """Reload model to free fragmented GPU memory. Override in subclasses."""
        self._clear_cuda_cache()

    def _get_vram_gb(self) -> float:
        """Get available VRAM in GB. Returns 4.0 as default if not available."""
        try:
            import torch
            if torch.cuda.is_available():
                props = torch.cuda.get_device_properties(0)
                return props.total_memory / (1024 ** 3)
        except ImportError:
            pass
        return 4.0  # Default fallback

    def emb_dataset(
        self,
        data: VeraData,
        train_size: float = 0.8,
        seed: Optional[int] = None,
        augmentation: bool = False,
        n_augmentations: int = 5,
        model_text: Optional[Any] = None,
        batch_size: int = 32
    ) -> EmbeddingDataset:
        """
        Create an EmbeddingDataset from VeraData.

        Args:
            data: VeraData object with questions and answers
            train_size: Fraction of data for training
            seed: Random seed for reproducibility
            augmentation: Whether to augment questions with paraphrases
            n_augmentations: Number of paraphrases per question
            model_text: LLM model for generating paraphrases
            batch_size: Batch size for embedding generation

        Returns:
            EmbeddingDataset ready for training
        """
        questions = data.questions.copy()
        answers = data.answers.copy()

        # Data augmentation
        if augmentation:
            if model_text is None:
                raise ValueError("model_text is required for augmentation")

            print(f"Generating {n_augmentations} paraphrases per question...")
            augmented_questions = []
            augmented_answers = []

            for q, a in tqdm(zip(data.questions, data.answers), total=len(data)):
                # Generate paraphrases
                paraphrases = model_text.paraphrase(q, n=n_augmentations)
                augmented_questions.extend(paraphrases)
                augmented_answers.extend([a] * len(paraphrases))

            questions.extend(augmented_questions)
            answers.extend(augmented_answers)

        # Generate embeddings (using asymmetric methods if available)
        # Calculate adaptive batch sizes based on text length and VRAM
        avg_q_len = sum(len(q) for q in questions) / len(questions)
        avg_a_len = sum(len(a) for a in answers) / len(answers)

        # Reference: 50 chars, 4GB VRAM, batch_size=128
        base_chars, base_vram, base_batch = 50, 4.0, 128
        vram_gb = self._get_vram_gb()

        # batch = (base_chars / avg_len) * base_batch * (vram / base_vram)
        q_batch_size = max(1, int((base_chars / avg_q_len) * base_batch * (vram_gb / base_vram)))
        a_batch_size = max(1, int((base_chars / avg_a_len) * base_batch * (vram_gb / base_vram)))

        print(f"VRAM: {vram_gb:.1f} GB")
        print(f"Avg question length: {avg_q_len:.0f} chars, batch_size: {q_batch_size}")
        print(f"Avg answer length: {avg_a_len:.0f} chars, batch_size: {a_batch_size}")

        print("Embedding questions (as queries)...")
        question_embeddings = self.embed_batch(questions, batch_size=q_batch_size, embed_type="query")

        # Force full memory cleanup: unload and reload model
        self._reload_model_if_needed()

        print("Embedding answers (as documents)...")
        answer_embeddings = self.embed_batch(answers, batch_size=a_batch_size, embed_type="document")

        # Create dataset with original indices for split
        original_len = len(data)
        train_idx, val_idx = train_val_split(
            VeraData(questions[:original_len], answers[:original_len]),
            train_size=train_size,
            seed=seed
        )

        # Extend train indices to include augmented data
        if augmentation:
            augmented_indices = list(range(original_len, len(questions)))
            train_idx = train_idx + augmented_indices

        return EmbeddingDataset(
            question_embeddings=question_embeddings,
            answer_embeddings=answer_embeddings,
            questions=questions,
            answers=answers,
            train_indices=train_idx,
            val_indices=val_idx
        )


class OpenAIEmbedding(BaseEmbeddingModel):
    """OpenAI embedding model wrapper"""

    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        base_url: Optional[str] = None
    ):
        """
        Initialize OpenAI embedding model.

        Args:
            api_key: OpenAI API key
            model: Model name (e.g., "text-embedding-3-small", "text-embedding-3-large")
            base_url: Optional custom base URL
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Please install openai: pip install openai")

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self._dim = None

    @property
    def dim(self) -> int:
        if self._dim is None:
            # Get dimension by embedding a test string
            test_emb = self.embed(["test"])
            self._dim = test_emb.shape[1]
        return self._dim

    def embed(self, texts: List[str]) -> np.ndarray:
        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )
        except:
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )

        embeddings = [item.embedding for item in response.data]
        return np.array(embeddings)


class HuggingFaceEmbedding(BaseEmbeddingModel):
    """HuggingFace/Sentence-Transformers embedding model wrapper"""

    def __init__(
        self,
        model: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: str = "cuda"
    ):
        """
        Initialize HuggingFace embedding model.

        Args:
            model: Model name or path
            device: Device to use ("cuda" or "cpu")
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError("Please install sentence-transformers: pip install sentence-transformers")

        self.model = SentenceTransformer(model, device=device)
        self.model_name = model
        self.device = device
        self._dim = self.model.get_sentence_embedding_dimension()

    @property
    def dim(self) -> int:
        return self._dim

    def embed(self, texts: List[str]) -> np.ndarray:
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        self._clear_cuda_cache()
        return embeddings

    def _reload_model_if_needed(self):
        """Unload model from GPU, clear memory, reload model."""
        import gc
        try:
            import torch
            from sentence_transformers import SentenceTransformer

            print("Reloading model to free GPU memory...")

            # Delete current model
            del self.model
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            # Reload model
            self.model = SentenceTransformer(self.model_name, device=self.device)
            print("Model reloaded successfully")
        except Exception as e:
            print(f"Could not reload model: {e}, using cache clear only")
            self._clear_cuda_cache()


class HuggingFaceAsymmetricEmbedding(BaseEmbeddingModel):
    """
    HuggingFace embedding model with asymmetric query/document prefixes.

    Optimized for retrieval tasks where queries (questions) and documents (answers)
    should be embedded differently for better semantic matching.

    Supported models and their prefixes:
    - intfloat/e5-*: "query: " / "passage: "
    - intfloat/multilingual-e5-*: "query: " / "passage: "
    - BAAI/bge-*: "Represent this sentence for searching relevant passages: " / ""
    - Alibaba-NLP/gte-*: "query: " / ""
    """

    # Preset prefixes for popular asymmetric models
    MODEL_PREFIXES = {
        "e5": {"query": "query: ", "document": "passage: "},
        "bge": {"query": "Represent this sentence for searching relevant passages: ", "document": ""},
        "gte": {"query": "query: ", "document": ""},
    }

    def __init__(
        self,
        model: str = "intfloat/multilingual-e5-large",
        device: str = "cuda",
        query_prefix: Optional[str] = None,
        document_prefix: Optional[str] = None
    ):
        """
        Initialize asymmetric HuggingFace embedding model.

        Args:
            model: Model name or path (e.g., "intfloat/multilingual-e5-large")
            device: Device to use ("cuda" or "cpu")
            query_prefix: Custom prefix for queries (auto-detected if None)
            document_prefix: Custom prefix for documents (auto-detected if None)
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError("Please install sentence-transformers: pip install sentence-transformers")

        self.model = SentenceTransformer(model, device=device)
        self.model_name = model
        self.device = device
        self._dim = self.model.get_sentence_embedding_dimension()

        # Auto-detect or use custom prefixes
        self.query_prefix, self.document_prefix = self._get_prefixes(
            model, query_prefix, document_prefix
        )

        print(f"Asymmetric embedding initialized:")
        print(f"  - Model: {model}")
        print(f"  - Query prefix: '{self.query_prefix}'")
        print(f"  - Document prefix: '{self.document_prefix}'")

    def _get_prefixes(
        self,
        model: str,
        query_prefix: Optional[str],
        document_prefix: Optional[str]
    ) -> tuple:
        """Auto-detect prefixes based on model name or use custom ones."""
        if query_prefix is not None and document_prefix is not None:
            return query_prefix, document_prefix

        model_lower = model.lower()
        for key, prefixes in self.MODEL_PREFIXES.items():
            if key in model_lower:
                return (
                    query_prefix or prefixes["query"],
                    document_prefix or prefixes["document"]
                )

        # Default: no prefixes
        return query_prefix or "", document_prefix or ""

    @property
    def dim(self) -> int:
        return self._dim

    def embed(self, texts: List[str]) -> np.ndarray:
        """Default embed (no prefix)"""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        self._clear_cuda_cache()
        return embeddings

    def embed_query(self, texts: List[str]) -> np.ndarray:
        """Embed queries with query prefix"""
        prefixed = [f"{self.query_prefix}{t}" for t in texts]
        embeddings = self.model.encode(prefixed, convert_to_numpy=True)
        self._clear_cuda_cache()
        return embeddings

    def embed_document(self, texts: List[str]) -> np.ndarray:
        """Embed documents with document prefix"""
        prefixed = [f"{self.document_prefix}{t}" for t in texts]
        embeddings = self.model.encode(prefixed, convert_to_numpy=True)
        self._clear_cuda_cache()
        return embeddings


class CustomEmbedding(BaseEmbeddingModel):
    """Custom API embedding model wrapper"""

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        embedding_key: str = "embedding",
        input_key: str = "input"
    ):
        """
        Initialize custom embedding model.

        Args:
            base_url: API endpoint URL
            api_key: Optional API key (added to Authorization header)
            headers: Optional additional headers
            embedding_key: Key in response JSON containing embeddings
            input_key: Key in request JSON for input texts
        """
        try:
            import requests
        except ImportError:
            raise ImportError("Please install requests: pip install requests")

        self.base_url = base_url
        self.embedding_key = embedding_key
        self.input_key = input_key
        self._dim = None

        self.headers = headers or {}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        self.headers.setdefault("Content-Type", "application/json")

    @property
    def dim(self) -> int:
        if self._dim is None:
            test_emb = self.embed(["test"])
            self._dim = test_emb.shape[1]
        return self._dim

    def embed(self, texts: List[str]) -> np.ndarray:
        import requests

        response = requests.post(
            self.base_url,
            headers=self.headers,
            json={self.input_key: texts}
        )
        response.raise_for_status()

        data = response.json()
        embeddings = data[self.embedding_key]

        # Handle nested structure (like OpenAI format)
        if isinstance(embeddings, list) and len(embeddings) > 0:
            if isinstance(embeddings[0], dict):
                embeddings = [e["embedding"] for e in embeddings]

        return np.array(embeddings)


# Factory functions for cleaner API
def openai(
    api_key: str,
    model: str = "text-embedding-3-small",
    base_url: Optional[str] = None
) -> OpenAIEmbedding:
    """Create an OpenAI embedding model"""
    return OpenAIEmbedding(api_key=api_key, model=model, base_url=base_url)


def huggingface(
    model: str = "sentence-transformers/all-MiniLM-L6-v2",
    device: str = "cuda"
) -> HuggingFaceEmbedding:
    """Create a HuggingFace embedding model (symmetric)"""
    return HuggingFaceEmbedding(model=model, device=device)


def huggingface_asymmetric(
    model: str = "intfloat/multilingual-e5-large",
    device: str = "cuda",
    query_prefix: Optional[str] = None,
    document_prefix: Optional[str] = None
) -> HuggingFaceAsymmetricEmbedding:
    """
    Create an asymmetric HuggingFace embedding model.

    Recommended models:
    - intfloat/multilingual-e5-large (multilingual, 1024 dim)
    - intfloat/multilingual-e5-base (multilingual, 768 dim)
    - BAAI/bge-m3 (multilingual, 1024 dim)
    - BAAI/bge-large-en-v1.5 (English, 1024 dim)
    """
    return HuggingFaceAsymmetricEmbedding(
        model=model,
        device=device,
        query_prefix=query_prefix,
        document_prefix=document_prefix
    )


def custom(
    base_url: str,
    api_key: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> CustomEmbedding:
    """Create a custom API embedding model"""
    return CustomEmbedding(base_url=base_url, api_key=api_key, headers=headers, **kwargs)
