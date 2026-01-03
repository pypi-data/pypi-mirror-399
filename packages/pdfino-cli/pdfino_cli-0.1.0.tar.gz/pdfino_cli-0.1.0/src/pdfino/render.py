from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RenderedMarkdown:
    markdown_text: str


def render_markdown_for_file(path: Path, language: str) -> RenderedMarkdown:
    """
    Render one file into a Markdown document containing a title and a fenced code block.
    """
    content = path.read_text(encoding="utf-8", errors="strict")
    if not content.endswith("\n"):
        content += "\n"

    md = []
    md.append(f"## {path.name}\n")
    md.append(f"```{language}\n")
    md.append(content)
    md.append("```\n")
    return RenderedMarkdown(markdown_text="".join(md))
