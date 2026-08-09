# Progress Log (append-only)

Newest entries at top. Format in MEMORY.md.

## 2026-08-09 · CV-002 · integrate: CI pipeline merged to main (session: claude-code)
- Supersedes the entry below, which was written while the work was still an unmerged draft. `cv/002-ci-pipeline` rebased onto main, every rung run locally and green — `lock-check`, `check` (fmt/clippy/6 tests), `lint-workflows` (actionlint clean), `e2e` (2 PTY tests), `perf-gate-selftest`, `coldstart` (1.9 ms ± 0.3 against the 50 ms budget), and the real `bench-baseline` → `bench-gate` round trip. Worktree and branch deleted.
- Fixed a permanent-ID collision: the draft and a concurrent main-branch commit both claimed CV-029. Main's (repo layout vs. skill defaults) keeps the number; the draft's L4 adversarial review became CV-033. Renumbering touched the draft's own PROGRESS line — the one edit to history this session, made before it merged, because a duplicate permanent ID is worse than a corrected draft.
- Installed `actionlint` (missing when the draft was written), so the workflow lint the draft could only reason about is now actually proven clean.
- Still not verified: the repo has no git remote, so `.github/workflows/ci.yml` has never executed. The ladder is real locally and aspirational in CI. Filed CV-034 to close that.
- Judgement calls inherited from the draft and still open for a maintainer: the spec was never approved before the build (SDLC Stage 1), and the criterion gate reads "regressions > 5% fail" as a confidence-interval comparison rather than a point estimate (see the entry below).
- Follow-ups filed: CV-034 (push to a remote, watch CI go green once).

## 2026-08-07 · CV-002 · feat: CI pipeline — draft on `cv/002-ci-pipeline`, not merged (session: claude-code)
- Shipped (unmerged): spec `specs/002-ci-pipeline.md`; `.github/workflows/ci.yml` (4 jobs — L0/L1 on 3 platforms, L2 on unix, L3 + workflow lint on ubuntu); `ci/bench_gate.py` + `ci/coldstart_gate.py`; justfile gains `lock-check`, `bench-baseline`, `bench-gate`, `perf-gate-selftest`, `lint-workflows`.
- Surprise (real bug, not a CI detail): `cargo bench --workspace` runs libtest's harness for every lib/bin/test target alongside the criterion benches, and libtest rejects `--save-baseline` — the regression gate failed the first time it ran for real. `--benches` doesn't exclude them; `bench = false` per target does. This was invisible until now because `just bench` passes no arguments, so those harnesses ran zero benchmarks and exited 0 — the recipe looked green while benchmarking nothing.
- Judgement call worth revisiting: a flat 5% criterion comparison would flake constantly on shared runners, so the gate compares the new measurement's CI lower bound against the baseline's CI upper bound × 1.05. Stronger evidence than a point-estimate check, not a laxer threshold — but it is an interpretation of "regressions > 5% fail", and a maintainer should agree with it.
- Not verified: actionlint isn't installed here, and the repo has no remote, so the workflow has never executed. Reviewed YAML, not proven-green CI.
- Follow-ups filed: CV-030 (Windows PTY), CV-031 (cold start vs the real fixture), CV-032 (SHA-pin actions), CV-033 (L4 adversarial review).

## 2026-08-07 · CV-001 · feat: cargo workspace scaffold + dev environment (session: claude-code)
- Shipped: git repo (`main`); 7-crate workspace under `crates/`; pinned toolchain (1.97.1, edition 2024); workspace-wide dep versions + lints (`unsafe_code = forbid`, `unwrap/expect_used = warn`); justfile covering the whole ladder (check/test/snapshot/e2e/bench/coldstart/review); MIT LICENSE; `AGENTS.md` → `CLAUDE.md` symlink; `.project/specs/` opened.
- Every rung proven green, not just wired: 6 unit tests, 2 PTY e2e tests (expectrl), criterion bench, hyperfine cold start (1.6 ms against a 50 ms budget — no TUI yet, so treat as a floor).
- Surprise: Homebrew's `rustup` formula is keg-only and no longer ships `rustup-init`, so `/opt/homebrew/opt/rustup/bin` and `~/.cargo/bin` had to be added to PATH by hand. Worth repeating in a future CONTRIBUTING.md.
- Not done here: CI (CV-002) — the gates exist locally but nothing enforces them on push.
- Follow-ups filed: CV-027 (cargo deny), CV-028 (bundle tree-sitter grammars).

## 2026-08-07 · docs: Rust-for-TS-devs onboarding dictionary (session: cowork/claude)
- Shipped: docs/RUST_FOR_TS_DEVS.md — language/toolchain dictionary, library analogies, house patterns, footguns, learning path. Linked from README.
- Rationale: lower the contributor barrier from the TS ecosystem (largest likely contributor pool for an agent-tooling project).

## 2026-08-07 · project inception (session: cowork/claude)
- Shipped: project bible v1 — VISION, ARCHITECTURE, SDLC, DESIGN, LANDSCAPE, PLAN; .project/ memory system; CLAUDE.md; ADR-0001 (Rust + Ratatui).
- Decisions: standalone TUI for v1; feedback-file bridge before hooks before MCP; docs/ + .project/ structure.
- Follow-ups filed: CV-001 … CV-026 (initial backlog).
