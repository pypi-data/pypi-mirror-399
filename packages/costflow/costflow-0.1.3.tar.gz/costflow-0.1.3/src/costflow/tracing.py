from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Any, Dict, List, Tuple

import pandas as pd

from .models import OpEvent


def _unwrap_df_arg(obj: Any) -> Any:
    """Return underlying DataFrame/Series when a DFProxy is passed into pandas APIs."""
    if isinstance(obj, DFProxy):
        return obj.df
    if isinstance(obj, SeriesProxy):
        return obj.series
    return obj


def _unwrap_nested(obj: Any) -> Any:
    if isinstance(obj, (list, tuple)):
        return type(obj)(_unwrap_nested(v) for v in obj)
    if isinstance(obj, dict):
        return {k: _unwrap_nested(v) for k, v in obj.items()}
    return _unwrap_df_arg(obj)


@contextmanager
def top_level_tracer(events: List[OpEvent]):
    """
    Context manager to trace common top-level pandas functions.
    Currently wraps pd.concat and pd.merge.
    """
    orig_concat = pd.concat
    orig_merge = pd.merge

    def wrap_concat(objs, *args, **kwargs):
        t0 = time.perf_counter()
        clean_objs = _unwrap_nested(objs)
        clean_args = tuple(_unwrap_nested(a) for a in args)
        clean_kwargs = {k: _unwrap_nested(v) for k, v in kwargs.items()}
        out = orig_concat(clean_objs, *clean_args, **clean_kwargs)
        dt = time.perf_counter() - t0
        out_shape = out.shape if isinstance(out, pd.DataFrame) else (len(out), 1) if hasattr(out, "__len__") else (-1, -1)
        events.append(
            OpEvent(
                op_name="pd.concat",
                duration_s=dt,
                in_shape=(-1, -1),
                out_shape=out_shape,
                meta={"objs": len(objs) if hasattr(objs, "__len__") else "unknown"},
            )
        )
        if isinstance(out, pd.DataFrame):
            return DFProxy(out, events)
        if isinstance(out, pd.Series):
            return SeriesProxy(out, events)
        return out

    def wrap_merge(left, right, *args, **kwargs):
        t0 = time.perf_counter()
        clean_left = _unwrap_df_arg(left)
        clean_right = _unwrap_df_arg(right)
        clean_args = tuple(_unwrap_nested(a) for a in args)
        clean_kwargs = {k: _unwrap_nested(v) for k, v in kwargs.items()}
        out = orig_merge(clean_left, clean_right, *clean_args, **clean_kwargs)
        dt = time.perf_counter() - t0
        out_shape = out.shape if isinstance(out, pd.DataFrame) else (len(out), 1) if hasattr(out, "__len__") else (-1, -1)
        events.append(
            OpEvent(
                op_name="pd.merge",
                duration_s=dt,
                in_shape=(getattr(clean_left, "shape", (-1, -1))),
                out_shape=out_shape,
                meta={"how": kwargs.get("how"), "on": kwargs.get("on")},
            )
        )
        if isinstance(out, pd.DataFrame):
            return DFProxy(out, events)
        if isinstance(out, pd.Series):
            return SeriesProxy(out, events)
        return out

    pd.concat = wrap_concat  # type: ignore
    pd.merge = wrap_merge  # type: ignore
    try:
        yield
    finally:
        pd.concat = orig_concat  # type: ignore
        pd.merge = orig_merge  # type: ignore


class DFProxy:
    """
    Wraps a pandas DataFrame and intercepts common expensive methods.
    Best-effort tracing; not all pandas internals are captured.
    """

    __slots__ = ("_df", "_events", "_label")

    def __init__(self, df: pd.DataFrame, events: List[OpEvent], label: str = "df"):
        self._df = df
        self._events = events
        self._label = label

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    def __len__(self) -> int:
        # allow len(proxy) in pipelines without unwrapping
        return len(self._df)

    def __iter__(self):
        # needed so `x in df_proxy` doesn't fall back to __getitem__(0)
        return iter(self._df)

    def __contains__(self, item: Any) -> bool:
        return item in self._df

    def _wrap(self, out: Any, op_name: str, t0: float, in_shape: Tuple[int, int], meta: Dict[str, Any]) -> Any:
        dt = time.perf_counter() - t0

        if isinstance(out, pd.DataFrame):
            out_shape = out.shape
        elif isinstance(out, pd.Series):
            out_shape = (len(out), 1)
        else:
            out_shape = (-1, -1)

        self._events.append(
            OpEvent(op_name=op_name, duration_s=dt, in_shape=in_shape, out_shape=out_shape, meta=meta)
        )

        if isinstance(out, pd.DataFrame):
            return DFProxy(out, self._events, label=self._label)
        if isinstance(out, pd.Series):
            return SeriesProxy(out, self._events, label=self._label)

        return out

    # --- frequently expensive ops ---
    def merge(self, *args, **kwargs):
        in_shape = self._df.shape
        t0 = time.perf_counter()
        clean_args = tuple(_unwrap_df_arg(a) for a in args)
        clean_kwargs = {k: _unwrap_df_arg(v) for k, v in kwargs.items()}
        out = self._df.merge(*clean_args, **clean_kwargs)
        meta = {
            "how": kwargs.get("how"),
            "on": kwargs.get("on"),
            "left_on": kwargs.get("left_on"),
            "right_on": kwargs.get("right_on"),
        }
        return self._wrap(out, "merge", t0, in_shape, meta)

    def join(self, *args, **kwargs):
        in_shape = self._df.shape
        t0 = time.perf_counter()
        clean_args = tuple(_unwrap_df_arg(a) for a in args)
        clean_kwargs = {k: _unwrap_df_arg(v) for k, v in kwargs.items()}
        out = self._df.join(*clean_args, **clean_kwargs)
        meta = {"how": kwargs.get("how"), "on": kwargs.get("on")}
        return self._wrap(out, "join", t0, in_shape, meta)

    def sort_values(self, *args, **kwargs):
        in_shape = self._df.shape
        t0 = time.perf_counter()
        out = self._df.sort_values(*args, **kwargs)
        meta = {"by": kwargs.get("by"), "ascending": kwargs.get("ascending")}
        return self._wrap(out, "sort_values", t0, in_shape, meta)

    def sort_index(self, *args, **kwargs):
        in_shape = self._df.shape
        t0 = time.perf_counter()
        out = self._df.sort_index(*args, **kwargs)
        meta = {"axis": kwargs.get("axis"), "ascending": kwargs.get("ascending")}
        return self._wrap(out, "sort_index", t0, in_shape, meta)

    def pivot_table(self, *args, **kwargs):
        in_shape = self._df.shape
        t0 = time.perf_counter()
        clean_args = tuple(_unwrap_df_arg(a) for a in args)
        clean_kwargs = {k: _unwrap_df_arg(v) for k, v in kwargs.items()}
        out = self._df.pivot_table(*clean_args, **clean_kwargs)
        meta = {
            "index": kwargs.get("index"),
            "columns": kwargs.get("columns"),
            "values": kwargs.get("values"),
            "aggfunc": str(kwargs.get("aggfunc")),
        }
        return self._wrap(out, "pivot_table", t0, in_shape, meta)

    def explode(self, *args, **kwargs):
        in_shape = self._df.shape
        t0 = time.perf_counter()
        out = self._df.explode(*args, **kwargs)
        meta = {"column": args[0] if args else kwargs.get("column")}
        return self._wrap(out, "explode", t0, in_shape, meta)

    def astype(self, *args, **kwargs):
        in_shape = self._df.shape
        t0 = time.perf_counter()
        out = self._df.astype(*args, **kwargs)
        meta = {"dtype": str(args[0]) if args else str(kwargs.get("dtype"))}
        return self._wrap(out, "astype", t0, in_shape, meta)

    def fillna(self, *args, **kwargs):
        in_shape = self._df.shape
        t0 = time.perf_counter()
        out = self._df.fillna(*args, **kwargs)
        meta = {"value": kwargs.get("value", None)}
        return self._wrap(out, "fillna", t0, in_shape, meta)

    def groupby(self, *args, **kwargs):
        gb = self._df.groupby(*args, **kwargs)
        by_val = kwargs.get("by", args[0] if args else None)
        return GroupByProxy(
            gb,
            events=self._events,
            parent_shape=self._df.shape,
            meta={"by": str(by_val)[:200]},
        )

    # selection and assignment (often copy-related)
    def __getitem__(self, item):
        in_shape = self._df.shape
        t0 = time.perf_counter()
        out = self._df.__getitem__(_unwrap_df_arg(item))
        meta = {"item": str(item)[:200]}
        return self._wrap(out, "__getitem__", t0, in_shape, meta)

    def __setitem__(self, key, value):
        in_shape = self._df.shape
        t0 = time.perf_counter()
        self._df.__setitem__(key, value)
        dt = time.perf_counter() - t0
        self._events.append(
            OpEvent(
                op_name="__setitem__",
                duration_s=dt,
                in_shape=in_shape,
                out_shape=self._df.shape,
                meta={"key": str(key)[:200]},
            )
        )

    # fallback: anything not explicitly wrapped just uses pandas
    def __getattr__(self, name: str):
        attr = getattr(self._df, name)

        if callable(attr):
            def wrapper(*args, **kwargs):
                in_shape = self._df.shape
                t0 = time.perf_counter()
                clean_args = tuple(_unwrap_df_arg(a) for a in args)
                clean_kwargs = {k: _unwrap_df_arg(v) for k, v in kwargs.items()}
                out = attr(*clean_args, **clean_kwargs)
                meta = {
                    "method": name,
                    "args": len(args),
                    "kwargs": list(kwargs.keys())[:10],
                }
                return self._wrap(out, f"df.{name}", t0, in_shape, meta)

            return wrapper

        return attr


class GroupByProxy:
    __slots__ = ("_gb", "_events", "_parent_shape", "_meta")

    def __init__(self, gb: Any, events: List[OpEvent], parent_shape: Tuple[int, int], meta: Dict[str, Any]):
        self._gb = gb
        self._events = events
        self._parent_shape = parent_shape
        self._meta = meta

    def _wrap(self, out: Any, op_name: str, t0: float, meta_extra: Dict[str, Any]) -> Any:
        dt = time.perf_counter() - t0

        if isinstance(out, pd.DataFrame):
            out_shape = out.shape
        elif isinstance(out, pd.Series):
            out_shape = (len(out), 1)
        else:
            out_shape = (-1, -1)

        meta = {**self._meta, **meta_extra}
        self._events.append(
            OpEvent(op_name=op_name, duration_s=dt, in_shape=self._parent_shape, out_shape=out_shape, meta=meta)
        )

        if isinstance(out, pd.DataFrame):
            return DFProxy(out, self._events)
        if isinstance(out, pd.Series):
            return SeriesProxy(out, self._events)

        return out

    def agg(self, *args, **kwargs):
        t0 = time.perf_counter()
        out = self._gb.agg(*args, **kwargs)
        meta_extra = {"agg": str(args[0])[:200] if args else str(kwargs)[:200]}
        return self._wrap(out, "groupby_agg", t0, meta_extra)

    def apply(self, *args, **kwargs):
        t0 = time.perf_counter()
        out = self._gb.apply(*args, **kwargs)
        meta_extra = {"func": getattr(args[0], "__name__", "callable") if args else "unknown"}
        return self._wrap(out, "groupby_apply", t0, meta_extra)

    def transform(self, *args, **kwargs):
        t0 = time.perf_counter()
        out = self._gb.transform(*args, **kwargs)
        meta_extra = {"func": getattr(args[0], "__name__", "callable") if args else "unknown"}
        return self._wrap(out, "groupby_transform", t0, meta_extra)

    def __getattr__(self, name: str):
        attr = getattr(self._gb, name)

        if callable(attr):
            def wrapper(*args, **kwargs):
                t0 = time.perf_counter()
                clean_args = tuple(_unwrap_df_arg(a) for a in args)
                clean_kwargs = {k: _unwrap_df_arg(v) for k, v in kwargs.items()}
                out = attr(*clean_args, **clean_kwargs)
                meta_extra = {"method": name, "args": len(args), "kwargs": list(kwargs.keys())[:10]}
                return self._wrap(out, f"groupby.{name}", t0, meta_extra)

            return wrapper

        return attr


class SeriesProxy:
    """
    Wraps a pandas Series and intercepts common operations for tracing.
    """

    __slots__ = ("_series", "_events", "_label")

    def __init__(self, series: pd.Series, events: List[OpEvent], label: str = "series"):
        self._series = series
        self._events = events
        self._label = label

    @property
    def series(self) -> pd.Series:
        return self._series

    def __len__(self) -> int:
        return len(self._series)

    def _wrap(self, out: Any, op_name: str, t0: float, meta: Dict[str, Any]) -> Any:
        dt = time.perf_counter() - t0

        if isinstance(out, pd.DataFrame):
            out_shape = out.shape
        elif isinstance(out, pd.Series):
            out_shape = (len(out), 1)
        else:
            out_shape = (-1, -1)

        self._events.append(
            OpEvent(
                op_name=op_name,
                duration_s=dt,
                in_shape=(len(self._series), 1),
                out_shape=out_shape,
                meta=meta,
            )
        )

        if isinstance(out, pd.DataFrame):
            return DFProxy(out, self._events, label=self._label)
        if isinstance(out, pd.Series):
            return SeriesProxy(out, self._events, label=self._label)
        return out

    def __getitem__(self, item):
        t0 = time.perf_counter()
        out = self._series.__getitem__(_unwrap_df_arg(item))
        meta = {"item": str(item)[:200]}
        return self._wrap(out, "series.__getitem__", t0, meta)

    def __setitem__(self, key, value):
        t0 = time.perf_counter()
        self._series.__setitem__(key, value)
        dt = time.perf_counter() - t0
        self._events.append(
            OpEvent(
                op_name="series.__setitem__",
                duration_s=dt,
                in_shape=(len(self._series), 1),
                out_shape=(len(self._series), 1),
                meta={"key": str(key)[:200]},
            )
        )

    def __getattr__(self, name: str):
        attr = getattr(self._series, name)

        if callable(attr):
            def wrapper(*args, **kwargs):
                t0 = time.perf_counter()
                clean_args = tuple(_unwrap_df_arg(a) for a in args)
                clean_kwargs = {k: _unwrap_df_arg(v) for k, v in kwargs.items()}
                out = attr(*clean_args, **clean_kwargs)
                meta = {
                    "method": name,
                    "args": len(args),
                    "kwargs": list(kwargs.keys())[:10],
                }
                return self._wrap(out, f"series.{name}", t0, meta)

            return wrapper

        return attr

    def _binop(self, op_name: str, other: Any, op) -> Any:
        t0 = time.perf_counter()
        out = op(self._series, _unwrap_df_arg(other))
        return self._wrap(out, op_name, t0, {"other_type": type(other).__name__})

    def _rbinop(self, op_name: str, other: Any, op) -> Any:
        t0 = time.perf_counter()
        out = op(_unwrap_df_arg(other), self._series)
        return self._wrap(out, op_name, t0, {"other_type": type(other).__name__})

    def __add__(self, other: Any) -> Any:
        return self._binop("series.__add__", other, lambda a, b: a + b)

    def __radd__(self, other: Any) -> Any:
        return self._rbinop("series.__radd__", other, lambda a, b: a + b)

    def __sub__(self, other: Any) -> Any:
        return self._binop("series.__sub__", other, lambda a, b: a - b)

    def __rsub__(self, other: Any) -> Any:
        return self._rbinop("series.__rsub__", other, lambda a, b: a - b)

    def __mul__(self, other: Any) -> Any:
        return self._binop("series.__mul__", other, lambda a, b: a * b)

    def __rmul__(self, other: Any) -> Any:
        return self._rbinop("series.__rmul__", other, lambda a, b: a * b)

    def __truediv__(self, other: Any) -> Any:
        return self._binop("series.__truediv__", other, lambda a, b: a / b)

    def __rtruediv__(self, other: Any) -> Any:
        return self._rbinop("series.__rtruediv__", other, lambda a, b: a / b)

    def __floordiv__(self, other: Any) -> Any:
        return self._binop("series.__floordiv__", other, lambda a, b: a // b)

    def __rfloordiv__(self, other: Any) -> Any:
        return self._rbinop("series.__rfloordiv__", other, lambda a, b: a // b)

    def __pow__(self, other: Any) -> Any:
        return self._binop("series.__pow__", other, lambda a, b: a**b)

    def __rpow__(self, other: Any) -> Any:
        return self._rbinop("series.__rpow__", other, lambda a, b: a**b)

    def __neg__(self) -> Any:
        t0 = time.perf_counter()
        out = -self._series
        return self._wrap(out, "series.__neg__", t0, {})

    def __abs__(self) -> Any:
        t0 = time.perf_counter()
        out = abs(self._series)
        return self._wrap(out, "series.__abs__", t0, {})
