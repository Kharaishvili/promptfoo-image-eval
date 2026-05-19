#!/usr/bin/env python3
"""Summarize Promptfoo JSON results into CSV and console insights.

The script uses pandas when it is installed, but falls back to the Python
standard library so CI artifacts can still be inspected without extra setup.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_INPUTS = [
    ".promptfoo/results-stable.json",
    ".promptfoo/results-failures.json",
    ".promptfoo/results-model-regression.json",
    ".promptfoo/results.json",
]


def nested_get(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def load_result_rows(path: Path) -> list[dict[str, Any]]:
    with path.open() as f:
        payload = json.load(f)

    result_root = payload.get("results", payload)
    rows = result_root.get("results", [])
    if not isinstance(rows, list):
        return []

    timestamp = result_root.get("timestamp", "")
    eval_id = payload.get("evalId", "")
    flattened = []

    for row in rows:
        grading = row.get("gradingResult") or {}
        provider = row.get("provider") or {}
        response = row.get("response") or {}
        test_case = row.get("testCase") or {}
        vars_ = row.get("vars") or test_case.get("vars") or {}
        component_results = grading.get("componentResults") or []
        failed_components = [
            component
            for component in component_results
            if component.get("pass") is False
        ]
        failing_assertions = [
            nested_get(component, "assertion", "type", default="javascript")
            for component in failed_components
        ]
        failure_reasons = [
            str(component.get("reason", ""))
            for component in failed_components
            if component.get("reason")
        ]

        flattened.append(
            {
                "source_file": str(path),
                "eval_id": eval_id,
                "timestamp": timestamp,
                "provider_label": provider.get("label", ""),
                "provider_id": provider.get("id", ""),
                "test_description": test_case.get("description", ""),
                "image": vars_.get("image", ""),
                "keywords": vars_.get("keywords", ""),
                "min_keywords": vars_.get("minKeywords", ""),
                "pass": bool(grading.get("pass", row.get("success", False))),
                "score": grading.get("score", row.get("score", "")),
                "reason": grading.get("reason", ""),
                "failure_reason": row.get("failureReason", ""),
                "failing_assertions": "; ".join(failing_assertions),
                "component_failure_reasons": " | ".join(failure_reasons),
                "latency_ms": row.get("latencyMs", ""),
                "cost": row.get("cost", ""),
                "output": response.get("output", ""),
            }
        )

    return flattened


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return

    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def print_standard_summary(rows: list[dict[str, Any]]) -> None:
    total = len(rows)
    passed = sum(1 for row in rows if row["pass"])
    failed = total - passed
    print(f"Total rows: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Pass rate: {(passed / total * 100) if total else 0:.1f}%")

    by_provider: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_test: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_provider[row["provider_label"] or row["provider_id"]].append(row)
        by_test[row["test_description"]].append(row)

    print("\nPass rate by provider:")
    for provider, provider_rows in sorted(by_provider.items()):
        provider_total = len(provider_rows)
        provider_passed = sum(1 for row in provider_rows if row["pass"])
        print(f"- {provider}: {provider_passed}/{provider_total}")

    print("\nFailures by test:")
    for test, test_rows in sorted(by_test.items()):
        test_failed = [row for row in test_rows if not row["pass"]]
        if test_failed:
            print(f"- {test}: {len(test_failed)} failure(s)")

    assertion_counts = Counter()
    for row in rows:
        if row["failing_assertions"]:
            for assertion in row["failing_assertions"].split("; "):
                assertion_counts[assertion] += 1

    if assertion_counts:
        print("\nFailure types:")
        for assertion, count in assertion_counts.most_common():
            print(f"- {assertion}: {count}")


def print_pandas_summary(rows: list[dict[str, Any]]) -> bool:
    try:
        import pandas as pd  # type: ignore
    except ModuleNotFoundError:
        return False

    df = pd.DataFrame(rows)
    if df.empty:
        print("No rows found.")
        return True

    print("Pass rate by provider:")
    print(df.groupby("provider_label")["pass"].agg(["count", "sum", "mean"]))

    failures = df[df["pass"] == False]  # noqa: E712
    if not failures.empty:
        print("\nFailures by test/provider:")
        print(
            failures.groupby(["test_description", "provider_label"])
            .size()
            .reset_index(name="failures")
            .to_string(index=False)
        )

    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze Promptfoo JSON results and produce CSV summaries."
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        help="Promptfoo JSON result files. Defaults to known .promptfoo outputs.",
    )
    parser.add_argument(
        "--out",
        default="reports/eval-analysis",
        help="Output directory for CSV reports.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_paths = [Path(path) for path in (args.inputs or DEFAULT_INPUTS)]
    existing_paths = [path for path in input_paths if path.exists()]

    if not existing_paths:
        print("No Promptfoo result files found.")
        print("Run npm run eval, npm run eval:failures, or npm run eval:models first.")
        return 1

    rows: list[dict[str, Any]] = []
    for path in existing_paths:
        rows.extend(load_result_rows(path))

    out_dir = Path(args.out)
    write_csv(out_dir / "rows.csv", rows)
    write_csv(out_dir / "failures.csv", [row for row in rows if not row["pass"]])

    print(f"Read {len(existing_paths)} result file(s).")
    print(f"Wrote {out_dir / 'rows.csv'}")
    print(f"Wrote {out_dir / 'failures.csv'}")
    print("")

    if not print_pandas_summary(rows):
        print_standard_summary(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
