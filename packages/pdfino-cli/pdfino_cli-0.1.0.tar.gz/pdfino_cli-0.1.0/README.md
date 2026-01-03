# pdfino

Convert `.ino` and `.py` files in the current directory into PDFs via Markdown + Pandoc.

> Note: if you are looking for the `pdfino` module that "wraps around ReportLab to simplify PDF document creation" then [this is where you want to go](https://pypi.org/project/pdfino/). My apologies for the name clash but I thought I had coined the name from PDF and Arduino and then became too invested in it.

## Install (global)

```sh
uv tool install pdfino-cli
```

## Use

```sh
cd /path/to/project
pdfino
```

One PDF is created per input file:

- `listing_demo.ino` -> `listing_demo.ino.pdf`
- `script.py` -> `script.py.pdf`

## Options

```sh
pdfino --help
```

## Examples:

```sh
pdfino -e .ino
pdfino -e py -o out_pdfs
pdfino --keep-md
pdfino --pdf-engine xelatex
```

---

## Step 5: Try it locally (developer loop)

From the project root:

```bash
uv venv
uv pip install -e .
pdfino --help
```

Then, in any folder with .ino or .py files:

```sh
cd /somewhere/with/files
pdfino
```

## Uninstall

If `pdfino` was installed as a global uv tool:

```sh
uv tool uninstall pdfino-cli
```

If you installed it from a local checkout and want to reinstall after changes:

```sh
uv tool uninstall pdfino-cli
uv tool install .
```

This removes the isolated tool environment and the pdfino command from your PATH.