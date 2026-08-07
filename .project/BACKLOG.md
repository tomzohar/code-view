# Backlog

Format: `- [ ] CV-<id> (<tags>, <milestone>) <summary>`. IDs are permanent. Priority = position within section. See MEMORY.md for rules.

## Now (M0 — Foundation)

- [x] CV-001 (infra, M0) Scaffold cargo workspace: cv-app, cv-ui, cv-core, cv-vcs, cv-watch, cv-syntax, cv-bridge. justfile with check/test/snapshot/bench targets.
- [ ] CV-002 (infra, M0) CI pipeline: fmt, clippy -D warnings, test, criterion regression gate, hyperfine cold-start gate (budgets from docs/ARCHITECTURE.md §4).
- [ ] CV-003 (core, M0) Elm-style reducer skeleton in cv-core with event/effect types + first property tests.
- [ ] CV-004 (ui, M0) File tree widget + virtualized code view with tree-sitter highlighting; j/k/Tab/?/q.
- [ ] CV-005 (test, M0) TestBackend snapshot harness + first PTY e2e test (expectrl) in CI.
- [ ] CV-006 (infra, M0) Fixture repo corpus v1: small, 10k-file, rename-heavy, unicode, binary-containing, mid-rebase.
- [ ] CV-007 (infra, M0) cargo-dist release pipeline; Friday pre-release automation.

## Next (M1 — The diff)

- [ ] CV-008 (vcs, M1) gitoxide integration: status + worktree/index/HEAD diffs behind Vcs trait.
- [ ] CV-009 (core, M1) DiffModel: hunk parsing, stable content-hash hunk IDs, intra-line highlights (imara-diff).
- [ ] CV-010 (ui, M1) DiffView unified + side-by-side; n/p hunk navigation; u/s toggle.
- [ ] CV-011 (app, M1) `cv diff <range>` + pager mode (`git diff | cv -`, core.pager support).
- [ ] CV-012 (core, M1) Edge-case handling: renames, mode changes, binary, huge files, submodule bumps.
- [ ] CV-013 (docs, M1) Rendering quality comparison doc vs delta on fixture corpus.

## Later (M2+)

- [ ] CV-014 (watch, M2) Live watcher: notify + debounce, cursor anchoring, fresh-edit gutter pulse.
- [ ] CV-015 (review, M2) Review state machine: a/c/r/A/R verdicts, inline comments, persistence in .cv/.
- [ ] CV-016 (bridge, M2) Feedback file v1: schema doc + golden tests + `f` flow with copyable agent one-liner.
- [ ] CV-017 (ux, M3) Themes, config.toml, remappable keys, command palette.
- [ ] CV-018 (syntax, M3) Async structural refinement pass (difftastic-style) with generation counters.
- [ ] CV-021 (bridge, M4) Claude Code hook adapter → turn markers; `t` navigation; diff-since-turn.
- [ ] CV-022 (app, M4) `cv --sessions` multi-worktree awareness (write US-08 spec first).
- [ ] CV-023 (bridge, M5) MCP server mode: get_pending_review / get_hunk_context / mark_addressed.

## Icebox

- [ ] CV-027 [proposed] (infra) Add `cargo deny` (licence + advisory audit) to the ladder — an MIT project shipping static binaries should assert its dependency licences.
- [ ] CV-028 [proposed] (infra) Bundle tree-sitter grammars with lazy loading; `cv_syntax::grammar_count()` returns 0 until then.
- [ ] CV-024 [proposed] (ux) Kitty/sixel image rendering for image diffs.
- [ ] CV-025 [proposed] (vcs) Jujutsu backend behind Vcs trait.
- [ ] CV-026 [proposed] (docs) Quarterly landscape refresh — next due 2026-11-07.
