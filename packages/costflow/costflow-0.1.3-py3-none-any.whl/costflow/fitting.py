from __future__ import annotations

import math
from typing import List, Tuple, Dict

import numpy as np

from .models import PipelineRun, FitResult


def design_matrix(runs: List[PipelineRun], basis: List[str]) -> Tuple[np.ndarray, List[str]]:
    """
    basis terms supported:
      - "1"      intercept
      - "n"      rows
      - "nlogn"  n * log(n)
      - "n2"     n^2
      - "nm"     rows * cols
    """
    cols = []
    names = []

    for b in basis:
        if b == "1":
            cols.append(np.ones(len(runs)))
            names.append("1")
        elif b == "n":
            cols.append(np.array([r.n_rows for r in runs], dtype=float))
            names.append("n")
        elif b == "nlogn":
            cols.append(np.array([r.n_rows * math.log(max(r.n_rows, 2)) for r in runs], dtype=float))
            names.append("nlogn")
        elif b == "n2":
            cols.append(np.array([r.n_rows ** 2 for r in runs], dtype=float))
            names.append("n2")
        elif b == "nm":
            cols.append(np.array([r.n_rows * r.n_cols for r in runs], dtype=float))
            names.append("nm")
        else:
            raise ValueError(f"Unknown basis term: {b}")

    X = np.vstack(cols).T
    return X, names


def fit_linear(X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, float, float]:
    """Least squares fit; returns beta, r2, rmse."""
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ beta
    resid = y - yhat

    ss_res = float(np.sum(resid ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))

    r2 = 1.0 - (ss_res / ss_tot if ss_tot > 0 else 0.0)
    rmse = float(np.sqrt(ss_res / max(len(y), 1)))
    return beta, r2, rmse


def fit_scaling_models(
    runs: List[PipelineRun],
    target: str,
    candidates: List[Tuple[str, List[str]]],
) -> FitResult:
    """
    candidates: list of (model_name, basis_terms)
      e.g. ("a*n", ["1","n"])
    """
    if target == "time":
        y = np.array([r.wall_time_s for r in runs], dtype=float)
        filtered_runs = runs
    elif target == "memory":
        filtered_runs = [r for r in runs if r.peak_rss_mb is not None]
        if len(filtered_runs) < 2:
            return FitResult(
                target=target,
                chosen_model="N/A",
                coefficients={},
                r2=float("nan"),
                rmse=float("nan"),
                notes="Not enough memory measurements (install psutil?)",
            )
        y = np.array([r.peak_rss_mb for r in filtered_runs], dtype=float)
    else:
        raise ValueError("target must be 'time' or 'memory'")

    best = None
    for model_name, basis in candidates:
        X, names = design_matrix(filtered_runs, basis)
        beta, r2, rmse = fit_linear(X, y)
        # Simple selection: minimize RMSE
        score = rmse
        entry = (score, model_name, names, beta, r2, rmse)
        if best is None or score < best[0]:
            best = entry

    assert best is not None
    _, model_name, names, beta, r2, rmse = best
    coeffs: Dict[str, float] = {names[i]: float(beta[i]) for i in range(len(names))}
    return FitResult(target=target, chosen_model=model_name, coefficients=coeffs, r2=float(r2), rmse=float(rmse))


def predict_from_fit(coeffs: Dict[str, float], n: int, m: int) -> float:
    """Predict y at (n,m) using basis terms present in coeffs."""
    vals = {
        "1": 1.0,
        "n": float(n),
        "nlogn": float(n * math.log(max(n, 2))),
        "n2": float(n ** 2),
        "nm": float(n * m),
    }
    y = 0.0
    for k, c in coeffs.items():
        y += c * vals.get(k, 0.0)
    return float(y)
