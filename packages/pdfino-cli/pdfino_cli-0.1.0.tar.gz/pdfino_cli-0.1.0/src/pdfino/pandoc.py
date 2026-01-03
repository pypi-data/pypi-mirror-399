from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PandocResult:
    output_pdf: Path


class PandocNotFoundError(RuntimeError):
    pass


class PandocFailedError(RuntimeError):
    def __init__(self, message: str, returncode: int, stderr: str | None):
        super().__init__(message)
        self.returncode = returncode
        self.stderr = stderr


def ensure_pandoc_available() -> None:
    if shutil.which("pandoc") is None:
        raise PandocNotFoundError(
            "pandoc not found on PATH. Install pandoc and ensure it is available as 'pandoc'."
        )


def run_pandoc(
    input_md: Path,
    output_pdf: Path,
    pdf_engine: str = "pdflatex",
    debug: bool = False,
) -> PandocResult:
    ensure_pandoc_available()

    cmd = [
        "pandoc",
        str(input_md),
        "--from",
        "markdown",
        "--pdf-engine",
        pdf_engine,
        "--output",
        str(output_pdf),
    ]

    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if proc.returncode != 0:
        msg = f"pandoc failed (exit {proc.returncode}) while producing {output_pdf.name}"
        if debug and proc.stderr:
            msg += f"\n\npandoc stderr:\n{proc.stderr}"
        raise PandocFailedError(msg, proc.returncode, proc.stderr)

    return PandocResult(output_pdf=output_pdf)
