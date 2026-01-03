"""
IF Craft Corpus - A curated knowledge base for interactive fiction writing craft.

Quick start:
    >>> from ifcraftcorpus import Corpus
    >>> corpus = Corpus()
    >>> results = corpus.search("dialogue subtext techniques")
    >>> for r in results:
    ...     print(f"{r.source}: {r.content[:100]}...")
"""

from ifcraftcorpus.index import CorpusIndex, SearchResult, build_index
from ifcraftcorpus.parser import Document, Section, parse_directory, parse_file
from ifcraftcorpus.search import Corpus, CorpusResult

__version__ = "0.1.1"

__all__ = [
    # Main API
    "Corpus",
    "CorpusResult",
    # Parser
    "Document",
    "Section",
    "parse_file",
    "parse_directory",
    # Index
    "CorpusIndex",
    "SearchResult",
    "build_index",
    # Version
    "__version__",
]
