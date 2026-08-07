#!/usr/bin/env python3
"""Validation ladder L3: assert the cold-start budget from ARCHITECTURE.md §4.

Reads `hyperfine --export-json` output and fails if the mean exceeds the budget.
Invoked via `just coldstart` — don't call it directly in CI (docs/SDLC.md §2).

The budget is 50 ms to first paint. `CV_COLDSTART_BUDGET_MS` overrides it so the
gate itself can be tested (`CV_COLDSTART_BUDGET_MS=0 just coldstart` must fail).
It exists for that, not as a pressure valve: raising the committed default is a
gate weakening and needs a human-approved ADR.

Caveat worth remembering when this number moves: §4 specifies the budget against
a 10k-file repo, and today we measure `cv --version` with no TUI. This is a
floor, not the real workload. Tightening it to the specified fixture is CV-031.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

DEFAULT_BUDGET_MS = 50.0

EXIT_OK = 0
EXIT_OVER_BUDGET = 1
EXIT_ERROR = 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("report", help="path to hyperfine --export-json output")
    parser.add_argument(
        "--budget-ms",
        type=float,
        default=float(os.environ.get("CV_COLDSTART_BUDGET_MS", DEFAULT_BUDGET_MS)),
    )
    args = parser.parse_args()

    try:
        with open(args.report, encoding="utf-8") as handle:
            results = json.load(handle)["results"]
    except (OSError, ValueError, KeyError) as exc:
        print(f"coldstart-gate: cannot read hyperfine report {args.report}: {exc}", file=sys.stderr)
        return EXIT_ERROR

    if not results:
        print(f"coldstart-gate: no benchmark results in {args.report}", file=sys.stderr)
        return EXIT_ERROR

    # hyperfine reports seconds; the budget is stated in milliseconds.
    measured = max(results, key=lambda item: item["mean"])
    mean_ms = measured["mean"] * 1000.0
    stddev_ms = measured.get("stddev", 0.0) * 1000.0

    print(
        f"coldstart-gate: {mean_ms:.1f} ms ± {stddev_ms:.1f} ms "
        f"(budget {args.budget_ms:.1f} ms) — {measured['command']}"
    )

    if mean_ms > args.budget_ms:
        over = mean_ms - args.budget_ms
        print(
            f"coldstart-gate: FAIL — {over:.1f} ms over the "
            f"{args.budget_ms:.1f} ms budget (docs/ARCHITECTURE.md §4).\n"
            "Raising the budget to pass this is a gate weakening and needs a "
            "human-approved ADR (docs/SDLC.md §1).",
            file=sys.stderr,
        )
        return EXIT_OVER_BUDGET

    headroom = args.budget_ms - mean_ms
    print(f"coldstart-gate: PASS ({headroom:.1f} ms of headroom)")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
