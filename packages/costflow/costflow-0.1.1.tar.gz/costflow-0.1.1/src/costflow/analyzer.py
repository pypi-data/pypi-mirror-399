from __future__ import annotations

import gc
import math
import time
from typing import Any, Callable, Dict, List, Tuple

import pandas as pd

from .models import AnalysisReport, OpEvent, PipelineRun
from .utils import get_rss_bytes, bytes_to_mb
from .tracing import DFProxy
from .fitting import fit_scaling_models, predict_from_fit


def analyze(
    pipeline_fn: Callable[[Any], Any],
    make_df: Callable[[int], pd.DataFrame],
    sizes: List[int],
    trace_ops: bool = True,
    warmup: bool = True,
    gc_collect: bool = True,
) -> AnalysisReport:
    runs: List[PipelineRun] = []

    # warmup (optional)
    if warmup and sizes:
        df0 = make_df(max(1000, min(sizes)))
        _ = pipeline_fn(df0 if not trace_ops else DFProxy(df0, []))
        del df0, _
        if gc_collect:
            gc.collect()

    for n in sizes:
        if gc_collect:
            gc.collect()

        df = make_df(n)
        events: List[OpEvent] = []

        rss0 = get_rss_bytes()
        peak_rss = rss0

        t0 = time.perf_counter()

        if trace_ops:
            out = pipeline_fn(DFProxy(df, events))
            if isinstance(out, DFProxy):
                out_df = out.df
            else:
                out_df = out
        else:
            out_df = pipeline_fn(df)

        wall = time.perf_counter() - t0

        rss1 = get_rss_bytes()
        if rss0 is not None and rss1 is not None:
            peak_rss = max(rss0, rss1)

        peak_mb = None
        if peak_rss is not None:
            peak_mb = float(bytes_to_mb(peak_rss))

        runs.append(
            PipelineRun(
                n_rows=int(df.shape[0]),
                n_cols=int(df.shape[1]),
                wall_time_s=float(wall),
                peak_rss_mb=peak_mb,
                op_events=events,
            )
        )

        # cleanup
        del df, out_df
        if gc_collect:
            gc.collect()

    # candidate models
    time_candidates: List[Tuple[str, List[str]]] = [
        ("a*n", ["1", "n"]),
        ("a*nlogn", ["1", "nlogn"]),
        ("a*n + b*nlogn", ["1", "n", "nlogn"]),
        ("a*n2", ["1", "n2"]),
        ("a*nm", ["1", "nm"]),
    ]
    mem_candidates: List[Tuple[str, List[str]]] = [
        ("a*n", ["1", "n"]),
        ("a*nm", ["1", "nm"]),
    ]

    time_fit = fit_scaling_models(runs, "time", time_candidates)
    mem_fit = fit_scaling_models(runs, "memory", mem_candidates)

    # dominant ops
    op_time: Dict[str, float] = {}
    traced_total = 0.0
    for r in runs:
        for e in r.op_events:
            op_time[e.op_name] = op_time.get(e.op_name, 0.0) + e.duration_s
            traced_total += e.duration_s

    dominant_ops: List[Tuple[str, float]] = []
    if traced_total > 0:
        dominant_ops = sorted(
            [(k, v / traced_total) for k, v in op_time.items()],
            key=lambda x: x[1],
            reverse=True,
        )

    # projections
    projections: Dict[str, Any] = {}
    if runs:
        m_ref = runs[-1].n_cols
        projections["reference_n"] = runs[-1].n_rows

        for n_target in [100_000, 1_000_000, 10_000_000]:
            projections[f"projected_time_at_{n_target}"] = predict_from_fit(time_fit.coefficients, n_target, m_ref)

            if not math.isnan(mem_fit.r2) and mem_fit.chosen_model != "N/A":
                projections[f"projected_peak_rss_mb_at_{n_target}"] = predict_from_fit(mem_fit.coefficients, n_target, m_ref)

    return AnalysisReport(
        runs=runs,
        time_fit=time_fit,
        mem_fit=mem_fit,
        dominant_ops=dominant_ops[:10],
        projections=projections,
    )


def analyze_with_df(
    pipeline_fn: Callable[[Any], Any],
    base_df: pd.DataFrame,
    sizes: List[int],
    trace_ops: bool = True,
    warmup: bool = True,
    gc_collect: bool = True,
) -> AnalysisReport:
    """
    Convenience wrapper: resample a provided DataFrame to requested sizes
    (sampling with replacement when scaling up) and run analyze().

    Use when you already have a representative dataset and don't want to write
    a custom make_df. The schema/dtypes of base_df are preserved.
    """
    base_df = base_df.copy()
    n_base = len(base_df)
    assert n_base > 0, "base_df must have at least one row"

    def _resample(target_n: int) -> pd.DataFrame:
        if target_n <= n_base:
            return base_df.sample(n=target_n, replace=False, random_state=0).reset_index(drop=True)
        k, r = divmod(target_n, n_base)
        return pd.concat(
            [base_df] * k + [base_df.sample(n=r, replace=True, random_state=0)],
            ignore_index=True,
        )

    return analyze(
        pipeline_fn=pipeline_fn,
        make_df=_resample,
        sizes=sizes,
        trace_ops=trace_ops,
        warmup=warmup,
        gc_collect=gc_collect,
    )
