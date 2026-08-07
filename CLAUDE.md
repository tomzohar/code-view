# CLAUDE.md — agent guide for code-view

You are working on **code-view (`cv`)**: an open-source Rust + Ratatui terminal code/diff viewer built for reviewing AI-agent changes. Read this file fully; follow the links only when relevant to your task.

## Start every session

1. Read your task's spec in `.project/specs/` (or the backlog item in `.project/BACKLOG.md`).
2. Skim `.project/MEMORY.md`, recent `.project/PROGRESS.md` entries, and any ADR your task touches.
3. Work in a git worktree (`git worktree add ../cv-<task-id>`), one task per session.

## Commands (always via just — never ad-hoc variants)

- `just check` — fmt + clippy (-D warnings) + tests for touched crates. Run after every meaningful edit.
- `just test` / `just snapshot <name>` — full tests / render a UI state via TestBackend to inspect your own UI as text.
- `just e2e` — PTY end-to-end scenarios. `just bench` — criterion perf gates. `just coldstart` — hyperfine budget check.
- `just review` — accept/reject pending insta snapshots. `just run -- <args>` — run the `cv` binary.
- `just --list` shows everything. Toolchain is pinned in `rust-toolchain.toml`; deps are versioned once in the root `[workspace.dependencies]` and referenced as `{ workspace = true }`.

## Architecture map (details: docs/ARCHITECTURE.md)

Workspace crates under `crates/`, strict downward deps: `cv-app` (CLI) → `cv-ui` (ratatui widgets) → `cv-core` (PURE Elm-style reducer — no I/O here, ever) → `cv-vcs` (gitoxide) / `cv-watch` (notify) / `cv-syntax` (tree-sitter) / `cv-bridge` (agent feedback files, hooks, MCP).

## Hard rules

- **Never weaken a validation gate** (no `#[ignore]`, threshold bumps, deleted assertions) — that requires a human-approved ADR.
- New dependency, public-interface change, or feedback-file format change → ADR first (`.project/decisions/ADR-TEMPLATE.md`).
- Test-first against the spec's acceptance criteria; UI work starts with a TestBackend snapshot test.
- Conventional commits (`feat:`/`fix:`/`perf:`/…), body references the backlog ID (e.g. `CV-014`).
- If your change wants to exceed the spec's file scope by ~20%, STOP and ask / file a spec amendment.
- Performance budgets (ARCHITECTURE.md §4) are release blockers — check `just bench` before opening a PR.

## Definition of done (a PR without this is not done)

Tests green through the ladder (docs/SDLC.md §1 L0–L3) → append a `.project/PROGRESS.md` entry → tick/move the backlog item → file follow-up items you discovered → update this file if you learned a missing convention.

## Product invariants (from docs/VISION.md)

cv never edits source code; it is read-only over the repo and write-only over review feedback (`.cv/`). No telemetry. No network calls in the core. Zero-config must always work: `cv` in any git repo does the right thing.
