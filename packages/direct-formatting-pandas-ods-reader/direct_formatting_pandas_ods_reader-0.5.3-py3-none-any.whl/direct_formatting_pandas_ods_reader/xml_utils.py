# direct_formatting_pandas_ods_reader/xml_utils.py
"""
Low-level ODS XML utilities:
- extract_ods_xml: read content.xml and styles.xml
- build_style_map: parse named styles + automatic styles (including table-cell family),
  resolve inheritance (parent-style-name)
- extract_cells_with_formatting: render table rows/cells into strings with AsciiDoc marks
"""

from lxml import etree
import zipfile

# ---------- Default text props ----------
DEFAULT_TEXT_PROPS = {
    "strong": False,
    "emphasis": False,
    "underline": False,
    "superscript": False,
    "subscript": False,
}

# ---------- Default format maps ----------
DEFAULT_FORMAT_MAPS = {
    "asciidoc": {
        "strong": ("**", "**"),
        "emphasis": ("__", "__"),
        "underline": ("[.underline]#", "#"),
        "superscript": ("^", "^"),
        "subscript": ("~", "~")
    },
    "markdown": {
        "strong": ("**", "**"),
        "emphasis": ("__", "__"),
        "underline": ("<u>", "</u>"),
        "superscript": ("<sup>", "</sup>"),
        "subscript": ("<sub>", "</sub>")
    },
    "html": {
        "strong": ("<strong>", "</strong>"),
        "emphasis": ("<em>", "</em>"),
        "underline": ("<u>", "</u>"),
        "superscript": ("<sup>", "</sup>"),
        "subscript": ("<sub>", "</sub>")
    },
}

# Namespaces commonly used in ODS files
NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
}

# ---------- XML extraction ----------
def extract_ods_xml(path):
    """
    Return (content_root, styles_root) parsed with lxml.
    Raises KeyError if the archive doesn't contain the expected files.
    """
    with zipfile.ZipFile(path, "r") as z:
        content_bytes = z.read("content.xml")
        # styles.xml may or may not exist (some ODS put everything in content.xml)
        styles_bytes = z.read("styles.xml") if "styles.xml" in z.namelist() else None

    parser = etree.XMLParser(ns_clean=True, recover=True)
    content_root = etree.fromstring(content_bytes, parser=parser)
    styles_root = etree.fromstring(styles_bytes, parser=parser) if styles_bytes is not None else None
    return content_root, styles_root

# ---------- Style parsing / helpers ----------
def _get_localname(qname):
    return etree.QName(qname).localname if qname is not None else None

def _extract_props_from_text_properties(text_properties_elem):
    """
    Inspect attributes of a <style:text-properties> element and infer
    strong/emphasis/underline/superscript/subscript booleans.
    """
    props = DEFAULT_TEXT_PROPS.copy()

    if text_properties_elem is None:
        return props

    for attr_name, attr_val in text_properties_elem.items():
        local = _get_localname(attr_name).lower()
        val_lower = (attr_val or "").lower()

        if "font-weight" in local:
            if val_lower == "bold":
                props["strong"] = True
        if "font-style" in local:
            if val_lower == "italic":
                props["emphasis"] = True
        if "text-underline-style" in local:
            if val_lower not in ("none", ""):
                props["underline"] = True
        if "text-position" in local:
            if val_lower.startswith("super"):
                props["superscript"] = True
            elif val_lower.startswith("sub"):
                props["subscript"] = True

    return props


def build_style_map(styles_root, content_root=None):
    """
    Build and return a dict mapping style-name -> {'strong':bool,'emphasis':bool,'underline':bool}.
    It parses:
      - styles from styles_root (styles.xml)
      - automatic styles in content_root (office:automatic-styles)
    Also resolves parent-style-name inheritance.
    """
    raw_props = {}    # name -> props (may be partial)
    parent_map = {}   # name -> parent_name (if any)

    def collect_from_root(root):
        if root is None:
            return
        # find all style:style elements under the given root
        for style_elem in root.xpath(".//style:style", namespaces=NS):
            name = style_elem.get(f"{{{NS['style']}}}name")
            if not name:
                continue
            # parent style name if present
            parent = style_elem.get(f"{{{NS['style']}}}parent-style-name")
            parent_map[name] = parent
            # text-properties can be present under different style families (text, table-cell, etc.)
            text_props_elem = style_elem.find("style:text-properties", namespaces=NS)
            props = _extract_props_from_text_properties(text_props_elem)
            # store (may be all false if nothing set)
            raw_props[name] = props

    # collect from styles.xml
    collect_from_root(styles_root)

    # collect automatic styles from content.xml
    if content_root is not None:
        # automatic styles are under office:automatic-styles
        autos = content_root.xpath("//office:automatic-styles", namespaces=NS)
        for auto in autos:
            collect_from_root(auto)

    # resolve inheritance: child's missing flags inherit from parent
    resolved = {}

    def resolve_style(name, seen=None):
        if name is None:
            return DEFAULT_TEXT_PROPS.copy()
        if name in resolved:
            return resolved[name]
        if seen is None:
            seen = set()
        if name in seen:
            # cycle, bail out
            resolved[name] = DEFAULT_TEXT_PROPS.copy()
            return resolved[name]
        seen.add(name)
        base = raw_props.get(name, DEFAULT_TEXT_PROPS.copy()).copy()
        parent = parent_map.get(name)
        if parent:
            parent_props = resolve_style(parent, seen)
            # inherit missing true attributes from parent
            for k in ("strong", "emphasis", "underline", "subscript", "superscript"):
                if not base.get(k) and parent_props.get(k):
                    base[k] = True
        resolved[name] = base
        return base

    # resolve all
    for style_name in set(list(raw_props.keys()) + list(parent_map.keys())):
        resolve_style(style_name)

    return resolved

def to_formatted_text(text, strong=False, emphasis=False, underline=False,
                      superscript=False, subscript=False, fmt_map=None):
    """
    Wrap text according to the given format map.
    Nesting order: emphasis -> strong -> underline -> super/sub.
    """
    if text is None:
        text = ""
    if not fmt_map:
        return text
    s = text
    if emphasis and "emphasis" in fmt_map:
        prefix, suffix = fmt_map["emphasis"]
        s = f"{prefix}{s}{suffix}"
    if strong and "strong" in fmt_map:
        prefix, suffix = fmt_map["strong"]
        s = f"{prefix}{s}{suffix}"
    if underline and "underline" in fmt_map:
        prefix, suffix = fmt_map["underline"]
        s = f"{prefix}{s}{suffix}"
    if superscript and "superscript" in fmt_map:
        prefix, suffix = fmt_map["superscript"]
        s = f"{prefix}{s}{suffix}"
    if subscript and "subscript" in fmt_map:
        prefix, suffix = fmt_map["subscript"]
        s = f"{prefix}{s}{suffix}"

    return s



# ---------- Render cells / nested spans ----------
def _merge_styles(base, override):
    """Return merged style dict (override wins)."""
    res = DEFAULT_TEXT_PROPS.copy()
    if base:
        res.update(base)
    if override:
        res.update(override)
    return res

# Modified _render_node_recursive to accept fmt_map
def _render_node_recursive(node, inherited_style, style_map, fmt_map=None):
    parts = []
    lead = node.text or ""
    if lead:
        parts.append(to_formatted_text(lead, **inherited_style, fmt_map=fmt_map))

    for child in node:
        tag_local = etree.QName(child.tag).localname
        if tag_local == "a" and fmt_map:  # handle hyperlink
            href = child.get("{http://www.w3.org/1999/xlink}href")
            child_style_name = child.get(f"{{{NS['text']}}}style-name")
            child_style = _merge_styles(inherited_style, style_map.get(child_style_name, {}))
            inner_text = _render_node_recursive(child, child_style, style_map, fmt_map)

            # choose format depending on fmt_map (or add a 'link' entry)
            # simplest: HTML always uses <a>, Asciidoc/Markdown become link[text]
            fmt = fmt_map.get("link", None) if fmt_map else None
            if fmt is not None:
                link_text = fmt.format(href=href, text=inner_text)
            else:
                if fmt_map is DEFAULT_FORMAT_MAPS["html"]:
                    link_text = f'<a href="{href}">{inner_text}</a>'
                elif fmt_map is DEFAULT_FORMAT_MAPS["markdown"]:
                    link_text = f'[{inner_text}]({href})'
                else:
                    link_text = f'{href}[{inner_text}]'
            parts.append(link_text)
            tail = child.tail or ""
            if tail:
                parts.append(to_formatted_text(tail, **inherited_style, fmt_map=fmt_map))
            continue
        child_style_name = child.get(f"{{{NS['text']}}}style-name")
        child_style = _merge_styles(inherited_style, style_map.get(child_style_name, {}))
        parts.append(_render_node_recursive(child, child_style, style_map, fmt_map))
        tail = child.tail or ""
        if tail:
            parts.append(to_formatted_text(tail, **inherited_style, fmt_map=fmt_map))

    return "".join(parts)

def extract_cells_with_formatting(table_elem, style_map, fmt_map=None, column_formats=None):
    """
    Extracts rows and cells from a <table:table> element, applying formatting
    according to the specified format map (AsciiDoc, Markdown, HTML).

    - Parses all columns that have a non-empty header.
    - Stops after the first completely empty row.
    - Empty cells in the middle are kept as empty strings.
    """
    rows_out = []
    empty_row_counter = 0

    row_elems = table_elem.xpath("./table:table-row", namespaces=NS)
    if not row_elems:
        return rows_out

    # --- Process header row ---
    header_elem = row_elems[0]
    header_cells = header_elem.xpath("./table:table-cell | ./table:covered-table-cell", namespaces=NS)
    header_row = []

    for cell_elem in header_cells:
        paragraphs = cell_elem.xpath("./text:p", namespaces=NS)
        cell_text = "\n".join(p.text or "" for p in paragraphs).strip()
        if not cell_text:
            break  # stop at first empty header cell
        col_repeat = int(cell_elem.get(f"{{{NS['table']}}}number-columns-repeated", "1"))
        for _ in range(col_repeat):
            header_row.append(cell_text)

    num_columns = len(header_row)
    if num_columns == 0:
        return rows_out
    rows_out.append(header_row)
    column_labels = header_row

    # --- Process data rows ---
    for row_elem in row_elems[1:]:
        # Handle repeated rows
        row_repeat = int(row_elem.get(f"{{{NS['table']}}}number-rows-repeated", "1"))

        row_cells = row_elem.xpath("./table:table-cell | ./table:covered-table-cell", namespaces=NS)
        single_row = []
        is_row_empty = True
        col_index = 0

        for cell_elem in row_cells:
            if col_index >= num_columns:
                break  # ignore extra columns beyond header
            if column_formats and col_index < len(column_labels):
                cf = column_formats.get(column_labels[col_index], "none")
                cell_fmt_map = None if cf == "none" else DEFAULT_FORMAT_MAPS.get(cf, None)
            else:
                cell_fmt_map = fmt_map
            paragraphs = cell_elem.xpath("./text:p", namespaces=NS)
            cell_text = ""
            if paragraphs:
                para_texts = []
                cell_style_name = cell_elem.get(f"{{{NS['table']}}}style-name")
                base_style = style_map.get(cell_style_name, DEFAULT_TEXT_PROPS.copy())
                for p in paragraphs:
                    p_style_name = p.get(f"{{{NS['text']}}}style-name")
                    p_base_style = _merge_styles(base_style, style_map.get(p_style_name, {}))
                    para_texts.append(_render_node_recursive(p, p_base_style, style_map, fmt_map=cell_fmt_map))
                cell_text = "\n".join(para_texts)

            if cell_text.strip():
                is_row_empty = False

            col_repeat = int(cell_elem.get(f"{{{NS['table']}}}number-columns-repeated", "1"))
            for _ in range(col_repeat):
                if col_index < num_columns:
                    single_row.append(cell_text if cell_text != "" else None)
                    col_index += 1

        # Fill missing cells with empty strings to match header length
        while len(single_row) < num_columns:
            single_row.append("")

        if is_row_empty:
            # add repeat count if empty
            empty_row_counter += row_repeat
            if empty_row_counter >= 10:
                break  # stop after five or more consecutive empty rows
            # skip adding empty rows
            continue
        else:
            empty_row_counter = 0
            # add non-empty row just once, repeated rows for non-empty seldom happen
            rows_out.append(single_row)

    return rows_out
