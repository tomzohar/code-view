# code-view — Architecture

**Stack decision:** Rust + [Ratatui](https://ratatui.rs) (see [ADR-0001](../.project/decisions/ADR-0001-tech-stack.md)). Single static binary `cv`, no runtime dependencies, cross-platform (macOS, Linux, Windows Terminal; first-class over SSH).

## 1. System overview

code-view is a local TUI application with four responsibilities: **observe** the repository (filesystem + git), **model** its state (files, diffs, review status), **render** it fast, and **exchange** structured review feedback with agents. That maps to a strict layered architecture:

```
┌────────────────────────────────────────────────────────────┐
│  cv-app          binary: CLI args, config, session wiring  │
├────────────────────────────────────────────────────────────┤
│  cv-ui           Ratatui widgets, layout, keymap, themes   │
├────────────────────────────────────────────────────────────┤
│  cv-core         domain model: RepoState, DiffModel,       │
│                  ReviewState, event reducer (pure)         │
├──────────────┬──────────────┬──────────────┬───────────────┤
│  cv-vcs      │  cv-watch    │  cv-syntax   │  cv-bridge    │
│  git via     │  fs events   │  tree-sitter │  agent I/O:   │
│  gitoxide/   │  (notify),   │  highlight + │  feedback     │
│  libgit2     │  debounce    │  structure   │  files, hooks,│
│              │              │              │  MCP server   │
└──────────────┴──────────────┴──────────────┴───────────────┘
```

Dependency rule: arrows point down only. `cv-core` is pure (no I/O, no terminal) — this is what makes the whole app testable and lets agents develop against it without a TTY.

## 2. Crate breakdown

### cv-core (the heart)
- **State model:** `AppState { repo: RepoState, view: ViewState, review: ReviewState }`. Elm-style: a single `update(state, Event) -> (state, Vec<Effect>)` reducer. All business logic is a pure function of events — trivially unit-testable, replayable, fuzzable.
- **Events:** `FileChanged(path)`, `GitStateChanged`, `Key(KeyEvent)`, `HunkVerdict(hunk_id, Verdict)`, `AgentSessionEvent(...)`, `Tick`.
- **DiffModel:** hunks with stable IDs (content-hash based, so a verdict survives an upstream refresh when the hunk didn't change), intra-line highlights, optional structural refinement from `cv-syntax`.

### cv-vcs
- Primary backend **gitoxide** (pure Rust, fast, no C toolchain pain); `git` CLI shell-out as a fallback for exotic cases. Trait `Vcs` so jujutsu can arrive later.
- Produces: status, diffs (worktree↔index↔HEAD↔arbitrary refs), blame-on-demand, file content at any revision.

### cv-watch
- `notify` crate → debounced (default 30 ms) coalesced batches → `FileChanged`/`GitStateChanged` events. Watches `.git/HEAD` and refs, respects `.gitignore`, degrades to polling on network filesystems.

### cv-syntax
- **tree-sitter** for highlighting and structure (functions/blocks) — the same foundation as difftastic and helix, battle-tested, ~30 grammars bundled, lazy-loaded.
- Two-tier diffing: line diff (Myers/histogram via `imara-diff`) renders *instantly*; structural refinement (moved-code detection, syntax-aware intra-line spans) computes async and upgrades the view when ready. Never block first paint on the fancy pass.

### cv-ui
- Ratatui + crossterm. Widget set: `FileTree`, `CodeView`, `DiffView` (unified + side-by-side), `HunkBar`, `CommandPalette`, `StatusLine`, `HelpOverlay`.
- Virtualized rendering: only visible lines are highlighted/laid out; a 100k-line file scrolls at full frame rate.
- Theming: built-in themes + load from user config; honors terminal background detection; degrades correctly to 256-color and 16-color terminals.

### cv-bridge (the agentic moat)
Three integration surfaces, all optional, all additive:

1. **Feedback files (works with everything, v1):** review verdicts and comments serialize to a stable, documented format at `.cv/review-<timestamp>.md` (human-readable markdown with a machine-parseable header). The user tells any agent `@.cv/review-*.md fix these`. Zero coupling, works with Claude Code, Codex, OpenCode, Aider, or a human colleague.
2. **Hook adapters (v1.x):** ship recipes/adapters for Claude Code hooks (e.g. `PostToolUse` → notify cv; `Stop` → cv marks "turn boundary" in the diff timeline) and equivalents for other agents. cv listens on a unix socket `$XDG_RUNTIME_DIR/cv/<repo-hash>.sock` for these nudges.
3. **MCP server mode (v2):** `cv --mcp` exposes tools like `get_pending_review`, `get_hunk_context`, `mark_addressed` so agents can *pull* review state instead of being handed a file. This makes cv a first-class peer in agent toolchains.

Turn-boundary awareness enables cv's signature view: **"diff since last agent turn"**, not just "diff vs HEAD".

### cv-app
- CLI (`clap`): `cv` (auto: dirty worktree → review mode, clean → browse mode), `cv <path>`, `cv diff <ref>..<ref>`, `cv --watch-session <adapter>`, `cv --mcp`. Also functions as a pager: `git diff | cv -`.
- Config: `~/.config/cv/config.toml` + per-repo `.cv/config.toml`. Everything has a default; the config file is optional.

## 3. Runtime model

Tokio-based, three loops sharing the event channel:

```
input task (crossterm events)──┐
watcher task (fs/git events) ──┼──▶ mpsc ──▶ update() ──▶ render (≤16ms budget)
bridge task (socket/hooks)   ──┘                │
                                    effects ──▶ async workers (diff compute,
                                                highlight, git ops) ──▶ events
```

Expensive work (structural diff, highlighting a huge file, blame) runs in worker tasks and lands as events; the render loop never blocks. Rendering diffs against a mid-write file is handled by generation counters — a stale worker result is discarded, not painted.

## 4. Performance budgets (enforced in CI — see SDLC.md)

| Operation | Budget |
|---|---|
| Cold start to first paint (10k-file repo) | < 50 ms |
| FS event → updated diff on screen | < 100 ms |
| Keystroke → visual response | < 16 ms |
| Scroll 10k-line diff | 60 fps, zero dropped frames |
| Memory, typical session | < 150 MB |

## 5. Error handling & resilience

- The viewer must never crash the terminal: panic hook restores the TTY, writes a crash report to `.cv/crash/`, and prints a one-line apology with the report path.
- Git weirdness (rebase in progress, detached HEAD, corrupt index, submodules) renders a degraded-but-honest view rather than erroring out. Agents put repos in strange states constantly; robustness here is a core feature, not polish.
- Binary/huge files: size-capped rendering with an explicit "show anyway" action; images get a placeholder (kitty/sixel image protocol support is a later nicety).

## 6. Testing architecture (summary — full detail in SDLC.md)

- `cv-core`: pure unit tests + property tests (proptest) on the reducer; snapshot tests (`insta`) on DiffModel output for a corpus of real-world diffs.
- `cv-ui`: Ratatui's `TestBackend` renders to an in-memory buffer → snapshot tests of actual screen content. This is the key enabler for agentic development: **agents can "see" the UI as text** without a terminal.
- End-to-end: PTY harness (`expectrl`) drives the real binary in a virtual terminal against fixture repos; scripted scenarios assert on screen states.
- Performance: `criterion` benches + a `hyperfine` cold-start check with budget thresholds as CI gates.

## 7. Decision log

All significant choices are recorded as ADRs in [`.project/decisions/`](../.project/decisions/). Standing decisions as of this document: Rust + Ratatui (ADR-0001); gitoxide-first VCS access; tree-sitter for syntax; Elm-architecture core; feedback-file bridge before MCP; MIT license.
