import numpy as np
import pandas as pd

from costflow import analyze


def make_orders_df(n: int) -> pd.DataFrame:
    rng = np.random.default_rng(123)
    n_customers = max(20, n // 50)
    n_products = max(5, n // 100)
    return pd.DataFrame(
        {
            "customer_id": rng.integers(0, n_customers, size=n),
            "product_id": rng.integers(0, n_products, size=n),
            "region": rng.choice(["NA", "EU", "APAC", "LATAM"], size=n),
            "date": pd.date_range("2024-01-01", periods=n, freq="h"),
            "quantity": rng.integers(1, 10, size=n),
            "price": rng.normal(50, 12, size=n).clip(5),
            "discount": rng.uniform(0, 0.35, size=n),
            "category": rng.choice(["A", "B", "C"], size=n),
        }
    )


def revenue_by_customer(df):
    df["revenue"] = df["quantity"] * df["price"] * (1 - df["discount"])
    customer = (
        df.groupby("customer_id")
        .agg(
            total_revenue=("revenue", "sum"),
            orders=("quantity", "count"),
            avg_discount=("discount", "mean"),
        )
        .reset_index()
    )
    regional = (
        df.groupby(["customer_id", "region"])
        .agg(region_revenue=("revenue", "sum"))
        .reset_index()
        .pivot_table(index="customer_id", columns="region", values="region_revenue", fill_value=0.0)
    )
    out = customer.merge(regional, on="customer_id", how="left")
    return out.sort_values("total_revenue", ascending=False)


def weekly_region_rollup(df):
    df["revenue"] = df["quantity"] * df["price"] * (1 - df["discount"])
    df["week"] = df["date"].dt.to_period("W").dt.start_time
    weekly = (
        df.groupby(["week", "region"])
        .agg(revenue=("revenue", "sum"), buyers=("customer_id", "nunique"))
        .reset_index()
    )
    pivot = weekly.pivot_table(index="week", columns="region", values="revenue", fill_value=0.0)
    return pivot.sort_index()


def test_revenue_pipeline_scaling_and_ops():
    report = analyze(revenue_by_customer, make_orders_df, sizes=[500, 1200], trace_ops=True, warmup=False)
    assert [r.n_rows for r in report.runs] == [500, 1200]
    assert report.dominant_ops  # traced events should surface expensive pandas ops
    assert "projected_time_at_100000" in report.projections


def test_weekly_rollup_projection_and_fit():
    report = analyze(weekly_region_rollup, make_orders_df, sizes=[300, 900], trace_ops=True, warmup=False)
    assert report.time_fit.chosen_model != "N/A"
    assert report.runs[-1].n_cols >= 4
    assert report.projections.get("reference_n") == report.runs[-1].n_rows


def test_generic_method_tracing():
    def pipeline(df):
        # uses methods we don't explicitly wrap to ensure generic tracing kicks in
        return (
            df.assign(net=df["quantity"] * df["price"])
              .rename(columns={"net": "net_revenue"})
              .drop_duplicates(subset=["customer_id", "product_id"])
        )

    report = analyze(pipeline, make_orders_df, sizes=[100, 150], trace_ops=True, warmup=False)
    op_names = [e.op_name for r in report.runs for e in r.op_events]
    assert any(name.startswith("df.assign") for name in op_names)
    assert any(name.startswith("df.rename") for name in op_names)


def test_trace_off_still_runs():
    report = analyze(revenue_by_customer, make_orders_df, sizes=[200, 400], trace_ops=False, warmup=False)
    assert all(len(r.op_events) == 0 for r in report.runs)
    assert report.time_fit.chosen_model != "N/A"


def test_memory_fit_with_psutil(monkeypatch):
    class FakeMem:
        def __init__(self):
            self._rss = 100_000_000

        def memory_info(self):
            # bump so different per call
            self._rss += 1_000_000
            return type("MemInfo", (), {"rss": self._rss})

    class FakePsutil:
        def Process(self):
            return FakeMem()

    import costflow.utils as utils

    original = utils.psutil
    utils.psutil = FakePsutil()
    try:
        report = analyze(revenue_by_customer, make_orders_df, sizes=[200, 400, 800], trace_ops=False, warmup=False)
        assert report.mem_fit.chosen_model != "N/A"
        assert not report.mem_fit.notes
    finally:
        utils.psutil = original
