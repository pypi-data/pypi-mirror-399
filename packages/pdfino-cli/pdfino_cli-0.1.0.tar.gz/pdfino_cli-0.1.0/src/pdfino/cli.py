from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from pdfino import __version__
from pdfino.discover import discover_sources
from pdfino.render import render_markdown_for_file
from pdfino.pandoc import PandocFailedError, PandocNotFoundError, run_pandoc


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pdfino",
        description=(
            "Convert source files in the current directory into PDFs by wrapping them in "
            "Markdown code blocks and calling Pandoc.\n\n"
            "Each input file produces one PDF named <filename>.<ext>.pdf."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    p.add_argument(
        "-e",
        "--ext",
        action="append",
        default=[],
        help=(
            "include only files with this extension (may be repeated; default: .ino, .py)\n"
            "examples: -e .ino  |  -e py"
        ),
    )
    p.add_argument(
        "-o",
        "--output",
        type=str,
        default=".",
        help="output directory (default: current)",
    )
    p.add_argument(
        "--keep-md",
        action="store_true",
        help="keep generated Markdown files (written next to the PDF)",
    )
    p.add_argument(
        "--pdf-engine",
        type=str,
        default="pdflatex",
        help="Pandoc PDF engine (default: pdflatex)",
    )
    p.add_argument(
        "--debug",
        action="store_true",
        help="enable verbose error output",
    )
    p.add_argument(
        "--version",
        action="version",
        version=f"pdfino {__version__}",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    cwd = Path.cwd()
    out_dir = Path(args.output).expanduser().resolve()

    exts = args.ext if args.ext else None

    try:
        sources = discover_sources(cwd, exts=exts)
        if not sources:
            exts_display = ", ".join(args.ext) if args.ext else ".ino, .py"
            print(f"No matching files found in {cwd} for extensions: {exts_display}", file=sys.stderr)
            return 2

        out_dir.mkdir(parents=True, exist_ok=True)

        for src in sources:
            md = render_markdown_for_file(src.path, src.language)

            output_pdf = out_dir / f"{src.path.name}.pdf"  # e.g. listing_demo.ino.pdf

            if args.keep_md:
                md_path = out_dir / f"{src.path.name}.md"
                md_path.write_text(md.markdown_text, encoding="utf-8")
                run_pandoc(md_path, output_pdf, pdf_engine=args.pdf_engine, debug=args.debug)
            else:
                with tempfile.TemporaryDirectory(prefix="pdfino_") as td:
                    md_path = Path(td) / f"{src.path.name}.md"
                    md_path.write_text(md.markdown_text, encoding="utf-8")
                    run_pandoc(md_path, output_pdf, pdf_engine=args.pdf_engine, debug=args.debug)

            print(f"created {output_pdf}")

        return 0

    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2
    except PandocNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 127
    except PandocFailedError as e:
        print(str(e), file=sys.stderr)
        return 1
    except UnicodeDecodeError as e:
        if args.debug:
            raise
        print(f"Failed to read a file as UTF-8: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
