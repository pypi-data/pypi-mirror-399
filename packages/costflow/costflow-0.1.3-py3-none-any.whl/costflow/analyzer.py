from __future__ import annotations

import gc
import inspect
import math
import time
from typing import Any, Callable, Dict, List, Tuple

import pandas as pd

from .models import AnalysisReport, OpEvent, PipelineRun
from .utils import get_rss_bytes, bytes_to_mb
from .tracing import DFProxy
from .fitting import fit_scaling_models, predict_from_fit


def _wrap_for_trace(obj: Any, events: List[OpEvent]) -> Any:
    if isinstance(obj, pd.DataFrame):
        return DFProxy(obj, events)
    if isinstance(obj, tuple):
        return tuple(_wrap_for_trace(v, events) for v in obj)
    if isinstance(obj, list):
        return [_wrap_for_trace(v, events) for v in obj]
    if isinstance(obj, dict):
        return {k: _wrap_for_trace(v, events) for k, v in obj.items()}
    return obj


def _should_unpack(pipeline_fn: Callable[..., Any], args: Tuple[Any, ...]) -> bool:
    try:
        sig = inspect.signature(pipeline_fn)
    except (TypeError, ValueError):
        return False

    params = list(sig.parameters.values())
    if any(p.kind == inspect.Parameter.VAR_POSITIONAL for p in params):
        return True

    positional = [p for p in params if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)]
    return len(positional) > 1 and len(args) <= len(positional)


def _call_pipeline(pipeline_fn: Callable[..., Any], data: Any) -> Any:
    if isinstance(data, (list, tuple)):
        args = tuple(data)
        if _should_unpack(pipeline_fn, args):
            return pipeline_fn(*args)
    return pipeline_fn(data)


def analyze(
    pipeline_fn: Callable[[Any], Any],
    make_df: Callable[[int], Any],
    sizes: List[int],
    trace_ops: bool = True,
    warmup: bool = True,
    gc_collect: bool = True,
) -> AnalysisReport:
    runs: List[PipelineRun] = []

    # warmup (optional)
    if warmup and sizes:
        df0 = make_df(max(1000, min(sizes)))
        warm_events: List[OpEvent] = []
        warm_input = _wrap_for_trace(df0, warm_events) if trace_ops else df0
        if trace_ops:
            from .tracing import top_level_tracer
            with top_level_tracer(warm_events):
                _ = _call_pipeline(pipeline_fn, warm_input)
        else:
            _ = _call_pipeline(pipeline_fn, warm_input)
        del df0, warm_input, _
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
            from .tracing import top_level_tracer
            wrapped_input = _wrap_for_trace(df, events)
            with top_level_tracer(events):
                out = _call_pipeline(pipeline_fn, wrapped_input)
            if isinstance(out, DFProxy):
                out_df = out.df
            else:
                out_df = out
        else:
            out_df = _call_pipeline(pipeline_fn, df)

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


def analyze_with_dfs(
    pipeline_fn: Callable[..., Any],
    base_dfs: List[pd.DataFrame],
    sizes: List[int],
    trace_ops: bool = True,
    warmup: bool = True,
    gc_collect: bool = True,
) -> AnalysisReport:
    """
    Convenience wrapper for multiple DataFrames. Each DataFrame in base_dfs is
    resampled to the requested size and passed to pipeline_fn.
    """
    if not base_dfs:
        raise ValueError("base_dfs must contain at least one DataFrame")
    bases = [df.copy() for df in base_dfs]
    base_lengths = [len(df) for df in bases]
    if any(n == 0 for n in base_lengths):
        raise ValueError("all base_dfs must have at least one row")

    def _resample(target_n: int):
        sampled = []
        for df, n_base in zip(bases, base_lengths):
            if target_n <= n_base:
                sampled.append(df.sample(n=target_n, replace=False, random_state=0).reset_index(drop=True))
            else:
                k, r = divmod(target_n, n_base)
                sampled.append(
                    pd.concat(
                        [df] * k + [df.sample(n=r, replace=True, random_state=0)],
                        ignore_index=True,
                    )
                )
        return tuple(sampled)

    return analyze(
        pipeline_fn=pipeline_fn,
        make_df=_resample,
        sizes=sizes,
        trace_ops=trace_ops,
        warmup=warmup,
        gc_collect=gc_collect,
    )
