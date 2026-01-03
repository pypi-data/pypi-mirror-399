from __future__ import annotations

from typing import Any, Dict, Optional
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


def plot_report(report: AnalysisReport, show_memory: bool = True, ax: Optional[Any] = None) -> Any:
    """
    Plot size vs time (and optionally memory) from a report using matplotlib.
    Returns the matplotlib Axes or a tuple of Axes when memory is shown.
    """
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        raise RuntimeError("plot_report requires matplotlib. Install with 'pip install matplotlib'.") from exc

    sizes = [r.n_rows for r in report.runs]
    times = [r.wall_time_s for r in report.runs]
    mems = [r.peak_rss_mb for r in report.runs]
    has_mem = any(m is not None for m in mems)

    if ax is not None:
        axes = [ax]
    else:
        if show_memory and has_mem:
            fig, (ax_time, ax_mem) = plt.subplots(1, 2, figsize=(10, 4))
            axes = [ax_time, ax_mem]
        else:
            fig, ax_time = plt.subplots(1, 1, figsize=(6, 4))
            axes = [ax_time]

    axes[0].plot(sizes, times, marker="o")
    axes[0].set_xlabel("Rows")
    axes[0].set_ylabel("Wall time (s)")
    axes[0].set_title("Scaling: time")

    if show_memory and has_mem and len(axes) > 1:
        axes[1].plot(sizes, mems, marker="o", color="tab:orange")
        axes[1].set_xlabel("Rows")
        axes[1].set_ylabel("Peak RSS (MB)")
        axes[1].set_title("Scaling: memory")
        return tuple(axes)

    return axes[0]
