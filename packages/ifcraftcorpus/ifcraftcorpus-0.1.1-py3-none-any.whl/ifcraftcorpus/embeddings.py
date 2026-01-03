"""
Semantic embeddings for vector search.

Optional module - requires sentence-transformers.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

    from ifcraftcorpus.index import CorpusIndex

# Default model - small, fast, good for semantic similarity
DEFAULT_MODEL = "all-MiniLM-L6-v2"


class EmbeddingIndex:
    """Vector embedding index for semantic search."""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        *,
        lazy_load: bool = True,
    ) -> None:
        """Initialize the embedding index.

        Args:
            model_name: Sentence-transformers model name.
            lazy_load: If True, load model on first use.
        """
        self.model_name = model_name
        self._model: SentenceTransformer | None = None
        self._embeddings: np.ndarray | None = None
        self._metadata: list[dict] = []

        if not lazy_load:
            self._load_model()

    def _load_model(self) -> SentenceTransformer:
        """Load the sentence transformer model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as e:
                raise ImportError(
                    "sentence-transformers is required for semantic search. "
                    "Install with: pip install ifcraftcorpus[embeddings]"
                ) from e
            self._model = SentenceTransformer(self.model_name)
        return self._model

    @property
    def model(self) -> SentenceTransformer:
        """Get the sentence transformer model."""
        return self._load_model()

    def add_texts(
        self,
        texts: list[str],
        metadata: list[dict],
    ) -> None:
        """Add texts with metadata to the index.

        Args:
            texts: List of text strings to embed.
            metadata: List of metadata dicts (same length as texts).
        """
        if len(texts) != len(metadata):
            raise ValueError("texts and metadata must have same length")

        # Generate embeddings
        new_embeddings = self.model.encode(
            texts,
            show_progress_bar=False,
            convert_to_numpy=True,
        )

        # Append to existing
        if self._embeddings is None:
            self._embeddings = new_embeddings
        else:
            self._embeddings = np.vstack([self._embeddings, new_embeddings])

        self._metadata.extend(metadata)

    def search(
        self,
        query: str,
        *,
        top_k: int = 10,
        cluster: str | None = None,
    ) -> list[tuple[dict, float]]:
        """Search for similar texts.

        Args:
            query: Search query.
            top_k: Number of results to return.
            cluster: Optional cluster filter.

        Returns:
            List of (metadata, similarity_score) tuples.
        """
        if self._embeddings is None or len(self._metadata) == 0:
            return []

        # Encode query
        query_embedding = self.model.encode(
            query,
            show_progress_bar=False,
            convert_to_numpy=True,
        )

        # Compute cosine similarities
        # Normalize embeddings
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        embeddings_norm = self._embeddings / np.linalg.norm(self._embeddings, axis=1, keepdims=True)

        similarities = np.dot(embeddings_norm, query_norm)

        # Get top-k indices
        if cluster:
            # Filter by cluster
            mask = np.array([m.get("cluster") == cluster for m in self._metadata])
            filtered_similarities = np.where(mask, similarities, -np.inf)
            top_indices = np.argsort(filtered_similarities)[-top_k:][::-1]
        else:
            top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Skip filtered out results
                results.append((self._metadata[idx], float(similarities[idx])))

        return results

    def save(self, path: Path) -> None:
        """Save the embedding index to disk.

        Args:
            path: Directory path to save index.
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

        # Save embeddings
        if self._embeddings is not None:
            np.save(path / "embeddings.npy", self._embeddings)

        # Save metadata
        with open(path / "metadata.json", "w") as f:
            json.dump(
                {
                    "model_name": self.model_name,
                    "metadata": self._metadata,
                },
                f,
            )

    @classmethod
    def load(cls, path: Path) -> EmbeddingIndex:
        """Load an embedding index from disk.

        Args:
            path: Directory path containing saved index.

        Returns:
            Loaded EmbeddingIndex.
        """
        path = Path(path)

        # Load metadata
        with open(path / "metadata.json") as f:
            data = json.load(f)

        index = cls(model_name=data["model_name"])
        index._metadata = data["metadata"]

        # Load embeddings if they exist
        embeddings_path = path / "embeddings.npy"
        if embeddings_path.exists():
            index._embeddings = np.load(embeddings_path)

        return index

    def __len__(self) -> int:
        """Return number of indexed items."""
        return len(self._metadata)


def build_embeddings_from_index(
    corpus_index: CorpusIndex,
    model_name: str = DEFAULT_MODEL,
) -> EmbeddingIndex:
    """Build embedding index from a CorpusIndex.

    Args:
        corpus_index: Populated CorpusIndex.
        model_name: Sentence-transformers model name.

    Returns:
        EmbeddingIndex with all corpus content.
    """

    embedding_index = EmbeddingIndex(model_name)

    # Get all documents
    for doc_info in corpus_index.list_documents():
        doc = corpus_index.get_document(doc_info["name"])
        if not doc:
            continue

        # Add document summary
        embedding_index.add_texts(
            [doc["summary"]],
            [
                {
                    "document_name": doc["name"],
                    "title": doc["title"],
                    "cluster": doc["cluster"],
                    "section_heading": None,
                    "content": doc["summary"],
                    "topics": doc["topics"],
                }
            ],
        )

        # Add sections
        for section in doc["sections"]:
            if section["content"].strip():
                embedding_index.add_texts(
                    [section["content"]],
                    [
                        {
                            "document_name": doc["name"],
                            "title": doc["title"],
                            "cluster": doc["cluster"],
                            "section_heading": section["heading"],
                            "content": section["content"],
                            "topics": doc["topics"],
                        }
                    ],
                )

    return embedding_index
