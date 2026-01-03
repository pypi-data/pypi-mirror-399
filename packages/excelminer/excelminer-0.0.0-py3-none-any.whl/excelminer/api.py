from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable

from excelminer.backends import (
    AnalysisContext,
    AnalysisOptions,
    Backend,
    BackendReport,
    CalamineBackend,
    ComBackend,
    OOXMLZipBackend,
    OpenpyxlBackend,
    PivotZipBackend,
    PowerQueryZipBackend,
    VbaZipBackend,
)
from excelminer.model.graph import WorkbookGraph


def _default_backends() -> list[Backend]:
    # Ordered from structural -> semantic -> enrichment.
    return [
        OOXMLZipBackend(),
        VbaZipBackend(),
        PowerQueryZipBackend(),
        PivotZipBackend(),
        CalamineBackend(),
        OpenpyxlBackend(),
        ComBackend(),
    ]


def analyze_workbook(
    path: str | Path,
    *,
    options: AnalysisOptions | None = None,
    backends: Iterable[Backend] | None = None,
) -> tuple[WorkbookGraph, list[BackendReport], AnalysisContext]:
    ctx = AnalysisContext(path=Path(path), options=options or AnalysisOptions())
    graph = WorkbookGraph()

    reports: list[BackendReport] = []
    for backend in (list(backends) if backends is not None else _default_backends()):
        try:
            if not backend.can_handle(ctx):
                continue
            report = backend.extract(ctx, graph)
        except Exception as e:  # noqa: BLE001
            ctx.add_issue(f"backend {getattr(backend, 'name', type(backend).__name__)} failed: {e}")
            report = BackendReport(backend=getattr(backend, "name", type(backend).__name__), issues=[str(e)])
        reports.append(report)

    return graph, reports, ctx


def analyze_to_dict(
    path: str | Path,
    *,
    options: AnalysisOptions | None = None,
    backends: Iterable[Backend] | None = None,
) -> dict[str, Any]:
    graph, reports, ctx = analyze_workbook(path, options=options, backends=backends)
    return {
        "path": str(ctx.path),
        "options": asdict(ctx.options),
        "issues": list(ctx.issues),
        "reports": [asdict(r) for r in reports],
        "graph": graph.to_dict(),
    }
