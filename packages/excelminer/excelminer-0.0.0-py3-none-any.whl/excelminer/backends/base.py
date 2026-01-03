from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from excelminer.model.graph import WorkbookGraph


@dataclass(slots=True)
class AnalysisOptions:
    """Flags + limits.

    Keep this minimal at first; expand as you add extractors.
    """

    include_vba: bool = True
    include_connections: bool = True
    include_powerquery: bool = True
    include_pivots: bool = True
    include_defined_names: bool = True

    # Explicit opt-in for Excel COM automation (Windows + Excel required)
    include_com: bool = False

    include_cells: bool = False  # value blocks, used ranges
    include_formulas: bool = False  # formula inventory + deps

    # Limits to keep scans bounded for huge workbooks
    max_sheets: int | None = None
    max_cells_per_sheet: int | None = None
    sample_rows_per_block: int = 10
    sample_cols_per_block: int = 12


@dataclass(slots=True)
class AnalysisContext:
    path: Path
    options: AnalysisOptions = field(default_factory=AnalysisOptions)
    issues: list[str] = field(default_factory=list)

    def add_issue(self, msg: str) -> None:
        self.issues.append(msg)


@dataclass(slots=True)
class BackendReport:
    backend: str
    issues: list[str] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)


class Backend(Protocol):
    """Backend interface.

    A backend may be structural (OOXML parsing), semantic (cell scanning), or
    OS-specific (COM).
    """

    name: str

    def can_handle(self, ctx: AnalysisContext) -> bool: ...

    def extract(self, ctx: AnalysisContext, graph: WorkbookGraph) -> BackendReport: ...


class BackendError(RuntimeError):
    pass
