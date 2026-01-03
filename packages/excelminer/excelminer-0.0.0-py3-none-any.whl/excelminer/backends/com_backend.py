from __future__ import annotations

import platform
from dataclasses import dataclass
from typing import Any

from excelminer.backends.base import AnalysisContext, BackendReport
from excelminer.backends.ooxml_zip import _parse_kv_connection_string, _sanitize_kv, _summarize_conn_kv
from excelminer.model.entities import Connection, DefinedName, FormulaCell, Sheet, Source
from excelminer.model.graph import WorkbookGraph


@dataclass(slots=True)
class ComBackend:
    """Windows-only enrichment backend using Excel COM automation.

    In v0.0.0 this is a safe placeholder. It is wired so callers can opt-in later
    without changing the orchestrator.

    Install extras with: `pip install excelminer[com]`
    """

    name: str = "com"

    def can_handle(self, ctx: AnalysisContext) -> bool:
        if platform.system() != "Windows":
            return False
        p = ctx.path
        if not p.exists() or not p.is_file():
            return False
        ext = p.suffix.lower()
        # Always allow COM for legacy formats (OOXML parsing may be incomplete or unavailable).
        if ext in (".xls", ".xlsb", ".xlt"):
            return True

        # For modern OOXML files, require explicit opt-in.
        if not getattr(ctx.options, "include_com", False):
            return False

        return ext in (".xlsx", ".xlsm", ".xltx", ".xltm")

    def extract(self, ctx: AnalysisContext, graph: WorkbookGraph) -> BackendReport:
        report = BackendReport(backend=self.name)
        try:
            import win32com.client  # type: ignore[import-not-found]
        except Exception as e:  # noqa: BLE001
            report.issues.append(f"pywin32 not available: {e}")
            report.stats = graph.stats()
            return report

        pythoncom = None
        com_initialized = False
        try:
            import pythoncom  # type: ignore[import-not-found]

            # Ensure COM is initialized for this thread (pytest can run in different contexts).
            pythoncom.CoInitialize()
            com_initialized = True
        except Exception:
            # If pythoncom is unavailable or initialization fails, continue; COM calls may still work.
            pythoncom = None

        xl = None
        wb = None

        # Excel constants (avoid importing win32com.client.constants for speed/reliability)
        msoAutomationSecurityForceDisable = 3

        def _col_to_name(col: int) -> str:
            # 1-indexed
            name = ""
            while col > 0:
                col, rem = divmod(col - 1, 26)
                name = chr(65 + rem) + name
            return name

        try:
            xl = win32com.client.DispatchEx("Excel.Application")
            xl.Visible = False
            xl.DisplayAlerts = False
            try:
                xl.AutomationSecurity = msoAutomationSecurityForceDisable
            except Exception:
                # Not available in some Excel versions.
                pass

            # Open workbook read-only; don't update links.
            wb = xl.Workbooks.Open(
                str(ctx.path),
                UpdateLinks=0,
                ReadOnly=True,
                AddToMru=False,
            )

            # --- Sheets ---
            sheets_scanned = 0
            for ws in wb.Worksheets:
                sheets_scanned += 1
                if ctx.options.max_sheets is not None and sheets_scanned > ctx.options.max_sheets:
                    break

                name = str(ws.Name)
                sheet_key = " ".join(name.strip().split())
                sheet_id = f"sheet:{sheet_key}"
                graph.upsert(Sheet.make(key=sheet_key, id=sheet_id, name=name, index=sheets_scanned))

            # --- Defined names ---
            if ctx.options.include_defined_names:
                try:
                    for n in wb.Names:
                        full_name = str(n.Name)
                        refers_to = str(getattr(n, "RefersTo", "") or "")

                        scope = "workbook"
                        name = full_name
                        if "!" in full_name:
                            scope, name = full_name.split("!", 1)
                            scope = scope.strip("'")

                        key = f"{scope}|{name}"
                        dn = DefinedName.make(
                            key=key,
                            id=f"defined:{key}",
                            name=name,
                            scope=scope,
                            refers_to=refers_to,
                        )
                        dn_node = graph.upsert(dn)
                        if scope not in ("workbook", ""):
                            sheet = graph.get_by_key("sheet", " ".join(scope.strip().split()))
                            if sheet:
                                graph.add_edge(dn_node.id, sheet.id, "scoped_to")
                except Exception as e:  # noqa: BLE001
                    report.issues.append(f"defined names extraction failed: {e}")

            # --- Connections ---
            if ctx.options.include_connections:
                try:
                    count = int(getattr(wb.Connections, "Count", 0) or 0)
                    for i in range(1, count + 1):
                        conn = wb.Connections.Item(i)
                        conn_name = str(getattr(conn, "Name", f"connection_{i}"))
                        raw = ""
                        details: dict[str, Any] = {}

                        # Try common sub-objects.
                        try:
                            raw = str(getattr(conn, "OLEDBConnection").Connection)
                            details["connection_kind"] = "oledb"
                        except Exception:
                            try:
                                raw = str(getattr(conn, "ODBCConnection").Connection)
                                details["connection_kind"] = "odbc"
                            except Exception:
                                raw = str(getattr(conn, "Connection", "") or "")
                                details["connection_kind"] = "unknown"

                        key = f"{conn_name}|{i}"
                        kv = _sanitize_kv(_parse_kv_connection_string(raw))
                        hints: dict[str, Any] = {}
                        if kv and raw:
                            summary, hints = _summarize_conn_kv(kv)
                            details["connection_summary"] = summary
                            details["connection_kv"] = kv

                        conn_node = graph.upsert(
                            Connection.make(
                                key=key,
                                id=f"conn:{key}",
                                name=conn_name,
                                connection_kind=str(details.get("connection_kind", "unknown")),  # type: ignore[arg-type]
                                raw=raw or None,
                                details=details,
                            )
                        )

                        if kv and raw:
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

                            src_key = "|".join([p for p in [src_type, server, database, value] if p])
                            src_node = graph.upsert(
                                Source.make(
                                    source_type=src_type,  # type: ignore[arg-type]
                                    key=src_key,
                                    id=f"src:{src_key}",
                                    server=str(server) if server else None,
                                    database=str(database) if database else None,
                                    value=value,
                                    provider=str(provider) if provider else None,
                                )
                            )
                            graph.add_edge(conn_node.id, src_node.id, "uses_source")
                except Exception as e:  # noqa: BLE001
                    report.issues.append(f"connections extraction failed: {e}")

            # --- Formulas ---
            if ctx.options.include_formulas:
                max_cells = ctx.options.max_cells_per_sheet if ctx.options.max_cells_per_sheet is not None else 20000
                for ws in wb.Worksheets:
                    sheet_name = str(ws.Name)
                    sheet_key = " ".join(sheet_name.strip().split())
                    sheet = graph.get_by_key("sheet", sheet_key)
                    if not sheet:
                        sheet = graph.upsert(Sheet.make(key=sheet_key, id=f"sheet:{sheet_key}", name=sheet_name))

                    try:
                        used = ws.UsedRange
                    except Exception:
                        continue

                    scanned = 0
                    try:
                        top = int(getattr(used, "Row", 1) or 1)
                        left = int(getattr(used, "Column", 1) or 1)
                        rows = int(getattr(getattr(used, "Rows", None), "Count", 0) or 0)
                        cols = int(getattr(getattr(used, "Columns", None), "Count", 0) or 0)

                        # Range.Formula returns a scalar for 1x1 or a 2D array for larger ranges.
                        formulas = used.Formula

                        def _iter_cells_formulas() -> list[tuple[int, int, str]]:
                            items: list[tuple[int, int, str]] = []
                            if rows <= 0 or cols <= 0:
                                return items

                            # Normalize to 2D array shape.
                            if rows == 1 and cols == 1:
                                val = formulas
                                if isinstance(val, str) and val.startswith("="):
                                    items.append((top, left, val))
                                return items

                            for r_idx, row_vals in enumerate(formulas, start=0):
                                # pywin32 may give a tuple for each row
                                for c_idx, val in enumerate(row_vals, start=0):
                                    if not isinstance(val, str) or not val.startswith("="):
                                        continue
                                    items.append((top + r_idx, left + c_idx, val))
                            return items

                        for r, c, formula in _iter_cells_formulas():
                            scanned += 1
                            if scanned > max_cells:
                                report.issues.append(f"{sheet_name}: truncated formulas to {max_cells}")
                                break
                            addr = f"{_col_to_name(c)}{r}"
                            key = f"{sheet_name}!{addr}"
                            node = graph.upsert(
                                FormulaCell.make(
                                    key=key,
                                    id=f"formula:{key}",
                                    sheet_name=sheet_name,
                                    address=addr,
                                    formula=formula,
                                )
                            )
                            graph.add_edge(sheet.id, node.id, "contains")
                    except Exception as e:  # noqa: BLE001
                        report.issues.append(f"{sheet_name}: formula scan failed: {e}")

            report.stats = graph.stats()
            return report

        except Exception as e:  # noqa: BLE001
            report.issues.append(f"excel com extraction failed: {e}")
            report.stats = graph.stats()
            return report

        finally:
            try:
                if wb is not None:
                    wb.Close(SaveChanges=False)
            except Exception:
                pass
            try:
                if xl is not None:
                    xl.Quit()
            except Exception:
                pass

            try:
                if pythoncom is not None and com_initialized:
                    pythoncom.CoUninitialize()
            except Exception:
                pass
