import numpy as np
import pandas as pd

from costflow import analyze


def make_df(n: int) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    return pd.DataFrame({"k": rng.integers(0, max(1, n // 10), size=n), "x": rng.normal(size=n)})


def pipeline(df):
    return df.groupby("k").agg(x_mean=("x", "mean")).sort_values("x_mean")


def test_analyze_runs():
    report = analyze(pipeline, make_df, sizes=[1000, 2000], trace_ops=True)
    assert len(report.runs) == 2
    assert report.time_fit.target == "time"
