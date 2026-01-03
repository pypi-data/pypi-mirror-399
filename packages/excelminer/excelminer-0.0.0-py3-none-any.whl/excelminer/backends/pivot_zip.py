from __future__ import annotations

import os
import re
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from excelminer.backends.base import AnalysisContext, BackendReport
from excelminer.backends.ooxml_zip import _is_ooxml_excel, _localname, _sheet_key
from excelminer.model.entities import PivotCache, PivotTable
from excelminer.model.graph import WorkbookGraph


def _read_zip_member(zf: zipfile.ZipFile, name: str) -> bytes | None:
    try:
        with zf.open(name) as f:
            return f.read()
    except KeyError:
        return None


def _get_sheet_path_to_name(zf: zipfile.ZipFile) -> dict[str, str]:
    """Return map of full worksheet part path -> sheet name."""

    wb_xml = _read_zip_member(zf, "xl/workbook.xml") or b""
    wb_rels = _read_zip_member(zf, "xl/_rels/workbook.xml.rels") or b""

    rid_to_target: dict[str, str] = {}
    try:
        root = ET.fromstring(wb_rels)
        for rel in root.iter():
            if _localname(rel.tag) != "Relationship":
                continue
            rid = rel.attrib.get("Id") or ""
            target = rel.attrib.get("Target") or ""
            if not rid or not target:
                continue
            if "worksheets/" in target.replace("\\", "/"):
                rid_to_target[rid] = os.path.normpath(os.path.join("xl", target)).replace("\\", "/")
    except ET.ParseError:
        pass

    sheet_path_to_name: dict[str, str] = {}
    try:
        root = ET.fromstring(wb_xml)
        for el in root.iter():
            if _localname(el.tag) != "sheet":
                continue
            name = (el.attrib.get("name") or "").strip()
            if not name:
                continue

            rid = ""
            for k, v in el.attrib.items():
                if k.endswith("}id") or k == "r:id":
                    rid = v
                    break

            target = rid_to_target.get(rid)
            if target:
                sheet_path_to_name[target] = name
    except ET.ParseError:
        pass

    return sheet_path_to_name


def _get_pivot_table_to_sheet(zf: zipfile.ZipFile, sheet_path_to_name: dict[str, str]) -> dict[str, str]:
    """Map full pivotTable part path -> sheet name."""

    out: dict[str, str] = {}
    for rels_path in zf.namelist():
        if not rels_path.startswith("xl/worksheets/_rels/") or not rels_path.endswith(".xml.rels"):
            continue

        sheet_path = rels_path.replace("xl/worksheets/_rels/", "xl/worksheets/").replace(".rels", "")
        sheet_name = sheet_path_to_name.get(sheet_path, "Unknown")

        rels_data = _read_zip_member(zf, rels_path)
        if not rels_data:
            continue

        try:
            root = ET.fromstring(rels_data)
        except ET.ParseError:
            continue

        for rel in root.iter():
            if _localname(rel.tag) != "Relationship":
                continue
            rel_type = rel.attrib.get("Type", "")
            if "pivotTable" not in rel_type:
                continue
            target = rel.attrib.get("Target", "")
            if not target:
                continue

            pt_path = os.path.normpath(os.path.join("xl/worksheets", target)).replace("\\", "/")
            out[pt_path] = sheet_name

    return out


def _get_cache_id_to_rid(zf: zipfile.ZipFile) -> dict[str, str]:
    cache_id_to_rid: dict[str, str] = {}
    wb_xml = _read_zip_member(zf, "xl/workbook.xml")
    if not wb_xml:
        return cache_id_to_rid

    try:
        root = ET.fromstring(wb_xml)
    except ET.ParseError:
        return cache_id_to_rid

    for el in root.iter():
        if _localname(el.tag) != "pivotCache":
            continue
        cache_id = (el.attrib.get("cacheId") or "").strip()
        if not cache_id:
            continue
        rid = ""
        for k, v in el.attrib.items():
            if k.endswith("}id") or k == "r:id":
                rid = v
                break
        if rid:
            cache_id_to_rid[cache_id] = rid

    return cache_id_to_rid


def _get_rid_to_cache_def_path(zf: zipfile.ZipFile) -> dict[str, str]:
    rid_to_path: dict[str, str] = {}
    rels = _read_zip_member(zf, "xl/_rels/workbook.xml.rels")
    if not rels:
        return rid_to_path

    try:
        root = ET.fromstring(rels)
    except ET.ParseError:
        return rid_to_path

    for rel in root.iter():
        if _localname(rel.tag) != "Relationship":
            continue
        rel_type = rel.attrib.get("Type", "")
        if "pivotCacheDefinition" not in rel_type:
            continue
        rid = rel.attrib.get("Id", "")
        target = rel.attrib.get("Target", "")
        if not rid or not target:
            continue
        rid_to_path[rid] = os.path.normpath(os.path.join("xl", target)).replace("\\", "/")

    return rid_to_path


def _parse_cache_definition(zf: zipfile.ZipFile, cache_path: str) -> tuple[str, str, list[str], dict[str, str]]:
    """Return (source_type, source_reference, field_names_list, field_index_to_name)."""

    data = _read_zip_member(zf, cache_path)
    if not data:
        return "unknown", "missing cache definition", [], {}

    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return "unknown", "unparseable cache definition", [], {}

    source_type = "unknown"
    source_ref = "Unknown"

    # Parse cache fields
    field_names: list[str] = []
    field_idx_map: dict[str, str] = {}
    for elem in root.iter():
        if _localname(elem.tag) != "cacheFields":
            continue
        idx = 0
        for cf in elem:
            if _localname(cf.tag) != "cacheField":
                continue
            nm = (cf.attrib.get("name") or "").strip()
            if nm:
                field_names.append(nm)
                field_idx_map[str(idx)] = nm
            idx += 1
        break

    # Parse cache source
    for elem in root.iter():
        if _localname(elem.tag) != "cacheSource":
            continue

        conn_id = (elem.attrib.get("connectionId") or "").strip()

        # Prefer explicit children
        for child in list(elem):
            ln = _localname(child.tag)
            if ln == "worksheetSource":
                source_type = "worksheet"
                ref = (child.attrib.get("ref") or "").strip()
                sheet = (child.attrib.get("sheet") or "").strip()
                name_attr = (child.attrib.get("name") or "").strip()
                if name_attr:
                    source_type = "table"
                    source_ref = f"{sheet}!{name_attr}" if sheet else name_attr
                elif sheet and ref:
                    source_ref = f"{sheet}!{ref}"
                elif ref:
                    source_ref = ref
                elif sheet:
                    source_ref = f"{sheet} (entire sheet)"
                else:
                    source_ref = "Unknown range"
                break

            if ln == "consolidation":
                source_type = "consolidation"
                source_ref = "Multiple ranges"
                break

        if source_type == "unknown" and conn_id:
            source_type = "connection"
            source_ref = f"Connection ID: {conn_id}"

        break

    return source_type, source_ref, field_names, field_idx_map


@dataclass(slots=True)
class PivotZipBackend:
    """Extract pivot tables and pivot caches from OOXML parts.

    This is best-effort and focuses on:
    - pivot table name
    - sheet placement (via worksheet relationships)
    - cacheId
    - cache source (worksheet vs connection) when available
    - measures (dataFields) and basic row/column grouping field names
    """

    name: str = "pivot_zip"

    def can_handle(self, ctx: AnalysisContext) -> bool:
        p = ctx.path
        if not ctx.options.include_pivots:
            return False
        if not p.exists() or not p.is_file():
            return False
        if p.suffix.lower() not in (".xlsx", ".xlsm", ".xltx", ".xltm"):
            return False
        try:
            with zipfile.ZipFile(p):
                return True
        except zipfile.BadZipFile:
            return False

    def extract(self, ctx: AnalysisContext, graph: WorkbookGraph) -> BackendReport:
        report = BackendReport(backend=self.name)
        p: Path = ctx.path

        pivots = 0
        caches = 0

        try:
            with zipfile.ZipFile(p) as zf:
                if not _is_ooxml_excel(zf):
                    report.issues.append("not an OOXML Excel workbook")
                    report.stats = graph.stats()
                    return report

                sheet_path_to_name = _get_sheet_path_to_name(zf)
                pt_to_sheet = _get_pivot_table_to_sheet(zf, sheet_path_to_name)

                cache_id_to_rid = _get_cache_id_to_rid(zf)
                rid_to_cache = _get_rid_to_cache_def_path(zf)

                cache_info_by_id: dict[str, dict[str, Any]] = {}
                field_idx_by_cache_id: dict[str, dict[str, str]] = {}

                for cache_id, rid in cache_id_to_rid.items():
                    cache_path = rid_to_cache.get(rid)
                    if not cache_path:
                        continue
                    source_type, source_ref, field_names, field_idx_map = _parse_cache_definition(
                        zf, cache_path
                    )

                    key = f"{cache_id}|{source_type}|{source_ref}"
                    cache_node = graph.upsert(
                        PivotCache.make(
                            key=key,
                            id=f"pcache:{key}",
                            cache_id=cache_id,
                            source_type=source_type,  # type: ignore[arg-type]
                            source_ref=source_ref,
                            extra={"ooxml_part": cache_path, "fields": field_names},
                        )
                    )
                    cache_info_by_id[cache_id] = {"node": cache_node, "source_type": source_type, "source_ref": source_ref}
                    field_idx_by_cache_id[cache_id] = field_idx_map
                    caches += 1

                    # Optional link to a connection node if we can match by connection_id.
                    if source_type == "connection":
                        m = re.search(r"Connection ID:\s*(\d+)", source_ref)
                        if m:
                            conn_id = m.group(1)
                            for n in graph.nodes.values():
                                if n.kind != "connection":
                                    continue
                                if str(n.attrs.get("connection_id") or "") == conn_id:
                                    graph.add_edge(cache_node.id, n.id, "uses_connection")
                                    break

                seen: set[tuple[str, str, str]] = set()
                for pt_path in zf.namelist():
                    if not pt_path.startswith("xl/pivotTables/pivotTable") or not pt_path.endswith(".xml"):
                        continue

                    data = _read_zip_member(zf, pt_path)
                    if not data:
                        continue

                    try:
                        root = ET.fromstring(data)
                    except ET.ParseError:
                        continue

                    pt_name = (root.attrib.get("name") or "PivotTable").strip() or "PivotTable"
                    cache_id = (root.attrib.get("cacheId") or "").strip()
                    sheet_name = pt_to_sheet.get(pt_path, "Unknown")

                    uniq = (pt_name, sheet_name, cache_id)
                    if uniq in seen:
                        continue
                    seen.add(uniq)

                    measures: list[dict[str, Any]] = []
                    grouping_fields: list[dict[str, Any]] = []

                    for el in root.iter():
                        if _localname(el.tag) == "dataField":
                            nm = (el.attrib.get("name") or "").strip()
                            subtotal = (el.attrib.get("subtotal") or "sum").strip()
                            if nm:
                                measures.append({"name": nm, "aggregation": subtotal})

                    for el in root.iter():
                        ln = _localname(el.tag)
                        if ln == "rowFields":
                            for f in el:
                                if _localname(f.tag) == "field":
                                    grouping_fields.append({"field_index": f.attrib.get("x", ""), "axis": "row"})
                        if ln == "colFields":
                            for f in el:
                                if _localname(f.tag) == "field":
                                    grouping_fields.append({"field_index": f.attrib.get("x", ""), "axis": "column"})

                    field_names = field_idx_by_cache_id.get(cache_id, {})
                    for gf in grouping_fields:
                        idx = str(gf.get("field_index") or "")
                        gf["name"] = field_names.get(idx, f"Field_{idx}" if idx else "Field")

                    sheet_key = _sheet_key(sheet_name)
                    key = f"{sheet_key}|{pt_name}|{cache_id}"
                    pt_node = graph.upsert(
                        PivotTable.make(
                            key=key,
                            id=f"pivot:{key}",
                            name=pt_name,
                            sheet_name=sheet_name,
                            measures=measures,
                            grouping_fields=[{"name": gf.get("name", ""), "axis": gf.get("axis", "")} for gf in grouping_fields],
                            extra={"ooxml_part": pt_path, "cache_id": cache_id},
                        )
                    )
                    pivots += 1

                    sheet = graph.get_by_key("sheet", sheet_key)
                    if sheet:
                        graph.add_edge(sheet.id, pt_node.id, "contains")

                    cache_node = cache_info_by_id.get(cache_id, {}).get("node")
                    if cache_node:
                        graph.add_edge(pt_node.id, cache_node.id, "uses_cache")

        except Exception as e:  # noqa: BLE001
            report.issues.append(str(e))

        report.stats = {"pivot_tables": pivots, "pivot_caches": caches, **graph.stats()}
        return report
