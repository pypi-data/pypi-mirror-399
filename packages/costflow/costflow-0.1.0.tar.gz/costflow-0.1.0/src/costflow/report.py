from __future__ import annotations

from typing import Any, Dict
from .models import AnalysisReport


def pretty_print(report: AnalysisReport) -> None:
    print("\n=== CostFlow Report ===")

    print("\nRuns:")
    for r in report.runs:
        rss = "N/A" if r.peak_rss_mb is None else f"{r.peak_rss_mb:.1f} MB"
        print(f"  n={r.n_rows:,}  cols={r.n_cols}  time={r.wall_time_s:.3f}s  peak_rss={rss}")

    print("\nTime model:")
    print(f"  chosen: {report.time_fit.chosen_model}")
    print(f"  r2={report.time_fit.r2:.3f}  rmse={report.time_fit.rmse:.4f}")
    print(f"  coeffs: {report.time_fit.coefficients}")

    print("\nMemory model:")
    print(f"  chosen: {report.mem_fit.chosen_model}")
    print(f"  r2={report.mem_fit.r2:.3f}  rmse={report.mem_fit.rmse:.4f}")
    print(f"  coeffs: {report.mem_fit.coefficients}")
    if report.mem_fit.notes:
        print(f"  note: {report.mem_fit.notes}")

    if report.dominant_ops:
        print("\nDominant pandas ops (by traced time):")
        for op, frac in report.dominant_ops[:10]:
            print(f"  {op:20s} {frac*100:5.1f}%")
    else:
        print("\nDominant pandas ops: (tracing disabled or no events)")

    print("\nProjections:")
    for k, v in report.projections.items():
        print(f"  {k}: {v}")


def to_json_dict(report: AnalysisReport) -> Dict[str, Any]:
    return report.to_dict()
