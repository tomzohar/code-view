# code-view task runner.
#
# This file is the single entry point for every validation command, so agents and
# CI run byte-identical checks (docs/SDLC.md §2). If CI runs something that isn't
# a recipe here, that's the bug.

default:
    @just --list

# ── the inner loop ────────────────────────────────────────────────────────────

# L0 + L1: fmt, clippy (-D warnings) and tests. Run after every meaningful edit.
check: fmt-check lint test

# Cargo.lock is committed; CI must fail rather than silently resolve new versions.
lock-check:
    cargo fetch --locked

# Format the workspace.
fmt:
    cargo fmt --all

fmt-check:
    cargo fmt --all --check

lint:
    cargo clippy --workspace --all-targets -- -D warnings

# L1: unit + property + snapshot tests.
test *ARGS:
    cargo test --workspace {{ ARGS }}

# Render a UI state to text via TestBackend and print it — the visual loop.
# Usage: just snapshot test_backend_round_trips
snapshot NAME:
    cargo test -p cv-ui {{ NAME }} -- --nocapture --exact --show-output

# Review pending insta snapshots interactively (requires: cargo install cargo-insta).
review:
    cargo insta review

# Lint the GitHub Actions workflows (requires: brew install actionlint).
lint-workflows:
    actionlint

# ── the outer loop ────────────────────────────────────────────────────────────

# L2: PTY end-to-end scenarios against fixture repos.
e2e:
    cargo test -p cv-app --test '*' -- --include-ignored

# L3: criterion performance gates (docs/ARCHITECTURE.md §4).
bench:
    cargo bench --workspace --benches

# CI runs this on main; run it locally before optimising to get a "before".
# Save the current numbers as the comparison baseline.
bench-baseline NAME="main":
    cargo bench --workspace --benches -- --save-baseline {{ NAME }}

# The 5% threshold and the significance test live in ci/bench_gate.py.
# L3 gate: bench this revision and fail on a regression against the baseline.
bench-gate BASELINE="main":
    cargo bench --workspace --benches -- --save-baseline pr
    python3 ci/bench_gate.py --baseline {{ BASELINE }} --candidate pr

# Cold-start budget: < 50 ms to first paint (requires: brew install hyperfine).
coldstart: build-release
    hyperfine --shell=none --warmup 3 --runs 20 \
        --export-json target/coldstart.json './target/release/cv --version'
    python3 ci/coldstart_gate.py target/coldstart.json

# A perf gate that can no longer fail is indistinguishable from no perf gate,
# and nothing else in the ladder would notice — so prove both can still fail.
perf-gate-selftest: bench-gate-selftest coldstart-gate-selftest

# Prove the criterion gate still rejects a regression.
bench-gate-selftest:
    python3 ci/bench_gate.py --selftest

# Prove the cold-start gate still rejects an over-budget start.
coldstart-gate-selftest: build-release
    #!/usr/bin/env bash
    set -uo pipefail
    if CV_COLDSTART_BUDGET_MS=0 just coldstart >/dev/null 2>&1; then
        echo "selftest: FAIL cold-start gate passed an impossible 0 ms budget" >&2
        exit 1
    fi
    echo "selftest: ok   cold-start gate fails when over budget"

build-release:
    cargo build --release

# `bench-gate` is absent by design: it needs a baseline saved from main, which
# CI restores from its cache. Locally, `just bench-baseline` then `just
# bench-gate` gives the same comparison against your own "before".
#
# Everything CI runs, in CI's order. Slow on purpose.
ci: lock-check check lint-workflows e2e perf-gate-selftest coldstart bench

# ── housekeeping ──────────────────────────────────────────────────────────────

run *ARGS:
    cargo run -p cv-app -- {{ ARGS }}

clean:
    cargo clean
