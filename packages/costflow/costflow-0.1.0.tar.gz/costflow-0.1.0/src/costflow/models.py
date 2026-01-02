from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class OpEvent:
    op_name: str
    duration_s: float
    in_shape: Tuple[int, int]
    out_shape: Tuple[int, int]
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineRun:
    n_rows: int
    n_cols: int
    wall_time_s: float
    peak_rss_mb: Optional[float]
    op_events: List[OpEvent] = field(default_factory=list)


@dataclass
class FitResult:
    target: str  # "time" or "memory"
    chosen_model: str
    coefficients: Dict[str, float]
    r2: float
    rmse: float
    notes: str = ""


@dataclass
class AnalysisReport:
    runs: List[PipelineRun]
    time_fit: FitResult
    mem_fit: FitResult
    dominant_ops: List[Tuple[str, float]]  # (op_name, fraction_of_traced_time)
    projections: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        import json
        return json.dumps(self.to_dict(), indent=indent, default=str)
