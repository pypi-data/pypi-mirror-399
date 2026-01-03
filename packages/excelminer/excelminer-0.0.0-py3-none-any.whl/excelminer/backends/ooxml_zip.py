from __future__ import annotations

import re
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from excelminer.backends.base import AnalysisContext, BackendReport
from excelminer.model.entities import Connection, DefinedName, Sheet, Source
from excelminer.model.graph import WorkbookGraph


def _read_zip_member(zf: zipfile.ZipFile, name: str) -> bytes | None:
    try:
        with zf.open(name) as f:
            return f.read()
    except KeyError:
        return None


def _localname(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


_SENSITIVE_KEYS = {"password", "pwd", "user id", "uid"}


def _parse_kv_connection_string(s: str) -> dict[str, str]:
    kv: dict[str, str] = {}
    if not s:
        return kv
    parts = [p for p in s.split(";") if p.strip()]
    for part in parts:
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        k = k.strip().lower()
        v = v.strip()
        if not k:
            continue
        kv[k] = v
    return kv


def _sanitize_kv(kv: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in kv.items():
        out[k] = "***" if k in _SENSITIVE_KEYS else v
    return out


def _summarize_conn_kv(kv: dict[str, str]) -> tuple[str, dict[str, Any]]:
    """Return (summary_string, structured_hints).

    Keep this stable and non-lossy enough for graph normalization.
    """

    hints: dict[str, Any] = {}
    provider = kv.get("provider")
    dsn = kv.get("dsn")
    server = kv.get("server") or kv.get("data source") or kv.get("address") or kv.get(
        "network address"
    )
    database = kv.get("database") or kv.get("initial catalog")

    if provider:
        hints["provider"] = provider
    if dsn:
        hints["dsn"] = dsn
    if server:
        hints["server"] = server
    if database:
        hints["database"] = database

    parts: list[str] = []
    if dsn:
        parts.append(f"odbc dsn={dsn}")
    if provider and provider.lower() != "microsoft.mashup.oledb.1":
        parts.append(f"provider={provider}")
    if server:
        parts.append(f"server={server}")
    if database:
        parts.append(f"database={database}")
    summary = "; ".join(parts) if parts else "unknown connection"
    return summary, hints


def _is_ooxml_excel(zf: zipfile.ZipFile) -> bool:
    names = set(zf.namelist())
    return "[Content_Types].xml" in names and "xl/workbook.xml" in names


def _parse_workbook_sheets(wb_xml: bytes) -> list[tuple[int, str]]:
    """Returns list[(index, sheet_name)] in workbook order (1-based index)."""

    out: list[tuple[int, str]] = []
    if not wb_xml:
        return out
    try:
        root = ET.fromstring(wb_xml)
    except ET.ParseError:
        return out

    idx = 0
    for el in root.iter():
        if _localname(el.tag) != "sheet":
            continue
        name = el.attrib.get("name")
        if not name:
            continue
        idx += 1
        out.append((idx, name))
    return out


def _parse_defined_names(wb_xml: bytes) -> list[dict[str, str]]:
    """Parses defined names from workbook.xml."""

    names: list[dict[str, str]] = []
    if not wb_xml:
        return names
    try:
        root = ET.fromstring(wb_xml)
    except ET.ParseError:
        return names

    # Build sheetId->name map (for localSheetId scope)
    sheet_map: dict[str, str] = {}
    for el in root.iter():
        if _localname(el.tag) != "sheet":
            continue
        sheet_id = el.attrib.get("sheetId")
        sheet_name = el.attrib.get("name")
        if sheet_id and sheet_name:
            sheet_map[sheet_id] = sheet_name

    for el in root.iter():
        if _localname(el.tag) != "definedName":
            continue
        name = (el.attrib.get("name") or "").strip()
        refers_to = (el.text or "").strip()
        local_sheet_id = (el.attrib.get("localSheetId") or "").strip()

        if not name:
            continue

        scope = "workbook"
        if local_sheet_id and local_sheet_id.isdigit():
            # localSheetId is 0-based index into workbook sheets in practice, but some
            # writers emit sheetId. We keep it best-effort and stable.
            scope = sheet_map.get(str(int(local_sheet_id) + 1), f"sheet:{local_sheet_id}")

        names.append({"name": name, "scope": scope, "refers_to": refers_to})

    return names


def _parse_connections_xml(xml_bytes: bytes) -> list[dict[str, Any]]:
    """Minimal, robust connection parsing from xl/connections.xml.

    Extracts:
      - id, name, type
      - raw connection string (if present)
      - url/file hints (web/text)
    """

    out: list[dict[str, Any]] = []
    if not xml_bytes:
        return out
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return out

    for conn in root.iter():
        if _localname(conn.tag) != "connection":
            continue

        c: dict[str, Any] = {}
        c["id"] = conn.attrib.get("id") or ""
        c["name"] = conn.attrib.get("name") or c["id"] or "connection"
        c["type"] = conn.attrib.get("type") or ""

        raw: str | None = None
        details: dict[str, Any] = {}

        for child in list(conn):
            ln = _localname(child.tag)
            if ln == "dbPr":
                raw = child.attrib.get("connection") or raw
                if child.attrib.get("command"):
                    details["command"] = child.attrib.get("command")
                if child.attrib.get("commandType"):
                    details["command_type"] = child.attrib.get("commandType")
            elif ln == "webPr":
                details["url"] = child.attrib.get("url") or details.get("url")
            elif ln == "textPr":
                details["source_file"] = child.attrib.get("sourceFile") or details.get(
                    "source_file"
                )

        if raw is not None:
            c["connection"] = raw
        if details:
            c["details"] = details

        out.append(c)

    return out


def _slug(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def _sheet_key(name: str) -> str:
    return _slug(name)


def _sheet_id(name: str) -> str:
    return f"sheet:{_sheet_key(name)}"


def _connection_key(name: str, conn_id: str) -> str:
    if conn_id:
        return f"{_slug(name)}|{conn_id}"
    return _slug(name)


def _connection_id(key: str) -> str:
    return f"conn:{key}"


def _source_key(source_type: str, server: str | None, database: str | None, value: str | None) -> str:
    parts = [source_type]
    if server:
        parts.append(server)
    if database:
        parts.append(database)
    if value:
        parts.append(value)
    return "|".join(parts)


def _source_id(key: str) -> str:
    return f"src:{key}"


@dataclass(slots=True)
class OOXMLZipBackend:
    """Structural OOXML backend: workbook.xml, connections.xml, defined names."""

    name: str = "ooxml_zip"

    def can_handle(self, ctx: AnalysisContext) -> bool:
        p = ctx.path
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
        p = ctx.path

        try:
            with zipfile.ZipFile(p) as zf:
                if not _is_ooxml_excel(zf):
                    report.issues.append("not an OOXML Excel workbook")
                    return report

                wb_xml = _read_zip_member(zf, "xl/workbook.xml") or b""

                sheets = _parse_workbook_sheets(wb_xml)
                if ctx.options.max_sheets is not None:
                    sheets = sheets[: ctx.options.max_sheets]

                sheet_ids: list[str] = []
                for idx, name in sheets:
                    s = Sheet.make(key=_sheet_key(name), id=_sheet_id(name), name=name, index=idx)
                    s2 = graph.upsert(s)
                    sheet_ids.append(s2.id)

                if ctx.options.include_defined_names:
                    for dn in _parse_defined_names(wb_xml):
                        name = dn.get("name", "")
                        scope = dn.get("scope", "workbook")
                        refers_to = dn.get("refers_to", "")
                        key = f"{scope}|{name}"
                        ent = DefinedName.make(
                            key=key,
                            id=f"defined:{key}",
                            name=name,
                            scope=scope,
                            refers_to=refers_to,
                        )
                        dn_node = graph.upsert(ent)
                        if scope not in ("workbook", ""):
                            sheet = graph.get_by_key("sheet", _sheet_key(scope))
                            if sheet:
                                graph.add_edge(dn_node.id, sheet.id, "scoped_to")

                if ctx.options.include_connections:
                    conns_xml = _read_zip_member(zf, "xl/connections.xml")
                    for c in _parse_connections_xml(conns_xml or b""):
                        conn_name = str(c.get("name") or "connection")
                        conn_id = str(c.get("id") or "")
                        conn_type = str(c.get("type") or "")
                        raw = str(c.get("connection") or "")
                        details = dict(c.get("details") or {})
                        if conn_id:
                            details.setdefault("connection_id", conn_id)

                        kind = "unknown"
                        if raw.lower().startswith("odbc") or "dsn=" in raw.lower():
                            kind = "odbc"
                        elif "provider=" in raw.lower() or conn_type == "1":
                            kind = "oledb"
                        elif "url" in details:
                            kind = "web"
                        elif "source_file" in details:
                            kind = "text"

                        kv = _parse_kv_connection_string(raw)
                        sanitized = _sanitize_kv(kv)
                        hints: dict[str, Any] = {}
                        if sanitized and raw:
                            summary, hints = _summarize_conn_kv(sanitized)
                            details.setdefault("connection_summary", summary)
                            details.setdefault("connection_kv", sanitized)

                        provider = str(hints.get("provider") or "")
                        if provider.lower() == "microsoft.mashup.oledb.1":
                            kind = "powerquery"

                        key = _connection_key(conn_name, conn_id)
                        conn = Connection.make(
                            key=key,
                            id=_connection_id(key),
                            name=conn_name,
                            connection_kind=kind,  # type: ignore[arg-type]
                            raw=raw or None,
                            details=details or None,
                        )
                        conn_node = graph.upsert(conn)

                        if sanitized and raw:
                            provider = hints.get("provider")
                            server = hints.get("server")
                            database = hints.get("database")
                            dsn = hints.get("dsn")

                            src_type: str = "unknown"
                            value: str | None = None
                            if dsn:
                                src_type = "odbc_dsn"
                                value = str(dsn)
                            elif provider and "sql" in str(provider).lower():
                                src_type = "sqlserver"
                            elif provider and "oracle" in str(provider).lower():
                                src_type = "oracle"

                            src_key = _source_key(src_type, server, database, value)
                            src = Source.make(
                                source_type=src_type,  # type: ignore[arg-type]
                                key=src_key,
                                id=_source_id(src_key),
                                server=str(server) if server else None,
                                database=str(database) if database else None,
                                value=value,
                                provider=str(provider) if provider else None,
                            )
                            src_node = graph.upsert(src)
                            graph.add_edge(conn_node.id, src_node.id, "uses_source")

                report.stats = graph.stats()
                report.stats.update({"sheets": len(sheet_ids)})
                return report

        except Exception as e:  # noqa: BLE001
            report.issues.append(str(e))
            return report
