from __future__ import annotations

from .api import analyze_to_dict, analyze_workbook
from .backends.base import AnalysisContext, AnalysisOptions, Backend, BackendReport
from .backends.pivot_zip import PivotZipBackend
from .backends.powerquery_zip import PowerQueryZipBackend
from .model.graph import WorkbookGraph

__version__ = "0.0.0"

__all__ = [
    "__version__",
    "AnalysisContext",
    "AnalysisOptions",
    "Backend",
    "BackendReport",
    "PivotZipBackend",
    "PowerQueryZipBackend",
    "WorkbookGraph",
    "analyze_workbook",
    "analyze_to_dict",
]
