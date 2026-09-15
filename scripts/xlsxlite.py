#!/usr/bin/env python3
"""xlsxlite — create, read and append to a simple one-sheet .xlsx using only the standard library.

Scope is deliberately tiny: one worksheet, a header row, text cells, optionally an Excel Table
over the data. Appending never rewrites existing parts — it inserts <row> elements as text before
</sheetData> and bumps the <dimension> and table refs. Reading resolves shared strings and inline
strings and ignores everything else.

Used by tracker_init.py, append_tasks.py and brief_collect.py. Run `python scripts/xlsxlite.py --selftest`.
"""
import argparse
import io
import os
import re
import sys
import tempfile
import zipfile
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"m": NS_MAIN, "r": NS_REL}


# ----------------------------------------------------------------------------- cell refs
def col_letter(n):
    """1 -> A, 27 -> AA"""
    s = ""
    while n > 0:
        n, rem = divmod(n - 1, 26)
        s = chr(65 + rem) + s
    return s


def col_index(letters):
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch.upper()) - 64)
    return n


def split_ref(ref):
    m = re.match(r"^([A-Z]+)(\d+)$", ref)
    if not m:
        raise ValueError("bad cell ref %r" % ref)
    return m.group(1), int(m.group(2))


# ----------------------------------------------------------------------------- package I/O
def read_pkg(path):
    with zipfile.ZipFile(path) as z:
        return {n: z.read(n) for n in z.namelist()}


def write_pkg(path, parts):
    names = list(parts.keys())
    if "[Content_Types].xml" in names:
        names.remove("[Content_Types].xml")
        names.insert(0, "[Content_Types].xml")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for n in names:
            z.writestr(n, parts[n])
    with open(path, "wb") as f:
        f.write(buf.getvalue())


def _first_sheet_part(parts):
    wb = ET.fromstring(parts["xl/workbook.xml"])
    sheets = wb.find("m:sheets", NS)
    first = sheets[0]
    rid = first.get("{%s}id" % NS_REL)
    rels = ET.fromstring(parts["xl/_rels/workbook.xml.rels"])
    for rel in rels:
        if rel.get("Id") == rid:
            target = rel.get("Target")
            if target.startswith("/"):
                return target[1:]
            return "xl/" + target
    raise ValueError("first sheet relationship not found")


def _table_parts_for_sheet(parts, sheet_part):
    d, base = os.path.split(sheet_part)
    rels_name = "%s/_rels/%s.rels" % (d, base)
    if rels_name not in parts:
        return []
    out = []
    rels = ET.fromstring(parts[rels_name])
    for rel in rels:
        if rel.get("Type", "").endswith("/table"):
            target = rel.get("Target")
            if target.startswith("/"):
                out.append(target[1:])
            else:
                out.append(os.path.normpath(os.path.join(d, target)).replace("\\", "/"))
    return out


# ----------------------------------------------------------------------------- reading
def _shared_strings(parts):
    if "xl/sharedStrings.xml" not in parts:
        return []
    root = ET.fromstring(parts["xl/sharedStrings.xml"])
    out = []
    for si in root.findall("m:si", NS):
        out.append("".join(t.text or "" for t in si.iter("{%s}t" % NS_MAIN)))
    return out


def read_rows(path):
    """Return (header, rows) where rows is a list of dicts keyed by header. Text only."""
    parts = read_pkg(path)
    sheet_part = _first_sheet_part(parts)
    sst = _shared_strings(parts)
    root = ET.fromstring(parts[sheet_part])
    grid = {}
    maxcol = 0
    for row in root.iter("{%s}row" % NS_MAIN):
        r = int(row.get("r"))
        for c in row.findall("m:c", NS):
            letters, _ = split_ref(c.get("r"))
            ci = col_index(letters)
            maxcol = max(maxcol, ci)
            t = c.get("t")
            v = c.find("m:v", NS)
            if t == "s" and v is not None:
                val = sst[int(v.text)]
            elif t == "inlineStr":
                val = "".join(x.text or "" for x in c.iter("{%s}t" % NS_MAIN))
            elif v is not None:
                val = v.text or ""
            else:
                val = ""
            grid[(r, ci)] = val
    if not grid:
        return [], []
    rownums = sorted({r for r, _ in grid})
    header = [grid.get((rownums[0], ci), "") for ci in range(1, maxcol + 1)]
    rows = []
    for r in rownums[1:]:
        vals = [grid.get((r, ci), "") for ci in range(1, maxcol + 1)]
        if not any(v.strip() for v in vals):
            continue
        rows.append(dict(zip(header, vals)))
    return header, rows


# ----------------------------------------------------------------------------- creating
def _minimal_parts(header, sheet_name="Actions", table_name="Actions"):
    ncols = len(header)
    last = col_letter(ncols)
    cells = "".join(
        '<c r="%s1" t="inlineStr"><is><t>%s</t></is></c>' % (col_letter(i + 1), escape(h))
        for i, h in enumerate(header)
    )
    sheet = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<worksheet xmlns="%s" xmlns:r="%s">'
        '<dimension ref="A1:%s2"/>'
        '<sheetViews><sheetView workbookViewId="0"/></sheetViews>'
        '<sheetFormatPr defaultRowHeight="15"/>'
        '<cols>%s</cols>'
        '<sheetData><row r="1">%s</row></sheetData>'
        '<tableParts count="1"><tablePart r:id="rId1"/></tableParts>'
        "</worksheet>"
    ) % (
        NS_MAIN, NS_REL, last,
        "".join('<col min="%d" max="%d" width="%d" customWidth="1"/>' % (i + 1, i + 1, 14 if h != "action" else 60)
                for i, h in enumerate(header)),
        cells,
    )
    table = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<table xmlns="%s" id="1" name="%s" displayName="%s" ref="A1:%s2" totalsRowShown="0">'
        '<autoFilter ref="A1:%s2"/>'
        '<tableColumns count="%d">%s</tableColumns>'
        '<tableStyleInfo name="TableStyleMedium2" showFirstColumn="0" showLastColumn="0" '
        'showRowStripes="1" showColumnStripes="0"/>'
        "</table>"
    ) % (
        NS_MAIN, table_name, table_name, last, last, ncols,
        "".join('<tableColumn id="%d" name="%s"/>' % (i + 1, escape(h)) for i, h in enumerate(header)),
    )
    workbook = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<workbook xmlns="%s" xmlns:r="%s">'
        '<sheets><sheet name="%s" sheetId="1" r:id="rId1"/></sheets>'
        "</workbook>"
    ) % (NS_MAIN, NS_REL, escape(sheet_name))
    wb_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="%s">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        "</Relationships>"
    ) % NS_PKG_REL
    sheet_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="%s">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/table" Target="../tables/table1.xml"/>'
        "</Relationships>"
    ) % NS_PKG_REL
    styles = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<styleSheet xmlns="%s">'
        '<fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>'
        '<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>'
        '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
        "</styleSheet>"
    ) % NS_MAIN
    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="%s">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        "</Relationships>"
    ) % NS_PKG_REL
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        '<Override PartName="/xl/tables/table1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.table+xml"/>'
        "</Types>"
    )
    return {
        "[Content_Types].xml": content_types.encode("utf-8"),
        "_rels/.rels": root_rels.encode("utf-8"),
        "xl/workbook.xml": workbook.encode("utf-8"),
        "xl/_rels/workbook.xml.rels": wb_rels.encode("utf-8"),
        "xl/styles.xml": styles.encode("utf-8"),
        "xl/worksheets/sheet1.xml": sheet.encode("utf-8"),
        "xl/worksheets/_rels/sheet1.xml.rels": sheet_rels.encode("utf-8"),
        "xl/tables/table1.xml": table.encode("utf-8"),
    }


def create(path, header, sheet_name="Actions", table_name="Actions"):
    if os.path.exists(path):
        raise FileExistsError(path)
    write_pkg(path, _minimal_parts(header, sheet_name, table_name))


# ----------------------------------------------------------------------------- appending
def _row_xml(rownum, values):
    cells = []
    for i, v in enumerate(values):
        v = "" if v is None else str(v)
        if v == "":
            continue
        cells.append('<c r="%s%d" t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>'
                     % (col_letter(i + 1), rownum, escape(v)))
    return '<row r="%d">%s</row>' % (rownum, "".join(cells))


def _bump_ref(xml_text, attr_pattern, last_row, ncols):
    """Rewrite ref="A1:X<n>" to cover last_row rows."""
    def repl(m):
        start = m.group(2)
        letters, _ = split_ref(start)
        return '%s="%s:%s%d"' % (m.group(1), start, col_letter(max(ncols, col_index(m.group(3)))), last_row)
    return re.sub(r'(%s)="([A-Z]+\d+):([A-Z]+)\d+"' % attr_pattern, repl, xml_text)


def append_rows(path, rows):
    """rows: list of lists (already in header order). Returns number of rows written.
    Raises PermissionError when the file is locked (Excel has it open)."""
    if not rows:
        return 0
    lock = os.path.join(os.path.dirname(os.path.abspath(path)), "~$" + os.path.basename(path))
    if os.path.exists(lock):
        raise PermissionError("tracker is open in Excel (lock file %s)" % lock)
    parts = read_pkg(path)
    sheet_part = _first_sheet_part(parts)
    text = parts[sheet_part].decode("utf-8")
    ncols = len(rows[0])
    # current last row (ignore rows with no cells — the empty table row of a fresh tracker)
    used = [int(m.group(1)) for m in re.finditer(r'<row [^>]*\br="(\d+)"[^>]*>(?!</row>)', text)]
    empty_rows = re.findall(r'<row [^>]*\br="(\d+)"[^>]*/>', text) + \
        re.findall(r'<row [^>]*\br="(\d+)"[^>]*></row>', text)
    last_used = max(used) if used else 1
    next_row = last_used + 1
    # drop trailing empty <row/> placeholders that we are about to overwrite
    for r in empty_rows:
        if int(r) >= next_row:
            text = re.sub(r'<row [^>]*\br="%s"[^>]*/>' % r, "", text)
            text = re.sub(r'<row [^>]*\br="%s"[^>]*></row>' % r, "", text)
    new_xml = "".join(_row_xml(next_row + i, r) for i, r in enumerate(rows))
    if "</sheetData>" in text:
        text = text.replace("</sheetData>", new_xml + "</sheetData>", 1)
    elif "<sheetData/>" in text:
        text = text.replace("<sheetData/>", "<sheetData>" + new_xml + "</sheetData>", 1)
    else:
        raise ValueError("no sheetData in %s" % sheet_part)
    last_row = next_row + len(rows) - 1
    text = _bump_ref(text, "ref", last_row, ncols) if "<dimension" in text else text
    # only the dimension element should have been touched above; autoFilter on the sheet too, which is fine
    parts[sheet_part] = text.encode("utf-8")
    for tp in _table_parts_for_sheet(parts, sheet_part):
        ttext = parts[tp].decode("utf-8")
        ttext = _bump_ref(ttext, "ref", last_row, ncols)
        parts[tp] = ttext.encode("utf-8")
    # write via temp + replace so a locked file fails cleanly
    tmp = path + ".tmp"
    write_pkg(tmp, parts)
    try:
        os.replace(tmp, path)
    except PermissionError:
        os.remove(tmp)
        raise
    return len(rows)


# ----------------------------------------------------------------------------- selftest
def _selftest():
    header = ["id", "created", "action", "notes"]
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "t.xlsx")
        create(p, header)
        h, rows = read_rows(p)
        assert h == header and rows == [], (h, rows)
        n = append_rows(p, [["a1", "2026-09-15", "Do the thing & more", ""], ["a2", "2026-09-15", "Second <thing>", "x"]])
        assert n == 2
        h, rows = read_rows(p)
        assert len(rows) == 2 and rows[1]["action"] == "Second <thing>", rows
        n = append_rows(p, [["a3", "2026-09-16", "Third", ""]])
        h, rows = read_rows(p)
        assert [r["id"] for r in rows] == ["a1", "a2", "a3"]
        parts = read_pkg(p)
        for name, data in parts.items():
            if name.endswith(".xml") or name.endswith(".rels"):
                ET.fromstring(data)  # well-formed
        assert b'ref="A1:D4"' in parts["xl/tables/table1.xml"], parts["xl/tables/table1.xml"]
        assert b'<dimension ref="A1:D4"/>' in parts["xl/worksheets/sheet1.xml"]
        # lock file → PermissionError
        open(os.path.join(d, "~$t.xlsx"), "w").close()
        try:
            append_rows(p, [["a4", "", "", ""]])
            raise AssertionError("lock not detected")
        except PermissionError:
            pass
    print("xlsxlite selftest OK")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dump", help="print the rows of an .xlsx as TSV")
    a = ap.parse_args()
    if a.selftest:
        _selftest()
    elif a.dump:
        h, rows = read_rows(a.dump)
        print("\t".join(h))
        for r in rows:
            print("\t".join(r.get(k, "") for k in h))
    else:
        ap.print_help()
        sys.exit(1)
