# code-view — Plan

Phased roadmap to v1.0. Each milestone is releasable, dogfoodable, and ends with a retro logged in [`.project/PROGRESS.md`](../.project/PROGRESS.md). Dates are targets, not promises; scope flexes before dates do.

## M0 — Foundation (weeks 1–2)
Skeleton that proves the architecture end to end.
- Cargo workspace with the six crates; CI (fmt/clippy/test/bench gates from SDLC L0–L3); `justfile`; `cargo-dist` release pipeline; fixture-repo corpus started.
- `cv` opens a repo: file tree + syntax-highlighted file view (tree-sitter, virtualized), `j/k`, `Tab`, `?`, `q`.
- TestBackend snapshot harness + first PTY e2e test running in CI.
- **Exit:** a maintainer reads code in cv daily; cold-start budget green in CI.

## M1 — The diff (weeks 3–5)
- `cv-vcs` via gitoxide: worktree/index/HEAD status and diffs; `cv diff <range>`; pager mode (`git diff | cv -`).
- DiffView unified + side-by-side, intra-line highlights, stable hunk IDs, `n/p` hunk navigation.
- Rename/mode-change/binary/huge-file handling against the fixture corpus.
- **Exit:** cv's own PRs are readable in cv (dogfood loop starts); rendering quality ≥ delta on the corpus (side-by-side visual comparison doc).

## M2 — Live + review (weeks 6–8) — *the identity milestone*
- `cv-watch`: live updates < 100 ms, cursor anchoring, fresh-edit gutter pulses.
- Review state: `a/c/r/A/R`, inline comments, persistence in `.cv/`, progress in status line.
- `f` → feedback file v1 (documented schema, golden tests) + copyable agent one-liner.
- **Exit:** full loop demo — Claude Code edits, human reviews live in cv, presses `f`, pastes one line, agent fixes rejected hunks. Record this as the launch demo GIF.

## M3 — Public alpha (weeks 9–10)
- Themes (dark/light/ansi + catppuccin/gruvbox), config file, remappable keys, command palette.
- Structural refinement pass (async difftastic-style upgrade), search `/`.
- Docs site, install paths (brew, cargo, curl script), CONTRIBUTING.md with agent-contributor guide, launch post ("the reading half of Claude Code") — HN/r/commandline/X.
- **Exit:** ≥ 200 installs week one; onboarding issues triaged into backlog.

## M4 — Agent-native depth (weeks 11–14)
- Claude Code hook adapter → turn markers, `t` navigation, "diff since turn N"; adapter recipes for Codex/OpenCode.
- `cv --sessions` multi-worktree awareness (US-08 spec first).
- Community keymap/theme contributions; first external-contributor milestone.
- **Exit:** turn-aware review demo; ≥ 3 external contributors merged.

## M5 — v1.0 (weeks 15–18)
- MCP server mode (`cv --mcp`) with `get_pending_review` / `mark_addressed`.
- Hardening: Windows Terminal parity, SSH/256-color audits, crash-report polish, perf pass on giant repos (Linux-kernel-scale fixture).
- Feedback-file format frozen as v1 (ADR); SemVer commitment begins.
- **Exit:** v1.0 tagged; roadmap-to-v2 drafted from backlog signal.

## Standing risks

| Risk | Mitigation |
|---|---|
| Agent vendor ships built-in reviewer | Vendor-neutral + reading mode value (see LANDSCAPE §4) |
| revdiff/diffai velocity | Win on live/turn-aware + rendering quality; ship M2 fast |
| Terminal compat rabbit holes | Fixture matrix early (M0), degrade gracefully policy |
| Scope creep toward git-client | VISION anti-goals are the checklist at every spec review |

## Operating cadence

Weekly: Friday pre-release + retro line in PROGRESS.md. Monthly: backlog grooming + UX papercut review + landscape refresh check. Per-PR: the SDLC validation ladder, no exceptions.
