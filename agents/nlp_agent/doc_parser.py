"""Technical document parser for NLP."""
from __future__ import annotations

import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class DocSection:
    """A parsed section of a document."""
    section_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    heading: str = ""
    level: int = 1
    content: str = ""
    subsections: List["DocSection"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeBlock:
    """A code block extracted from a document."""
    language: str = ""
    code: str = ""
    line_start: int = 0
    line_end: int = 0


@dataclass
class ParsedDocument:
    """Fully parsed document structure."""
    doc_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    doc_type: str = "unknown"   # "markdown" | "rst" | "text" | "yaml" | "json" | "log"
    sections: List[DocSection] = field(default_factory=list)
    code_blocks: List[CodeBlock] = field(default_factory=list)
    tables: List[List[List[str]]] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    word_count: int = 0
    parsed_at: datetime = field(default_factory=datetime.utcnow)


def _count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def _extract_links(text: str) -> List[str]:
    return re.findall(r"https?://[^\s\)\"'>]+", text)


def _extract_code_blocks_markdown(text: str) -> Tuple[List[CodeBlock], str]:
    blocks: List[CodeBlock] = []
    lines = text.split("\n")
    cleaned_lines: List[str] = []
    in_block = False
    language = ""
    block_lines: List[str] = []
    start_line = 0

    for i, line in enumerate(lines):
        if not in_block and re.match(r"^```(\w*)", line):
            in_block = True
            language = re.match(r"^```(\w*)", line).group(1) or "text"
            block_lines = []
            start_line = i
        elif in_block and line.strip() == "```":
            blocks.append(CodeBlock(language=language, code="\n".join(block_lines),
                                    line_start=start_line, line_end=i))
            in_block = False
            block_lines = []
        elif in_block:
            block_lines.append(line)
        else:
            cleaned_lines.append(line)

    return blocks, "\n".join(cleaned_lines)


def _parse_markdown_sections(text: str) -> Tuple[str, List[DocSection]]:
    lines = text.split("\n")
    title = ""
    sections: List[DocSection] = []
    current_section: Optional[DocSection] = None
    current_content: List[str] = []

    for line in lines:
        heading_match = re.match(r"^(#{1,6})\s+(.+)", line)
        if heading_match:
            if current_section:
                current_section.content = "\n".join(current_content).strip()
                sections.append(current_section)
            level = len(heading_match.group(1))
            heading = heading_match.group(2).strip()
            if level == 1 and not title:
                title = heading
            current_section = DocSection(heading=heading, level=level)
            current_content = []
        else:
            current_content.append(line)

    if current_section:
        current_section.content = "\n".join(current_content).strip()
        sections.append(current_section)

    return title, sections


def _parse_markdown_tables(text: str) -> List[List[List[str]]]:
    tables: List[List[List[str]]] = []
    lines = text.split("\n")
    table_lines: List[str] = []
    in_table = False

    for line in lines:
        if re.match(r"^\|.+\|", line):
            in_table = True
            if not re.match(r"^\|[-| ]+\|", line):
                table_lines.append(line)
        else:
            if in_table and table_lines:
                table = [[cell.strip() for cell in row.strip("|").split("|")]
                         for row in table_lines]
                tables.append(table)
                table_lines = []
            in_table = False

    if in_table and table_lines:
        tables.append([[cell.strip() for cell in row.strip("|").split("|")]
                       for row in table_lines])
    return tables


def _parse_log_document(text: str) -> List[DocSection]:
    patterns = {
        "ERROR": re.compile(r"\b(ERROR|CRITICAL|FATAL)\b"),
        "WARNING": re.compile(r"\bWARN(?:ING)?\b"),
        "INFO": re.compile(r"\bINFO\b"),
    }
    sections: List[DocSection] = []
    for level, pattern in patterns.items():
        matching_lines = [line for line in text.split("\n") if pattern.search(line)]
        if matching_lines:
            sections.append(DocSection(
                heading=f"{level} Log Entries",
                level=2,
                content="\n".join(matching_lines[:50]),
                metadata={"entry_count": len(matching_lines), "level": level},
            ))
    return sections


def _detect_doc_type(text: str) -> str:
    text_strip = text.strip()
    if text_strip.startswith("#") or re.search(r"^#{1,6}\s", text_strip, re.MULTILINE):
        return "markdown"
    if re.match(r"^[-=]+\n", text_strip) or re.search(r"\n[-=]+\n", text_strip):
        return "rst"
    if re.search(r"^\s*[\{\[]", text_strip):
        return "json"
    if re.match(r"^\w+:", text_strip) or re.search(r"\n\w+:", text_strip):
        return "yaml"
    if re.search(r"\b(ERROR|WARN|INFO|DEBUG)\b", text_strip):
        return "log"
    return "text"


class DocParser:
    """
    Technical document parser supporting Markdown, RST, logs,
    YAML, JSON, and plain text with section extraction, code blocks,
    tables, and link detection.
    """

    def __init__(self) -> None:
        self._custom_extractors: List[Any] = []
        logger.info("DocParser initialized")

    def parse(self, text: str, doc_type: Optional[str] = None) -> ParsedDocument:
        if not text.strip():
            return ParsedDocument(doc_type="empty", word_count=0)

        detected_type = doc_type or _detect_doc_type(text)
        code_blocks: List[CodeBlock] = []
        sections: List[DocSection] = []
        tables: List[List[List[str]]] = []
        title = ""

        if detected_type == "markdown":
            code_blocks, clean_text = _extract_code_blocks_markdown(text)
            tables = _parse_markdown_tables(clean_text)
            title, sections = _parse_markdown_sections(clean_text)
        elif detected_type == "log":
            sections = _parse_log_document(text)
            clean_text = text
        elif detected_type in ("yaml", "json"):
            sections = [DocSection(heading="Content", level=1, content=text)]
            clean_text = text
        else:
            paragraphs = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
            sections = [DocSection(heading=f"Section {i+1}", level=1, content=p)
                        for i, p in enumerate(paragraphs)]
            clean_text = text

        links = _extract_links(text)
        word_count = _count_words(text)

        doc = ParsedDocument(
            title=title or "Untitled",
            doc_type=detected_type,
            sections=sections,
            code_blocks=code_blocks,
            tables=tables,
            links=links,
            word_count=word_count,
            metadata={
                "char_count": len(text),
                "section_count": len(sections),
                "code_block_count": len(code_blocks),
                "table_count": len(tables),
                "link_count": len(links),
            },
        )
        logger.debug("Parsed %s document: %d sections, %d code blocks",
                     detected_type, len(sections), len(code_blocks))
        return doc

    def extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract key-value metadata from YAML frontmatter or header comments."""
        metadata: Dict[str, Any] = {}
        frontmatter_match = re.match(r"^---\n(.+?)\n---", text, re.DOTALL)
        if frontmatter_match:
            for line in frontmatter_match.group(1).split("\n"):
                kv = re.match(r"(\w+):\s*(.+)", line)
                if kv:
                    metadata[kv.group(1)] = kv.group(2).strip()
        return metadata

    def batch_parse(self, texts: List[str]) -> List[ParsedDocument]:
        return [self.parse(t) for t in texts]

    def to_plain_text(self, doc: ParsedDocument) -> str:
        parts = [doc.title] if doc.title and doc.title != "Untitled" else []
        for section in doc.sections:
            parts.append(f"\n{section.heading}\n{section.content}")
        return "\n".join(parts)
