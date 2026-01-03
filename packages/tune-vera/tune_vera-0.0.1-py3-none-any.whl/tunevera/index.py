"""
VERA - FAISS-based search index
"""
import numpy as np
from typing import List, Tuple, Optional, Any, Union
from dataclasses import dataclass

from .data import EmbeddingDataset
from .adapter import VeraAdapter


@dataclass
class SearchResult:
    """Single search result"""
    score: float
    answer: str
    index: int


class VeraIndex:
    """
    FAISS-based search index for finding similar embeddings.

    Stores answer embeddings and allows searching with adapted question embeddings.
    """

    def __init__(
        self,
        data: EmbeddingDataset,
        model_adapter: VeraAdapter,
        model_embedding: Any,
        use_gpu: bool = False
    ):
        """
        Initialize the search index.

        Args:
            data: EmbeddingDataset containing answers and their embeddings
            model_adapter: Trained VeraAdapter for transforming queries
            model_embedding: Embedding model for encoding query strings
            use_gpu: Whether to use GPU for FAISS (if available)

        Note:
            The index stores ONLY unique answer embeddings. Duplicates are
            automatically filtered to avoid redundant storage and results.
        """
        self.data = data
        self.adapter = model_adapter
        self.embedding_model = model_embedding
        self.use_gpu = use_gpu

        # Filter unique answers and their embeddings
        unique_answers, unique_indices = self._get_unique_answers(
            data.answers,
            data.answer_embeddings
        )

        # Get answer embeddings (these are what we search against)
        # Only unique answers are stored in the index
        self.answer_embeddings = data.answer_embeddings[unique_indices].astype(np.float32)
        self.dim = self.answer_embeddings.shape[1]

        # Store unique texts for retrieval
        self.answers = unique_answers

        print(f"Index: {len(unique_answers)} unique answers (from {len(data.answers)} total)")

        # Build FAISS index
        self._build_index()

        # Build baseline index (without adapter)
        self._build_baseline_index()

    def _get_unique_answers(
        self,
        answers: List[str],
        embeddings: np.ndarray
    ) -> Tuple[List[str], List[int]]:
        """
        Get unique answers and their corresponding indices.

        Args:
            answers: List of answer strings
            embeddings: Answer embeddings array

        Returns:
            Tuple of (unique_answers, indices of first occurrence)
        """
        seen = {}
        unique_answers = []
        unique_indices = []

        for i, answer in enumerate(answers):
            if answer not in seen:
                seen[answer] = i
                unique_answers.append(answer)
                unique_indices.append(i)

        return unique_answers, unique_indices

    def _build_index(self):
        """Build the FAISS index with adapted embeddings"""
        try:
            import faiss
        except ImportError:
            raise ImportError("Please install faiss: pip install faiss-cpu or faiss-gpu")

        # Transform answer embeddings through the adapter
        # This allows us to search in the "adapted" space
        adapted_answers = self.adapter.transform_vect(self.answer_embeddings)
        adapted_answers = adapted_answers.astype(np.float32)

        # Normalize for cosine similarity
        faiss.normalize_L2(adapted_answers)

        # Create index
        self.index = faiss.IndexFlatIP(self.dim)  # Inner product = cosine sim after normalization

        if self.use_gpu:
            try:
                res = faiss.StandardGpuResources()
                self.index = faiss.index_cpu_to_gpu(res, 0, self.index)
            except Exception:
                pass  # Fall back to CPU

        self.index.add(adapted_answers)

    def _build_baseline_index(self):
        """Build a baseline index without adapter transformation"""
        try:
            import faiss
        except ImportError:
            return  # Already raised in _build_index

        # Use original answer embeddings
        original_answers = self.answer_embeddings.copy()
        faiss.normalize_L2(original_answers)

        self.baseline_index = faiss.IndexFlatIP(self.dim)
        self.baseline_index.add(original_answers)

    def search(
        self,
        query: Union[str, np.ndarray, List[float]],
        top_k: int = 5,
        baseline: bool = False
    ) -> List[SearchResult]:
        """
        Search for similar answers given a query.

        Args:
            query: Query string or pre-computed embedding (1D or 2D array)
            top_k: Number of results to return
            baseline: If True, also return baseline results (without adapter)

        Returns:
            List of SearchResult objects, or tuple of (adapted_results, baseline_results)
            if baseline=True
        """
        import faiss

        # Handle different query types
        if isinstance(query, str):
            # Text query: compute embedding
            query_embedding = self.embedding_model.embed_query([query])[0:1]  # Keep 2D
        else:
            # Pre-computed embedding
            query_embedding = np.array(query)
            if query_embedding.ndim == 1:
                query_embedding = query_embedding.reshape(1, -1)  # Make 2D

        # Transform through adapter
        adapted_query = self.adapter.transform_vect(query_embedding).astype(np.float32)
        faiss.normalize_L2(adapted_query)

        # Search
        scores, indices = self.index.search(adapted_query, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            results.append(SearchResult(
                score=float(score),
                answer=self.answers[idx],
                index=int(idx)
            ))

        if baseline:
            # Also search with original embedding
            original_query = query_embedding.astype(np.float32)
            faiss.normalize_L2(original_query)

            baseline_scores, baseline_indices = self.baseline_index.search(original_query, top_k)

            baseline_results = []
            for score, idx in zip(baseline_scores[0], baseline_indices[0]):
                baseline_results.append(SearchResult(
                    score=float(score),
                    answer=self.answers[idx],
                    index=int(idx)
                ))

            return results, baseline_results

        return results

    def search_batch(
        self,
        queries: Union[List[str], np.ndarray, List[List[float]]],
        top_k: int = 5,
        baseline: bool = False
    ) -> List[List[SearchResult]]:
        """
        Search for multiple queries at once.

        Args:
            queries: List of query strings or pre-computed embeddings (2D array)
            top_k: Number of results per query
            baseline: If True, also return baseline results (without adapter)

        Returns:
            List of result lists, one per query, or tuple of (adapted_results, baseline_results)
            if baseline=True
        """
        import faiss

        # Handle different query types
        if isinstance(queries, list) and len(queries) > 0 and isinstance(queries[0], str):
            # Text queries: compute embeddings
            query_embeddings = self.embedding_model.embed_query(queries)
        else:
            # Pre-computed embeddings
            query_embeddings = np.array(queries)

        # Transform through adapter
        adapted_queries = self.adapter.transform_vect(query_embeddings).astype(np.float32)
        faiss.normalize_L2(adapted_queries)

        # Search
        scores, indices = self.index.search(adapted_queries, top_k)

        all_results = []
        for q_scores, q_indices in zip(scores, indices):
            results = []
            for score, idx in zip(q_scores, q_indices):
                results.append(SearchResult(
                    score=float(score),
                    answer=self.answers[idx],
                    index=int(idx)
                ))
            all_results.append(results)

        if baseline:
            # Also search with original embeddings
            original_queries = query_embeddings.astype(np.float32)
            faiss.normalize_L2(original_queries)

            baseline_scores, baseline_indices = self.baseline_index.search(original_queries, top_k)

            all_baseline_results = []
            for q_scores, q_indices in zip(baseline_scores, baseline_indices):
                results = []
                for score, idx in zip(q_scores, q_indices):
                    results.append(SearchResult(
                        score=float(score),
                        answer=self.answers[idx],
                        index=int(idx)
                    ))
                all_baseline_results.append(results)

            return all_results, all_baseline_results

        return all_results

    def save(self, path: str):
        """Save the index to disk"""
        import faiss
        import pickle

        # Save FAISS index
        faiss.write_index(
            faiss.index_gpu_to_cpu(self.index) if self.use_gpu else self.index,
            f"{path}.faiss"
        )
        faiss.write_index(self.baseline_index, f"{path}.baseline.faiss")

        # Save metadata (only answers, no questions)
        with open(f"{path}.meta", "wb") as f:
            pickle.dump({
                "answers": self.answers,
                "dim": self.dim
            }, f)

    @classmethod
    def load(
        cls,
        path: str,
        model_adapter: VeraAdapter,
        model_embedding: Any,
        use_gpu: bool = False
    ) -> "VeraIndex":
        """Load an index from disk"""
        import faiss
        import pickle

        # Create empty instance
        instance = object.__new__(cls)

        # Load FAISS index
        instance.index = faiss.read_index(f"{path}.faiss")
        instance.baseline_index = faiss.read_index(f"{path}.baseline.faiss")

        if use_gpu:
            try:
                res = faiss.StandardGpuResources()
                instance.index = faiss.index_cpu_to_gpu(res, 0, instance.index)
            except Exception:
                pass

        # Load metadata
        with open(f"{path}.meta", "rb") as f:
            meta = pickle.load(f)
            instance.answers = meta["answers"]
            instance.dim = meta["dim"]

        instance.adapter = model_adapter
        instance.embedding_model = model_embedding
        instance.use_gpu = use_gpu

        return instance


def index(
    data: EmbeddingDataset,
    model_adapter: VeraAdapter,
    model_embedding: Any,
    use_gpu: bool = False
) -> VeraIndex:
    """
    Create a VERA search index.

    Args:
        data: EmbeddingDataset with answers and their embeddings
        model_adapter: Trained adapter for query transformation
        model_embedding: Embedding model for encoding queries
        use_gpu: Use GPU acceleration for FAISS

    Returns:
        VeraIndex that searches against answer embeddings
    """
    return VeraIndex(
        data=data,
        model_adapter=model_adapter,
        model_embedding=model_embedding,
        use_gpu=use_gpu
    )
