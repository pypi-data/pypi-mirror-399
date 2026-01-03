"""
SQLite FTS5 full-text search index.

Provides fast keyword-based search across the corpus.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from ifcraftcorpus.parser import Document, parse_directory


@dataclass
class SearchResult:
    """A search result from the corpus index."""

    document_name: str
    title: str
    cluster: str
    section_heading: str | None
    content: str
    score: float
    topics: list[str]

    @property
    def source(self) -> str:
        """Human-readable source reference."""
        if self.section_heading:
            return f"{self.document_name} > {self.section_heading}"
        return self.document_name


class CorpusIndex:
    """SQLite FTS5 index for corpus search."""

    SCHEMA = """
    -- Documents table
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        path TEXT NOT NULL,
        title TEXT NOT NULL,
        summary TEXT NOT NULL,
        cluster TEXT NOT NULL,
        topics TEXT NOT NULL,
        content_hash TEXT NOT NULL
    );

    -- Sections table
    CREATE TABLE IF NOT EXISTS sections (
        id INTEGER PRIMARY KEY,
        document_id INTEGER NOT NULL,
        heading TEXT NOT NULL,
        level INTEGER NOT NULL,
        content TEXT NOT NULL,
        line_start INTEGER NOT NULL,
        FOREIGN KEY (document_id) REFERENCES documents(id)
    );

    -- FTS5 virtual table for full-text search
    CREATE VIRTUAL TABLE IF NOT EXISTS corpus_fts USING fts5(
        document_name,
        title,
        cluster,
        topics,
        section_heading,
        content,
        tokenize='porter unicode61'
    );
    """

    def __init__(self, db_path: Path | str = ":memory:") -> None:
        """Initialize the corpus index.

        Args:
            db_path: Path to SQLite database file, or ':memory:' for in-memory.
        """
        self.db_path = Path(db_path) if db_path != ":memory:" else db_path
        self._conn: sqlite3.Connection | None = None

    @property
    def conn(self) -> sqlite3.Connection:
        """Get or create the database connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(
                str(self.db_path) if isinstance(self.db_path, Path) else self.db_path
            )
            self._conn.row_factory = sqlite3.Row
            self._init_schema()
        return self._conn

    def _init_schema(self) -> None:
        """Initialize database schema."""
        self.conn.executescript(self.SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> CorpusIndex:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def add_document(self, doc: Document) -> int:
        """Add a document to the index.

        Args:
            doc: Parsed Document to add.

        Returns:
            The document ID in the database.
        """
        cursor = self.conn.cursor()

        # Insert or replace document
        cursor.execute(
            """
            INSERT OR REPLACE INTO documents
            (name, path, title, summary, cluster, topics, content_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                doc.name,
                str(doc.path),
                doc.title,
                doc.summary,
                doc.cluster,
                ",".join(doc.topics),
                doc.content_hash,
            ),
        )
        doc_id = cursor.lastrowid
        assert doc_id is not None

        # Delete old sections
        cursor.execute("DELETE FROM sections WHERE document_id = ?", (doc_id,))

        # Insert sections
        for section in doc.sections:
            cursor.execute(
                """
                INSERT INTO sections (document_id, heading, level, content, line_start)
                VALUES (?, ?, ?, ?, ?)
                """,
                (doc_id, section.heading, section.level, section.content, section.line_start),
            )

            # Add to FTS index
            cursor.execute(
                """
                INSERT INTO corpus_fts
                (document_name, title, cluster, topics, section_heading, content)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    doc.name,
                    doc.title,
                    doc.cluster,
                    " ".join(doc.topics),
                    section.heading,
                    section.content,
                ),
            )

        # Also index the document summary
        cursor.execute(
            """
            INSERT INTO corpus_fts
            (document_name, title, cluster, topics, section_heading, content)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                doc.name,
                doc.title,
                doc.cluster,
                " ".join(doc.topics),
                None,
                doc.summary,
            ),
        )

        self.conn.commit()
        return doc_id

    def build_from_directory(self, corpus_dir: Path) -> int:
        """Build index from a corpus directory.

        Args:
            corpus_dir: Path to corpus directory.

        Returns:
            Number of documents indexed.
        """
        documents = parse_directory(corpus_dir)
        for doc in documents:
            self.add_document(doc)
        return len(documents)

    def search(
        self,
        query: str,
        *,
        cluster: str | None = None,
        limit: int = 10,
    ) -> list[SearchResult]:
        """Search the corpus.

        Args:
            query: Search query (FTS5 syntax supported).
            cluster: Optional cluster filter.
            limit: Maximum results to return.

        Returns:
            List of SearchResult objects, ranked by relevance.
        """
        # Build FTS5 query
        fts_query = query

        # Add cluster filter if specified
        where_clause = ""
        params: list[str | int] = [fts_query]
        if cluster:
            where_clause = "AND cluster = ?"
            params.append(cluster)
        params.append(limit)

        cursor = self.conn.execute(
            f"""
            SELECT
                document_name,
                title,
                cluster,
                topics,
                section_heading,
                content,
                bm25(corpus_fts) as score
            FROM corpus_fts
            WHERE corpus_fts MATCH ?
            {where_clause}
            ORDER BY score
            LIMIT ?
            """,
            params,
        )

        results = []
        for row in cursor:
            topics = row["topics"].split() if row["topics"] else []
            results.append(
                SearchResult(
                    document_name=row["document_name"],
                    title=row["title"],
                    cluster=row["cluster"],
                    section_heading=row["section_heading"],
                    content=row["content"],
                    score=abs(row["score"]),  # bm25 returns negative scores
                    topics=topics,
                )
            )

        return results

    def list_documents(self) -> list[dict[str, str]]:
        """List all indexed documents.

        Returns:
            List of document metadata dicts.
        """
        cursor = self.conn.execute(
            "SELECT name, title, cluster, topics FROM documents ORDER BY cluster, name"
        )
        return [
            {
                "name": row["name"],
                "title": row["title"],
                "cluster": row["cluster"],
                "topics": row["topics"].split(","),
            }
            for row in cursor
        ]

    def list_clusters(self) -> list[str]:
        """List all clusters in the index.

        Returns:
            Sorted list of cluster names.
        """
        cursor = self.conn.execute("SELECT DISTINCT cluster FROM documents ORDER BY cluster")
        return [row["cluster"] for row in cursor]

    def get_document(self, name: str) -> dict | None:
        """Get a document by name.

        Args:
            name: Document name (stem of filename).

        Returns:
            Document metadata and sections, or None if not found.
        """
        cursor = self.conn.execute(
            """
            SELECT id, name, path, title, summary, cluster, topics
            FROM documents WHERE name = ?
            """,
            (name,),
        )
        row = cursor.fetchone()
        if not row:
            return None

        sections_cursor = self.conn.execute(
            """
            SELECT heading, level, content, line_start
            FROM sections WHERE document_id = ?
            ORDER BY line_start
            """,
            (row["id"],),
        )

        return {
            "name": row["name"],
            "path": row["path"],
            "title": row["title"],
            "summary": row["summary"],
            "cluster": row["cluster"],
            "topics": row["topics"].split(","),
            "sections": [
                {
                    "heading": s["heading"],
                    "level": s["level"],
                    "content": s["content"],
                    "line_start": s["line_start"],
                }
                for s in sections_cursor
            ],
        }

    def document_count(self) -> int:
        """Get the number of indexed documents."""
        cursor = self.conn.execute("SELECT COUNT(*) FROM documents")
        return cursor.fetchone()[0]


def build_index(corpus_dir: Path, output_path: Path) -> CorpusIndex:
    """Build a corpus index and save to file.

    Args:
        corpus_dir: Path to corpus directory.
        output_path: Path for output SQLite database.

    Returns:
        The built CorpusIndex.
    """
    index = CorpusIndex(output_path)
    index.build_from_directory(corpus_dir)
    return index
