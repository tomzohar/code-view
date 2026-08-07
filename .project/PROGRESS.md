# Progress Log (append-only)

Newest entries at top. Format in MEMORY.md.

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
