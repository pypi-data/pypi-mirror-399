import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Callable, List

import pandas as pd

from . import analyze
from .report import pretty_print


def _load_callable(target: str, default_name: str) -> Callable[[Any], Any]:
    """
    Load a function from either MODULE:FUNC or a python file path.
    If only a path is given, defaults to `default_name`.
    """
    if ":" in target:
        path_part, func_name = target.split(":", 1)
    else:
        path_part, func_name = target, default_name

    path = Path(path_part)
    if not path.exists():
        raise FileNotFoundError(f"Cannot find module file: {path}")

    spec = importlib.util.spec_from_file_location("user_module", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)  # type: ignore[union-attr]
    finally:
        sys.path.pop(0)

    if not hasattr(module, func_name):
        raise AttributeError(f"{path} does not define '{func_name}'")

    return getattr(module, func_name)


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CostFlow: analyze pandas pipeline scaling.")
    parser.add_argument(
        "--pipeline",
        required=True,
        help="Path to python file (or file:func) exporting the pipeline function (default func name: pipeline)",
    )
    parser.add_argument(
        "--make-df",
        required=True,
        help="Path to python file (or file:func) exporting a make_df factory (default func name: make_df)",
    )
    parser.add_argument(
        "--sizes",
        nargs="+",
        type=int,
        required=True,
        help="List of dataset sizes to run (e.g., --sizes 1000 5000 10000)",
    )
    parser.add_argument(
        "--no-trace-ops",
        action="store_true",
        help="Disable per-operation tracing for lower overhead.",
    )
    parser.add_argument(
        "--no-warmup",
        action="store_true",
        help="Skip warmup run before measuring.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON instead of the pretty text report.",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> None:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    pipeline_fn = _load_callable(args.pipeline, default_name="pipeline")
    make_df_fn = _load_callable(args.make_df, default_name="make_df")

    report = analyze(
        pipeline_fn=pipeline_fn,
        make_df=make_df_fn,
        sizes=args.sizes,
        trace_ops=not args.no_trace_ops,
        warmup=not args.no_warmup,
    )

    if args.json:
        print(json.dumps(report.to_dict(), indent=2, default=str))
    else:
        pretty_print(report)


if __name__ == "__main__":
    main()
