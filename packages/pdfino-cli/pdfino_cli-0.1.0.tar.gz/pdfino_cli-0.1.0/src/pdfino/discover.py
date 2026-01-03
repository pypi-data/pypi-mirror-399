from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class SourceFile:
    path: Path
    language: str


DEFAULT_EXT_TO_LANG = {
    ".ino": "cpp",
    ".py": "python",
}


def discover_sources(
    directory: Path,
    exts: Iterable[str] | None = None,
    ext_to_lang: dict[str, str] | None = None,
) -> list[SourceFile]:
    """
    Discover source files in `directory` (non-recursive), returning sorted SourceFile objects.
    Hidden files are ignored.
    """
    ext_to_lang = ext_to_lang or DEFAULT_EXT_TO_LANG
    allowed_exts = set(exts) if exts is not None else set(ext_to_lang.keys())

    # normalise extensions to include leading dot
    normalised_exts: set[str] = set()
    for e in allowed_exts:
        e = e.strip()
        if not e:
            continue
        if not e.startswith("."):
            e = "." + e
        normalised_exts.add(e)

    sources: list[SourceFile] = []
    for p in directory.iterdir():
        if not p.is_file():
            continue
        if p.name.startswith("."):
            continue
        if p.suffix not in normalised_exts:
            continue
        lang = ext_to_lang.get(p.suffix)
        if lang is None:
            # extension requested but not supported by mapping
            raise ValueError(f"Unsupported extension: {p.suffix} (no language mapping)")
        sources.append(SourceFile(path=p, language=lang))

    sources.sort(key=lambda s: s.path.name.lower())
    return sources
