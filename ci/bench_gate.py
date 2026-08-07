#!/usr/bin/env python3
"""Validation ladder L3: fail the build on a criterion performance regression.

Invoked via `just bench-gate` — don't call it directly in CI, or the command an
agent runs locally stops matching the command CI runs (docs/SDLC.md §2).

Why this isn't a naive point-estimate comparison
------------------------------------------------
docs/SDLC.md §1 sets the bar at "regressions > 5% fail". Comparing criterion's
point estimates at a flat 5% would fire constantly on GitHub's shared runners,
where that much run-to-run variance is ordinary noise. A gate that is red for
no reason trains everyone to ignore red, and flaky gates are P1 bugs here.

So a benchmark fails only when even the most optimistic reading of the new
measurement is >5% slower than the most pessimistic reading of the baseline:

    new.mean.ci.lower_bound > base.mean.ci.upper_bound * (1 + threshold)

That is *stronger* evidence than comparing point estimates, not a laxer
threshold: a real 5% regression that criterion measured with any confidence
still fails. The 5% figure itself is unchanged, and changing it needs an ADR.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import tempfile

DEFAULT_THRESHOLD = 0.05
DEFAULT_CRITERION_DIR = "target/criterion"

EXIT_OK = 0
EXIT_REGRESSION = 1
EXIT_ERROR = 2


class BenchError(Exception):
    """A malformed or unreadable criterion tree — a bug, not a slow benchmark."""


def load_baseline(criterion_dir: str | pathlib.Path, name: str) -> dict[str, dict]:
    """Collect every `<bench id>/<name>/estimates.json` under the criterion dir.

    Returns a map of bench id -> criterion's `mean` estimate. An absent
    directory yields {} so the caller can distinguish "no baseline" from
    "baseline with no benchmarks".
    """
    root = pathlib.Path(criterion_dir)
    if not root.is_dir():
        return {}

    estimates: dict[str, dict] = {}
    for path in sorted(root.rglob("estimates.json")):
        if path.parent.name != name:
            continue
        bench_id = path.parent.parent.relative_to(root).as_posix()
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            estimates[bench_id] = payload["mean"]
        except (OSError, ValueError, KeyError) as exc:
            raise BenchError(f"unreadable criterion estimates at {path}: {exc}") from exc
    return estimates


def _ns(value: float) -> str:
    """Format nanoseconds at whatever scale keeps the number readable."""
    for unit, scale in (("s", 1e9), ("ms", 1e6), ("µs", 1e3)):
        if value >= scale:
            return f"{value / scale:.3f} {unit}"
    return f"{value:.1f} ns"


def compare(
    base: dict[str, dict],
    candidate: dict[str, dict],
    threshold: float = DEFAULT_THRESHOLD,
) -> tuple[list[str], list[str]]:
    """Return (regressions, report lines) comparing candidate against base."""
    regressions: list[str] = []
    lines: list[str] = []

    for bench_id in sorted(candidate):
        new = candidate[bench_id]
        old = base.get(bench_id)
        if old is None:
            lines.append(f"  NEW       {bench_id}  {_ns(new['point_estimate'])}")
            continue

        old_point = old["point_estimate"]
        new_point = new["point_estimate"]
        delta = (new_point - old_point) / old_point if old_point else 0.0

        # Conservative: optimistic new vs pessimistic old.
        ceiling = old["confidence_interval"]["upper_bound"] * (1.0 + threshold)
        regressed = new["confidence_interval"]["lower_bound"] > ceiling

        label = "REGRESSED" if regressed else ("faster" if delta < -threshold else "ok")
        lines.append(
            f"  {label:<9} {bench_id}  "
            f"{_ns(old_point)} -> {_ns(new_point)}  ({delta:+.1%})"
        )
        if regressed:
            regressions.append(f"{bench_id}: {delta:+.1%} ({_ns(old_point)} -> {_ns(new_point)})")

    for bench_id in sorted(set(base) - set(candidate)):
        lines.append(f"  GONE      {bench_id}  (in baseline, not in this run)")

    return regressions, lines


def run(criterion_dir: str, baseline: str, candidate: str, threshold: float) -> int:
    try:
        base = load_baseline(criterion_dir, baseline)
        new = load_baseline(criterion_dir, candidate)
    except BenchError as exc:
        print(f"bench-gate: {exc}", file=sys.stderr)
        return EXIT_ERROR

    if not new:
        print(
            f"bench-gate: no '{candidate}' benchmark results under {criterion_dir}/ — "
            "did `cargo bench` run?",
            file=sys.stderr,
        )
        return EXIT_ERROR

    if not base:
        # Bootstrap case: nothing to compare against yet. Loud, but not fatal —
        # failing here would block the very push to main that seeds the baseline.
        print(f"bench-gate: NO BASELINE named '{baseline}' under {criterion_dir}/.")
        print("bench-gate: nothing to compare against; this run gates nothing.")
        print("bench-gate: a baseline is saved on the next push to main.")
        return EXIT_OK

    regressions, lines = compare(base, new, threshold)

    print(f"bench-gate: '{candidate}' vs '{baseline}' (threshold {threshold:.0%})")
    for line in lines:
        print(line)

    if regressions:
        print(f"\nbench-gate: FAIL — {len(regressions)} benchmark(s) regressed:", file=sys.stderr)
        for item in regressions:
            print(f"  - {item}", file=sys.stderr)
        print(
            "\nRaising the threshold to pass this is a gate weakening and needs a "
            "human-approved ADR (docs/SDLC.md §1).",
            file=sys.stderr,
        )
        return EXIT_REGRESSION

    print("\nbench-gate: PASS")
    return EXIT_OK


# --- self-test ---------------------------------------------------------------
# Acceptance criterion 5: prove the gate actually gates. A perf gate that never
# fires is indistinguishable from no perf gate, and nothing else in the ladder
# would notice.


def _write_estimate(root: pathlib.Path, bench_id: str, name: str, point: float, spread: float) -> None:
    directory = root / bench_id / name
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "estimates.json").write_text(
        json.dumps(
            {
                "mean": {
                    "point_estimate": point,
                    "standard_error": point * spread / 2,
                    "confidence_interval": {
                        "confidence_level": 0.95,
                        "lower_bound": point * (1 - spread),
                        "upper_bound": point * (1 + spread),
                    },
                }
            }
        ),
        encoding="utf-8",
    )


def selftest() -> int:
    cases = [
        # (label, base ns, candidate ns, ci spread, expected exit)
        ("20% regression fails", 1000.0, 1200.0, 0.01, EXIT_REGRESSION),
        ("20% improvement passes", 1000.0, 800.0, 0.01, EXIT_OK),
        ("1% noise passes", 1000.0, 1010.0, 0.01, EXIT_OK),
        # A big point-estimate jump that criterion measured with wide confidence
        # intervals is runner noise, not a regression. This is the case a naive
        # point-estimate gate gets wrong.
        ("noisy 8% with wide CIs passes", 1000.0, 1080.0, 0.20, EXIT_OK),
    ]

    failures = 0
    for label, base_ns, cand_ns, spread, expected in cases:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            _write_estimate(root, "cv_core/reducer", "main", base_ns, spread)
            _write_estimate(root, "cv_core/reducer", "pr", cand_ns, spread)
            actual = run(str(root), "main", "pr", DEFAULT_THRESHOLD)
        ok = actual == expected
        failures += not ok
        print(f"selftest: {'ok  ' if ok else 'FAIL'} {label} (exit {actual}, want {expected})")

    # Missing baseline must be a loud no-op, not a failure.
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        _write_estimate(root, "cv_core/reducer", "pr", 1000.0, 0.01)
        actual = run(str(root), "main", "pr", DEFAULT_THRESHOLD)
    ok = actual == EXIT_OK
    failures += not ok
    print(f"selftest: {'ok  ' if ok else 'FAIL'} missing baseline is a no-op (exit {actual})")

    # An empty candidate is an error, not a pass — a bench that failed to run
    # must not read as "no regressions".
    with tempfile.TemporaryDirectory() as tmp:
        actual = run(tmp, "main", "pr", DEFAULT_THRESHOLD)
    ok = actual == EXIT_ERROR
    failures += not ok
    print(f"selftest: {'ok  ' if ok else 'FAIL'} empty candidate is an error (exit {actual})")

    print(f"\nselftest: {'PASS' if not failures else f'FAIL ({failures} case(s))'}")
    return EXIT_OK if not failures else EXIT_REGRESSION


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--criterion-dir", default=DEFAULT_CRITERION_DIR)
    parser.add_argument("--baseline", default="main", help="saved baseline to compare against")
    parser.add_argument("--candidate", default="pr", help="baseline name of this run")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument("--selftest", action="store_true", help="prove the gate gates (AC-5)")
    args = parser.parse_args()

    if args.selftest:
        return selftest()
    return run(args.criterion_dir, args.baseline, args.candidate, args.threshold)


if __name__ == "__main__":
    sys.exit(main())
