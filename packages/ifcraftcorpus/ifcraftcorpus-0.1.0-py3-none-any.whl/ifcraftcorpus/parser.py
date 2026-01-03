"""
Corpus file parser.

Extracts YAML frontmatter and markdown sections from corpus files.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# Regex patterns
FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
HEADING_PATTERN = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)

# Valid cluster names
VALID_CLUSTERS = frozenset(
    {
        "narrative-structure",
        "prose-and-language",
        "genre-conventions",
        "audience-and-access",
        "world-and-setting",
        "emotional-design",
        "scope-and-planning",
        "craft-foundations",
        "agent-design",
        "game-design",
    }
)


@dataclass
class Section:
    """A section extracted from a corpus file."""

    heading: str
    level: int  # 1=H1, 2=H2, 3=H3
    content: str
    line_start: int = 0

    def __post_init__(self) -> None:
        self.content = self.content.strip()


@dataclass
class Document:
    """A parsed corpus document with frontmatter and sections."""

    path: Path
    title: str
    summary: str
    topics: list[str]
    cluster: str
    sections: list[Section] = field(default_factory=list)
    content_hash: str = ""
    raw_content: str = ""

    @property
    def name(self) -> str:
        """Document name without extension."""
        return self.path.stem

    def validate(self) -> list[str]:
        """Validate document, return list of errors."""
        errors = []

        if not self.title:
            errors.append("Missing required field: title")
        elif len(self.title) < 5:
            errors.append(f"Title too short (min 5 chars): {len(self.title)}")

        if not self.summary:
            errors.append("Missing required field: summary")
        elif len(self.summary) < 20:
            errors.append(f"Summary too short (min 20 chars): {len(self.summary)}")
        elif len(self.summary) > 300:
            errors.append(f"Summary too long (max 300 chars): {len(self.summary)}")

        if not self.topics:
            errors.append("Missing required field: topics")
        elif len(self.topics) < 3:
            errors.append(f"Too few topics (min 3): {len(self.topics)}")

        if not self.cluster:
            errors.append("Missing required field: cluster")
        elif self.cluster not in VALID_CLUSTERS:
            errors.append(f"Invalid cluster '{self.cluster}', must be one of: {VALID_CLUSTERS}")

        return errors


def parse_file(path: Path) -> Document:
    """Parse a corpus markdown file.

    Args:
        path: Path to the markdown file.

    Returns:
        Parsed Document with frontmatter and sections.

    Raises:
        ValueError: If file cannot be parsed.
    """
    content = path.read_text(encoding="utf-8")
    content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

    # Extract frontmatter
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        raise ValueError(f"No valid frontmatter found in {path}")

    try:
        frontmatter_data: dict[str, Any] = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in frontmatter of {path}: {e}") from e

    # Body content after frontmatter
    body = content[match.end() :]

    # Extract sections
    sections = _extract_sections(body)

    return Document(
        path=path,
        title=frontmatter_data.get("title", ""),
        summary=frontmatter_data.get("summary", ""),
        topics=frontmatter_data.get("topics", []),
        cluster=frontmatter_data.get("cluster", ""),
        sections=sections,
        content_hash=content_hash,
        raw_content=content,
    )


def _extract_sections(content: str) -> list[Section]:
    """Extract heading-based sections from markdown content."""
    sections: list[Section] = []
    lines = content.split("\n")

    # Find all heading positions
    heading_positions: list[tuple[int, int, str]] = []  # (line_num, level, heading)

    for i, line in enumerate(lines):
        match = HEADING_PATTERN.match(line)
        if match:
            level = len(match.group(1))
            heading = match.group(2).strip()
            heading_positions.append((i, level, heading))

    # Extract content between headings
    for idx, (line_num, level, heading) in enumerate(heading_positions):
        # Find end of this section (next heading of same or higher level, or end)
        end_line = len(lines)
        for next_line, next_level, _ in heading_positions[idx + 1 :]:
            if next_level <= level:
                end_line = next_line
                break
        else:
            # No higher-level heading found, check for any heading
            if idx + 1 < len(heading_positions):
                end_line = heading_positions[idx + 1][0]

        # Extract section content (excluding the heading line itself)
        section_lines = lines[line_num + 1 : end_line]
        section_content = "\n".join(section_lines).strip()

        sections.append(
            Section(
                heading=heading,
                level=level,
                content=section_content,
                line_start=line_num + 1,  # 1-indexed
            )
        )

    return sections


def parse_directory(corpus_dir: Path) -> list[Document]:
    """Parse all markdown files in a corpus directory.

    Args:
        corpus_dir: Path to corpus directory (searches recursively).

    Returns:
        List of parsed Documents.
    """
    documents = []
    for md_path in sorted(corpus_dir.rglob("*.md")):
        try:
            doc = parse_file(md_path)
            documents.append(doc)
        except ValueError:
            # Skip files that can't be parsed
            continue
    return documents
