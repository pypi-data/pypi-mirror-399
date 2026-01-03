from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from excelminer.backends.base import AnalysisContext, AnalysisOptions
from excelminer.backends.com_backend import ComBackend
from excelminer.backends.ooxml_zip import OOXMLZipBackend
from excelminer.backends.openpyxl_backend import _extract_deps  # type: ignore
from excelminer.model.entities import Connection, Edge, Sheet, Source
from excelminer.model.graph import WorkbookGraph


def test_entities_to_dict_and_factories() -> None:
    e = Edge(src="a", dst="b", kind="k", attrs={"x": 1})
    assert e.to_dict()["attrs"]["x"] == 1

    c = Connection.make(key="k", id="conn:k", name="n", raw="abc", details={"d": 1})
    d = c.to_dict()
    assert d["kind"] == "connection"
    assert d["attrs"]["name"] == "n"
    assert d["attrs"]["raw"] == "abc"
    assert d["attrs"]["d"] == 1

    s = Source.make(source_type="sqlserver", key="k", id="src:k", server="h", database="db")
    sd = s.to_dict()
    assert sd["kind"] == "source"
    assert sd["attrs"]["server"] == "h"
    assert sd["attrs"]["database"] == "db"


def test_graph_get_or_create_calls_factory_once() -> None:
    g = WorkbookGraph()
    calls: list[str] = []

    def factory() -> Sheet:
        calls.append("x")
        return Sheet.make(key="A", id="sheet:A", name="A")

    a1 = g.get_or_create("sheet", "A", factory)
    a2 = g.get_or_create("sheet", "A", factory)
    assert a1 is a2
    assert calls == ["x"]


@pytest.mark.parametrize(
    "formula,expected",
    [
        ("=SUM(A1:A2)", {"refs": [{"sheet": "", "cell": "A1"}, {"sheet": "", "cell": "A2"}]}),
        ("='My Sheet'!$B$2 + Sheet2!C3", {"refs": [{"sheet": "My Sheet", "cell": "B2"}, {"sheet": "Sheet2", "cell": "C3"}]}),
        ("=1+2", {}),
        ("", {}),
    ],
)
def test_extract_deps_edge_cases(formula: str, expected: dict[str, object]) -> None:
    assert _extract_deps(formula) == expected


def _write_minimal_zip(path: Path, files: dict[str, str]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, body in files.items():
            zf.writestr(name, body)


def test_ooxml_zip_backend_web_and_text_connections(tmp_path: Path) -> None:
    content_types = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\"></Types>
"""
    workbook_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">
  <sheets>
    <sheet name=\"S\" sheetId=\"1\"/>
  </sheets>
</workbook>
"""
    connections_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<connections xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">
  <connection id=\"1\" name=\"WebConn\">
    <webPr url=\"https://example.com\" />
  </connection>
  <connection id=\"2\" name=\"TextConn\">
    <textPr sourceFile=\"C:\\data.csv\" />
  </connection>
</connections>
"""

    xlsx = tmp_path / "conn_types.xlsx"
    _write_minimal_zip(
        xlsx,
        {
            "[Content_Types].xml": content_types,
            "xl/workbook.xml": workbook_xml,
            "xl/connections.xml": connections_xml,
        },
    )

    ctx = AnalysisContext(path=xlsx, options=AnalysisOptions(include_connections=True, include_defined_names=False))
    g = WorkbookGraph()
    rep = OOXMLZipBackend().extract(ctx, g)
    assert rep.issues == []

    conns = [n for n in g.nodes.values() if n.kind == "connection"]
    assert len(conns) == 2
    kinds = {c.attrs.get("connection_kind") for c in conns}
    assert "web" in kinds
    assert "text" in kinds


def test_ooxml_zip_backend_handles_malformed_xml(tmp_path: Path) -> None:
    # workbook.xml is malformed; backend should not crash.
    content_types = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\"></Types>
"""
    xlsx = tmp_path / "bad.xlsx"
    _write_minimal_zip(
        xlsx,
        {
            "[Content_Types].xml": content_types,
            "xl/workbook.xml": "<workbook><notclosed>",
        },
    )

    ctx = AnalysisContext(path=xlsx, options=AnalysisOptions(include_connections=False, include_defined_names=True))
    g = WorkbookGraph()
    rep = OOXMLZipBackend().extract(ctx, g)
    # No exception; report exists.
    assert rep.backend == "ooxml_zip"
    assert rep.stats["nodes"] == len(g.nodes)


def test_com_backend_extract_reports_missing_pywin32(tmp_path: Path) -> None:
    p = tmp_path / "x.xlsx"
    p.write_bytes(b"dummy")
    ctx = AnalysisContext(path=p)

    b = ComBackend()
    if not b.can_handle(ctx):
        pytest.skip("COM backend not applicable on this platform")

    rep = b.extract(ctx, WorkbookGraph())
    assert rep.backend == "com"
    assert rep.stats
    # In most envs, pywin32 won't be installed; either way, we shouldn't crash.
    assert isinstance(rep.issues, list)
