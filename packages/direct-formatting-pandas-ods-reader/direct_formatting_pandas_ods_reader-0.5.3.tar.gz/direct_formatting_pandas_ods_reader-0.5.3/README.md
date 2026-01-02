# direct-formatting-pandas-ods-reader


[![pipeline status](https://gitlab.com/yanntrividic/direct-formatting-pandas-ods-reader/badges/main/pipeline.svg)](https://gitlab.com/yanntrividic/direct-formatting-pandas-ods-reader/-/commits/main) 


Inspired from [pandas-ods-reader](https://github.com/iuvbio/pandas_ods_reader), but with the ability to read direct formatting. pandas-ods-reader relies on [ezodf](https://pypi.org/project/ezodf/) to extract cell content, but ezodf ignores direct formatting, so we need to go at a lower level.

The direct (emphasis, strong, underline, subscript, superscript, and anchors) formatting is turned into markup in the resulting pandas DataFrame.

## Dependencies

* `lxml`
* `pandas`

## Usage


### In a Python project

```python
from direct_formatting_pandas_ods_reader import read_ods

# single global format
df = read_ods("test/test.ods")

df = read_ods("test/test.ods", format="markdown")

df = read_ods("test/test.ods", format="html", sheet=0)

# or per-column formats:
df = read_ods("test/test.ods", format={
    "Column 1": "markdown",
    "Column 3": "html"
})
```

The `format` argument can be:

1. `"html"`, `"markdown"`, `"asciidoc"` or `"none"` (global format for all columns),
2. or a dict mapping column labels to formats (unspecified column labels to `"none"`)

`sheet_index` defaults to `0`, which corresponds to the first sheet of the file.

### Command-line usage

You can use this package as a CLI tool:

```bash
python -m direct_formatting_pandas_ods_reader input.ods -o output.csv -t html
```

* `input.ods` path to the ODS file (required).
* `-o`, `--output` output CSV file (if omitted, writes to standard output).
* `-t`, `--type` output format for formatting marks (asciidoc, markdown, html). Defaults to asciidoc.
* `-s`, `--sheet` index of the sheet to read (0-based, default: 0).

### Install as a global CLI tool

```bash
pip install -e .
```

This creates a global `direct-formatting-ods-to-csv` command:

```bash
direct-formatting-ods-to-csv input.ods -t markdown
```

## License

Licensed under the GNU GPL v3.0, [Yann Trividic](https://yanntrividic.fr).