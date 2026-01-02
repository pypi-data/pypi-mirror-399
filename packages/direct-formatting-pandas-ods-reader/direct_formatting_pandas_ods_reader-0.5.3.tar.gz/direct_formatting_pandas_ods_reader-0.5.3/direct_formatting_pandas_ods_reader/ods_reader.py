# direct_formatting_pandas_ods_reader/ods_reader.py
"""
High-level ODS reader that returns a pandas.DataFrame.
Converts direct formatting (strong/emphasis/underline) to AsciiDoc markup.
"""

import pandas as pd
from .xml_utils import *

def read_ods(path, sheet_index=0, format="asciidoc"):
    """
    Read the ODS at `path` and return a pandas DataFrame for the sheet at `sheet_index`.

    `format` can be:
        * one of the strings in DEFAULT_FORMAT_MAPS (asciidoc/markdown/html)
        * the string "none" (no formatting)
        * a dict mapping column labels -> one of the above strings

    Returns:
        pandas.DataFrame
    """
    content_root, styles_root = extract_ods_xml(path)
    style_map = build_style_map(styles_root, content_root)

    tables = content_root.xpath("//table:table", namespaces=NS)
    if not tables:
        raise ValueError("No tables found in content.xml")

    if sheet_index < 0 or sheet_index >= len(tables):
        raise IndexError("sheet_index out of range")

    table_elem = tables[sheet_index]

    if isinstance(format, str):
        fmt = format.lower()
        if fmt == "none":
            fmt_map = None
            column_formats = None
        else:
            if fmt not in DEFAULT_FORMAT_MAPS:
                raise ValueError(
                    f"Invalid format '{format}'. Valid options: {list(DEFAULT_FORMAT_MAPS.keys()) + ['none']}"
                )
            fmt_map = DEFAULT_FORMAT_MAPS[fmt]
            column_formats = None
    elif isinstance(format, dict):
        fmt_map = None
        column_formats = format
    else:
        raise ValueError("format must be a string or a dict")

    rows = extract_cells_with_formatting(table_elem, style_map, fmt_map=fmt_map, column_formats=column_formats)

    max_cols = max((len(r) for r in rows), default=0)
    normalized = []
    for r in rows:
        if len(r) < max_cols:
            r = r + [""] * (max_cols - len(r))
        normalized.append(r)

    df = pd.DataFrame(normalized)
    df.columns = df.iloc[0]    # set headers to first row
    df = df[1:].reset_index(drop=True)  # drop the old header row
    return df