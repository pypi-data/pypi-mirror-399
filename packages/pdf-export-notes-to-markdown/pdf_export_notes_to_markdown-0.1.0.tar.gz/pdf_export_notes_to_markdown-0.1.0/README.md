## pdf_export_notes_to_markdown

This program extracts annotations from PDF files using [PyMuPDF](https://github.com/pymupdf/pymupdf).

code from chatgpt.

## Installation

```shell
pip install pdf_export_notes_to_markdown
```

## Usage

```shell
# input_number: Defaults to 1
pdf_export_notes_to_markdown pdf_files

# if chapter == "9.6. 私有变量":
#     number_of("#")  = input_number + number_of(".")  # chapter in md will be "### 📘 9.6. 私有变量"
```