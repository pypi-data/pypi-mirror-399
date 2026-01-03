"""
Unified search API for the IF Craft Corpus.

Provides a simple interface combining FTS5 keyword search
and optional semantic vector search.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from ifcraftcorpus.index import CorpusIndex


@dataclass
class CorpusResult:
    """A unified search result."""

    document_name: str
    title: str
    cluster: str
    section_heading: str | None
    content: str
    score: float
    topics: list[str]
    search_type: Literal["keyword", "semantic"]

    @property
    def source(self) -> str:
        """Human-readable source reference."""
        if self.section_heading:
            return f"{self.document_name} > {self.section_heading}"
        return self.document_name


class Corpus:
    """Main interface for searching the IF Craft Corpus."""

    def __init__(
        self,
        *,
        corpus_dir: Path | None = None,
        index_path: Path | None = None,
        embeddings_path: Path | None = None,
        use_bundled: bool = True,
    ) -> None:
        """Initialize the corpus.

        Args:
            corpus_dir: Path to corpus markdown files. If None, uses bundled corpus.
            index_path: Path to pre-built SQLite index. If None, builds in-memory.
            embeddings_path: Path to pre-built embeddings. If None, semantic search disabled.
            use_bundled: If True and corpus_dir is None, use bundled corpus files.
        """
        self._corpus_dir = corpus_dir
        self._index_path = index_path
        self._embeddings_path = embeddings_path
        self._use_bundled = use_bundled

        self._fts_index: CorpusIndex | None = None
        self._embedding_index = None  # Lazy loaded

    def _get_corpus_dir(self) -> Path:
        """Get the corpus directory path."""
        if self._corpus_dir:
            return self._corpus_dir

        if self._use_bundled:
            # Try to find bundled corpus
            try:
                import sys

                import ifcraftcorpus

                # Check for installed shared data (pip install)
                bundled = Path(sys.prefix) / "share" / "ifcraftcorpus" / "corpus"
                if bundled.exists():
                    return bundled

                # Check relative to package (development mode / editable install)
                pkg_dir = Path(ifcraftcorpus.__file__).parent
                dev_corpus = pkg_dir.parent.parent / "corpus"
                if dev_corpus.exists():
                    return dev_corpus
            except Exception:
                pass

        raise ValueError(
            "No corpus directory found. Provide corpus_dir or install package with bundled corpus."
        )

    def _get_fts_index(self) -> CorpusIndex:
        """Get or create the FTS index."""
        if self._fts_index is None:
            if self._index_path and self._index_path.exists():
                self._fts_index = CorpusIndex(self._index_path)
            else:
                # Build in-memory index
                self._fts_index = CorpusIndex()
                corpus_dir = self._get_corpus_dir()
                self._fts_index.build_from_directory(corpus_dir)
        return self._fts_index

    def _get_embedding_index(self):
        """Get the embedding index (lazy loaded)."""
        if self._embedding_index is None and self._embeddings_path:
            try:
                from ifcraftcorpus.embeddings import EmbeddingIndex

                if self._embeddings_path.exists():
                    self._embedding_index = EmbeddingIndex.load(self._embeddings_path)
            except ImportError:
                pass  # embeddings not available
        return self._embedding_index

    def search(
        self,
        query: str,
        *,
        cluster: str | None = None,
        limit: int = 10,
        mode: Literal["keyword", "semantic", "hybrid"] = "keyword",
    ) -> list[CorpusResult]:
        """Search the corpus.

        Args:
            query: Search query.
            cluster: Optional cluster filter.
            limit: Maximum results to return.
            mode: Search mode - 'keyword' (FTS5), 'semantic' (vector), or 'hybrid'.

        Returns:
            List of CorpusResult objects.
        """
        results: list[CorpusResult] = []

        if mode in ("keyword", "hybrid"):
            fts_results = self._get_fts_index().search(query, cluster=cluster, limit=limit)
            for r in fts_results:
                results.append(
                    CorpusResult(
                        document_name=r.document_name,
                        title=r.title,
                        cluster=r.cluster,
                        section_heading=r.section_heading,
                        content=r.content,
                        score=r.score,
                        topics=r.topics,
                        search_type="keyword",
                    )
                )

        if mode in ("semantic", "hybrid"):
            embedding_index = self._get_embedding_index()
            if embedding_index:
                semantic_results = embedding_index.search(query, top_k=limit, cluster=cluster)
                for metadata, score in semantic_results:
                    results.append(
                        CorpusResult(
                            document_name=metadata["document_name"],
                            title=metadata["title"],
                            cluster=metadata["cluster"],
                            section_heading=metadata.get("section_heading"),
                            content=metadata["content"],
                            score=score,
                            topics=metadata.get("topics", []),
                            search_type="semantic",
                        )
                    )

        # Deduplicate and sort by score
        if mode == "hybrid":
            seen = set()
            unique_results = []
            for r in sorted(results, key=lambda x: x.score, reverse=True):
                key = (r.document_name, r.section_heading)
                if key not in seen:
                    seen.add(key)
                    unique_results.append(r)
            results = unique_results[:limit]

        return results

    def get_document(self, name: str) -> dict | None:
        """Get a document by name.

        Args:
            name: Document name (stem of filename).

        Returns:
            Document with title, summary, cluster, topics, and sections.
        """
        return self._get_fts_index().get_document(name)

    def list_documents(self) -> list[dict[str, str]]:
        """List all documents in the corpus.

        Returns:
            List of document metadata.
        """
        return self._get_fts_index().list_documents()

    def list_clusters(self) -> list[str]:
        """List all clusters.

        Returns:
            Sorted list of cluster names.
        """
        return self._get_fts_index().list_clusters()

    def document_count(self) -> int:
        """Get total number of documents."""
        return self._get_fts_index().document_count()

    @property
    def has_semantic_search(self) -> bool:
        """Check if semantic search is available."""
        return self._get_embedding_index() is not None

    def close(self) -> None:
        """Close resources."""
        if self._fts_index:
            self._fts_index.close()
            self._fts_index = None

    def __enter__(self) -> Corpus:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
