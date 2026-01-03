"""
VERA - Data loading and dataset utilities
"""
import pandas as pd
import numpy as np
import pickle
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Tuple
import random


@dataclass
class VeraData:
    """Container for loaded Q&A data"""
    questions: List[str]
    answers: List[str]
    metadata: Optional[List[Dict[str, Any]]] = None

    def __len__(self):
        return len(self.questions)

    def __getitem__(self, idx):
        meta = self.metadata[idx] if self.metadata else {}
        return {
            "question": self.questions[idx],
            "answer": self.answers[idx],
            "metadata": meta
        }


@dataclass
class EmbeddingDataset:
    """Dataset containing embeddings for training"""
    question_embeddings: Any  # np.ndarray
    answer_embeddings: Any    # np.ndarray
    questions: List[str]
    answers: List[str]

    # Train/val split indices
    train_indices: List[int] = None
    val_indices: List[int] = None

    def __len__(self):
        return len(self.questions)

    def get_train_data(self) -> Tuple[Any, Any]:
        """Return training embeddings (questions, answers)"""
        if self.train_indices is None:
            return self.question_embeddings, self.answer_embeddings
        return (
            self.question_embeddings[self.train_indices],
            self.answer_embeddings[self.train_indices]
        )

    def get_val_data(self) -> Tuple[Any, Any]:
        """Return validation embeddings (questions, answers)"""
        if self.val_indices is None:
            return None, None
        return (
            self.question_embeddings[self.val_indices],
            self.answer_embeddings[self.val_indices]
        )

    def save(self, path: str):
        """
        Save the embedding dataset to disk.

        Args:
            path: Path to save the dataset (without extension)
        """
        # Save embeddings as numpy arrays
        np.save(f"{path}_q_emb.npy", self.question_embeddings)
        np.save(f"{path}_a_emb.npy", self.answer_embeddings)

        # Save metadata
        with open(f"{path}_meta.pkl", "wb") as f:
            pickle.dump({
                "questions": self.questions,
                "answers": self.answers,
                "train_indices": self.train_indices,
                "val_indices": self.val_indices
            }, f)

        print(f"Dataset saved to {path}")

    @classmethod
    def load(cls, path: str) -> "EmbeddingDataset":
        """
        Load an embedding dataset from disk.

        Args:
            path: Path to the saved dataset (without extension)

        Returns:
            EmbeddingDataset object
        """
        # Load embeddings
        question_embeddings = np.load(f"{path}_q_emb.npy")
        answer_embeddings = np.load(f"{path}_a_emb.npy")

        # Load metadata
        with open(f"{path}_meta.pkl", "rb") as f:
            meta = pickle.load(f)

        dataset = cls(
            question_embeddings=question_embeddings,
            answer_embeddings=answer_embeddings,
            questions=meta["questions"],
            answers=meta["answers"],
            train_indices=meta["train_indices"],
            val_indices=meta["val_indices"]
        )

        print(f"Dataset loaded from {path}")
        print(f"  - {len(dataset)} samples")
        print(f"  - Embedding dim: {question_embeddings.shape[1]}")

        return dataset


def load_data(
    path: str,
    question_col: str,
    answer_col: str,
    metadata_cols: Optional[List[str]] = None
) -> VeraData:
    """
    Load Q&A data from CSV file.

    Args:
        path: Path to CSV file
        question_col: Column name for questions
        answer_col: Column name for answers
        metadata_cols: Optional list of columns to include as metadata

    Returns:
        VeraData object containing questions and answers
    """
    try:
        df = pd.read_csv(path)
    except pd.errors.ParserError:
        try:
            df = pd.read_csv(path, delimiter=";")
        except pd.errors.ParserError:
            raise ValueError(
                f"Error al leer el archivo CSV '{path}'. "
                "Solo se admiten los delimitadores ',' y ';'."
            )

    if question_col not in df.columns:
        raise ValueError(f"Column '{question_col}' not found in CSV. Available: {list(df.columns)}")
    if answer_col not in df.columns:
        raise ValueError(f"Column '{answer_col}' not found in CSV. Available: {list(df.columns)}")

    questions = df[question_col].tolist()
    answers = df[answer_col].tolist()

    metadata = None
    if metadata_cols:
        metadata = df[metadata_cols].to_dict('records')

    return VeraData(
        questions=questions,
        answers=answers,
        metadata=metadata
    )


def train_val_split(
    data: VeraData,
    train_size: float = 0.8,
    seed: Optional[int] = None
) -> Tuple[List[int], List[int]]:
    """
    Split data indices into train and validation sets.

    Args:
        data: VeraData object
        train_size: Fraction of data for training
        seed: Random seed for reproducibility

    Returns:
        Tuple of (train_indices, val_indices)
    """
    n = len(data)
    indices = list(range(n))

    if seed is not None:
        random.seed(seed)
    random.shuffle(indices)

    split_idx = int(n * train_size)
    train_indices = indices[:split_idx]
    val_indices = indices[split_idx:]

    return train_indices, val_indices
