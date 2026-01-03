from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from excelminer.backends.base import AnalysisContext, BackendReport
from excelminer.backends.ooxml_zip import _is_ooxml_excel
from excelminer.model.entities import Entity
from excelminer.model.graph import WorkbookGraph


@dataclass(slots=True)
class VbaZipBackend:
    """Detect VBA projects embedded in OOXML workbooks.

    For macro-enabled OOXML formats (like `.xlsm`), VBA is typically stored in
    `xl/vbaProject.bin`.

    This backend intentionally does not attempt to parse the binary OLE container.
    It emits a `vba_project` node with basic metadata so downstream systems can
    detect the presence of macros.
    """

    name: str = "vba_zip"

    def can_handle(self, ctx: AnalysisContext) -> bool:
        p = ctx.path
        if not ctx.options.include_vba:
            return False
        if not p.exists() or not p.is_file():
            return False
        if p.suffix.lower() not in (".xlsm", ".xltm", ".xlam"):
            return False
        try:
            with zipfile.ZipFile(p):
                return True
        except zipfile.BadZipFile:
            return False

    def extract(self, ctx: AnalysisContext, graph: WorkbookGraph) -> BackendReport:
        report = BackendReport(backend=self.name)
        p: Path = ctx.path

        try:
            with zipfile.ZipFile(p) as zf:
                if not _is_ooxml_excel(zf):
                    report.issues.append("not an OOXML Excel workbook")
                    report.stats = graph.stats()
                    return report

                vba_parts: list[dict[str, Any]] = []
                for name in zf.namelist():
                    if name.lower().endswith("vbaproject.bin"):
                        try:
                            info = zf.getinfo(name)
                            vba_parts.append({"part": name, "size": int(getattr(info, "file_size", 0) or 0)})
                        except KeyError:
                            continue

                if not vba_parts:
                    report.stats = {"vba_projects": 0, **graph.stats()}
                    return report

                vba_parts = sorted(vba_parts, key=lambda d: str(d.get("part") or ""))

                key = str(ctx.path.name)
                node = Entity(
                    kind="vba_project",
                    id=f"vba:{key}",
                    key=key,
                    attrs={
                        "file": str(ctx.path.name),
                        "parts": vba_parts,
                        "has_vba": True,
                    },
                )
                graph.upsert(node)

                report.stats = {"vba_projects": 1, **graph.stats()}
                return report

        except Exception as e:  # noqa: BLE001
            report.issues.append(str(e))
            report.stats = graph.stats()
            return report
