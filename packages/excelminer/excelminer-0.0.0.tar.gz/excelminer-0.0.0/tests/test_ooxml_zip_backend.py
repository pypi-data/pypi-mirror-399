from __future__ import annotations

import zipfile
from pathlib import Path

from excelminer.backends.base import AnalysisContext, AnalysisOptions
from excelminer.backends.ooxml_zip import OOXMLZipBackend
from excelminer.model.graph import WorkbookGraph


def _write_minimal_ooxml_zip(path: Path, *, workbook_xml: str, connections_xml: str | None = None) -> None:
    # Minimal structure to satisfy OOXMLZipBackend._is_ooxml_excel
    content_types = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\"></Types>
"""

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("xl/workbook.xml", workbook_xml)
        if connections_xml is not None:
            zf.writestr("xl/connections.xml", connections_xml)


def test_ooxml_zip_backend_extracts_sheets_and_defined_names(tmp_path: Path) -> None:
    workbook_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">
  <sheets>
    <sheet name=\"Sheet One\" sheetId=\"1\"/>
    <sheet name=\"Second\" sheetId=\"2\"/>
  </sheets>
  <definedNames>
    <definedName name=\"MyName\">Sheet One!$A$1</definedName>
    <definedName name=\"LocalName\" localSheetId=\"0\">$B$2</definedName>
  </definedNames>
</workbook>
"""

    xlsx = tmp_path / "minimal.xlsx"
    _write_minimal_ooxml_zip(xlsx, workbook_xml=workbook_xml)

    ctx = AnalysisContext(
        path=xlsx,
        options=AnalysisOptions(include_connections=False, include_defined_names=True),
    )
    g = WorkbookGraph()
    report = OOXMLZipBackend().extract(ctx, g)

    assert report.backend == "ooxml_zip"
    assert report.issues == []

    kinds = {n.kind for n in g.nodes.values()}
    assert "sheet" in kinds
    assert "defined_name" in kinds

    # Both sheets should exist
    assert g.get_by_key("sheet", "Sheet One") is not None
    assert g.get_by_key("sheet", "Second") is not None


def test_ooxml_zip_backend_parses_connections_and_sanitizes(tmp_path: Path) -> None:
    workbook_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">
  <sheets>
    <sheet name=\"Sheet1\" sheetId=\"1\"/>
  </sheets>
</workbook>
"""

    connections_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<connections xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">
  <connection id=\"1\" name=\"MyConn\" type=\"1\">
    <dbPr connection=\"Provider=SQLOLEDB;Data Source=HOST;Initial Catalog=DB;User ID=sa;Password=secret\" />
  </connection>
</connections>
"""

    xlsx = tmp_path / "with_connections.xlsx"
    _write_minimal_ooxml_zip(xlsx, workbook_xml=workbook_xml, connections_xml=connections_xml)

    ctx = AnalysisContext(
        path=xlsx,
        options=AnalysisOptions(include_connections=True, include_defined_names=False),
    )
    g = WorkbookGraph()
    report = OOXMLZipBackend().extract(ctx, g)

    assert report.issues == []

    conn = next((n for n in g.nodes.values() if n.kind == "connection"), None)
    assert conn is not None

    # Ensure sanitized connection string data made it into attrs
    kv = conn.attrs.get("connection_kv")
    assert isinstance(kv, dict)
    assert kv.get("password") == "***"
    assert kv.get("user id") == "***"

    # A Source should be created and connected
    src = next((n for n in g.nodes.values() if n.kind == "source"), None)
    assert src is not None

    assert any(e.src == conn.id and e.dst == src.id and e.kind == "uses_source" for e in g.edges)


def test_ooxml_zip_backend_can_handle_rejects_non_zip(tmp_path: Path) -> None:
    p = tmp_path / "not_a_zip.xlsx"
    p.write_text("nope", encoding="utf-8")

    ctx = AnalysisContext(path=p)
    assert OOXMLZipBackend().can_handle(ctx) is False
