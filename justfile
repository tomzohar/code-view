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

# ── the outer loop ────────────────────────────────────────────────────────────

# L2: PTY end-to-end scenarios against fixture repos.
e2e:
    cargo test -p cv-app --test '*' -- --include-ignored

# L3: criterion performance gates (docs/ARCHITECTURE.md §4).
bench:
    cargo bench --workspace

# Cold-start budget: < 50 ms to first paint (requires: brew install hyperfine).
coldstart: build-release
    hyperfine --shell=none --warmup 3 --runs 20 './target/release/cv --version'

build-release:
    cargo build --release

# Everything CI runs, in CI's order. Slow on purpose.
ci: check e2e bench

# ── housekeeping ──────────────────────────────────────────────────────────────

run *ARGS:
    cargo run -p cv-app -- {{ ARGS }}

clean:
    cargo clean
