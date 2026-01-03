"""
MCP server for IF Craft Corpus.

Exposes corpus search as tools for LLM clients via FastMCP 2.
"""

from __future__ import annotations

from typing import Literal

from fastmcp import FastMCP

from ifcraftcorpus.search import Corpus

# Initialize FastMCP server
mcp = FastMCP(
    name="IF Craft Corpus",
    instructions="""
    This server provides access to the Interactive Fiction Craft Corpus,
    a curated knowledge base for writing interactive fiction. Use the tools
    to search for craft guidance on topics like narrative structure, dialogue,
    branching, prose style, and genre conventions.
    """,
)

# Global corpus instance (initialized on first use)
_corpus: Corpus | None = None


def get_corpus() -> Corpus:
    """Get or create the corpus instance."""
    global _corpus
    if _corpus is None:
        _corpus = Corpus()
    return _corpus


@mcp.tool
def search_corpus(
    query: str,
    cluster: str | None = None,
    limit: int = 5,
) -> list[dict]:
    """Search the IF Craft Corpus for writing guidance.

    Use this tool to find craft advice for interactive fiction writing,
    including narrative structure, dialogue, branching, prose style,
    worldbuilding, and genre conventions.

    Args:
        query: Search query describing what craft guidance you need.
               Examples: "dialogue subtext", "branching narrative",
               "pacing action scenes", "horror atmosphere".
        cluster: Optional topic cluster to filter by. Valid clusters:
                 narrative-structure, prose-and-language, genre-conventions,
                 audience-and-access, world-and-setting, emotional-design,
                 scope-and-planning, craft-foundations, agent-design, game-design.
        limit: Maximum number of results (1-20, default 5).

    Returns:
        List of relevant corpus passages with source references.
    """
    limit = max(1, min(20, limit))

    corpus = get_corpus()
    results = corpus.search(query, cluster=cluster, limit=limit)

    return [
        {
            "source": r.source,
            "title": r.title,
            "cluster": r.cluster,
            "content": r.content[:2000],  # Truncate for token efficiency
            "topics": r.topics,
        }
        for r in results
    ]


@mcp.tool
def get_document(name: str) -> dict | None:
    """Get a specific document from the IF Craft Corpus.

    Use this tool when you need the full content of a known document,
    rather than searching for relevant passages.

    Args:
        name: Document name (e.g., "dialogue_craft", "branching_narrative_construction").
              Use list_documents to discover available documents.

    Returns:
        Full document with title, summary, cluster, topics, and all sections.
    """
    corpus = get_corpus()
    return corpus.get_document(name)


@mcp.tool
def list_documents(cluster: str | None = None) -> list[dict]:
    """List all documents in the IF Craft Corpus.

    Use this tool to discover what craft guidance is available.

    Args:
        cluster: Optional cluster to filter by.

    Returns:
        List of documents with name, title, cluster, and topics.
    """
    corpus = get_corpus()
    docs = corpus.list_documents()

    if cluster:
        docs = [d for d in docs if d["cluster"] == cluster]

    return docs


@mcp.tool
def list_clusters() -> list[dict]:
    """List all topic clusters in the IF Craft Corpus.

    Each cluster groups related craft documents. Use this to understand
    the organization of the corpus.

    Returns:
        List of clusters with names and document counts.
    """
    corpus = get_corpus()
    clusters = corpus.list_clusters()
    docs = corpus.list_documents()

    # Count documents per cluster
    counts = {}
    for d in docs:
        c = d["cluster"]
        counts[c] = counts.get(c, 0) + 1

    return [{"name": c, "document_count": counts.get(c, 0)} for c in clusters]


@mcp.tool
def corpus_stats() -> dict:
    """Get statistics about the IF Craft Corpus.

    Returns:
        Statistics including document count, cluster count, and availability.
    """
    corpus = get_corpus()
    return {
        "document_count": corpus.document_count(),
        "cluster_count": len(corpus.list_clusters()),
        "clusters": corpus.list_clusters(),
        "semantic_search_available": corpus.has_semantic_search,
    }


def run_server(
    transport: Literal["stdio", "http"] = "stdio",
    host: str = "127.0.0.1",
    port: int = 8000,
) -> None:
    """Run the MCP server.

    Args:
        transport: Transport protocol ('stdio' or 'http').
        host: Host to bind to (for http transport).
        port: Port to bind to (for http transport).
    """
    if transport == "http":
        mcp.run(transport="http", host=host, port=port)
    else:
        mcp.run()


# Entry point for `uvx ifcraftcorpus-mcp` or `python -m ifcraftcorpus.mcp_server`
if __name__ == "__main__":
    mcp.run()
