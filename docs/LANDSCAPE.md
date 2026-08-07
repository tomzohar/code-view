# code-view — Competitive Landscape

*Research date: 2026-08-07. Sources listed at the bottom; refresh quarterly (backlog item).*

## 1. The field today

Developers reviewing code in the terminal today assemble a personal stack from four tool families. None was designed for the agentic loop; a new fifth family is emerging that is — and it validates our thesis while leaving the center of the board open.

### A. Diff pagers & pretty-printers
- **delta** — the de facto standard `git diff` pager: syntax highlighting, side-by-side, intra-line emphasis. Read-only, no navigation, no interactivity. The rendering quality bar we must meet or beat.
- **difftastic** — structural (tree-sitter) diffs that ignore formatting noise. Brilliant idea, but slow on large files and non-interactive. We adopt the *idea* as our async "refinement pass" so it never costs first-paint latency.
- **diffnav / git-split-diffs / riff / diff-so-fancy** — pager variants adding file trees or nicer highlighting. Confirm demand for tree + diff in the terminal; all remain passive pipes.
- **bat** — `cat` with syntax highlighting; the standard for *reading* single files, but no tree, no diff context, no navigation.

### B. Git TUIs
- **lazygit** (~60k+ stars) — the most successful git TUI; proves developers happily live in a full-screen terminal app for repo work. But it's *commit-and-branch* centric: diff viewing is a side panel, reviews aren't a concept, and it delegates rendering to delta.
- **gitui, tig** — same family: fast (Rust/C), keyboard-driven, staging-oriented. Diff reading is functional, not state-of-the-art.
- **magit / neovim plugins (diffview.nvim, gitsigns)** — superb review ergonomics *if* you live in Emacs/Neovim. Locked to an editor; agents fight editors over buffer state. Their hunk-granular workflows are the ergonomic bar for our review grammar.

### C. Agent CLIs' built-in views
Claude Code, Codex CLI, OpenCode, Gemini CLI each render diffs inline in the transcript. This is where our users are *today* — and it's the weakest reading experience of all: diffs scroll away, no tree, no navigation, no persistent review state, limited context lines. The agent vendors are focused on the writing loop, not the reading loop. **This is the gap.**

### D. Session managers / orchestrators
- **Claude Squad, Agent Deck** — tmux/worktree multiplexers for parallel agent sessions (terminal).
- **Nimbalyst, Opcode, Conductor, Crystal** — GUI dashboards: kanban of sessions, checkpoints, file-change sidebars.
These tools manage *sessions*; their change-review surfaces are thin. Industry commentary (Nimbalyst's own comparison) names the open problem: *traceability from session to code changes* — "which files did each session change, did it drift from the spec." They are complements and future integration partners, not competitors.

### E. The emerging direct competitors (agent-native diff review)
- **revdiff** — TUI diff review with inline annotations that flow back to Claude Code/Codex/OpenCode; multi-VCS; themes; MIT. Closest in spirit to us.
- **diffai** — Rust TUI, tree + diff, `c` to comment, writes a markdown feedback file for `@`-mentioning in Claude Code. Validates our exact feedback-file mechanism.
- **hunk, critique, drft, livediff** — smaller entrants: review-first diff TUIs, live file watching. A Cambrian explosion in the last ~18 months — the market is telling us this category is real.
- **diffity, Nimbalyst viewer** (web/GUI) — GitHub-style local diff pages for agent changes; serve the audience that abandons the terminal to read. Every user they win is a terminal UX failure we intend to fix.

## 2. What we adapt (proven patterns we adopt shamelessly)

1. **delta's rendering bar** — intra-line highlights, side-by-side, syntax theming. Table stakes.
2. **difftastic's structural insight** — as an async refinement layer (never on the critical path).
3. **lazygit's interaction DNA** — full-screen TUI, panel model, `?` help, single-key verbs, zero-config launch. Its popularity is the proof that our form factor works.
4. **magit/diffview's hunk-granular review grammar** — the best review ergonomics ever built; we port the grammar out of the editor.
5. **diffai/revdiff's feedback-file bridge** — markdown with file:line anchors that agents ingest via `@`-mention. We standardize and document the format rather than inventing a private one.
6. **The Rust TUI toolchain** — ratatui + tree-sitter + gitoxide + notify: the stack proven by gitui, yazi, helix, atuin.

## 3. What we disrupt

1. **The passive pager.** Post-agent, a diff is not output to scroll past — it's a *work queue with state* (reviewed/approved/rejected/commented, persisted). No pager family tool has state; we make statefulness the default.
2. **Review as a point-in-time act.** Everyone diffs a frozen snapshot. Agents make the worktree a *stream*. Live-updating, turn-segmented review ("what changed since the agent's last turn") is our signature capability; nobody in families A–C has it, and the E-family entrants treat watching as a feature, not the architecture.
3. **The IDE round-trip.** The alt-tab to VS Code "just to read" is the tax we eliminate. State-of-the-art reading (virtualized rendering, structural awareness, symbol navigation) has simply never been attempted seriously in a terminal viewer — bat stopped at files, delta at pipes.
4. **One-way review.** Human judgment currently returns to the agent as retyped prose. We make the review artifact itself machine-consumable (feedback files → hooks → MCP), turning review from commentary into *control*.
5. **The transcript as UI.** Agent CLIs conflate conversation with code. We unbundle: transcript stays in the agent pane, code lives in cv. As agent vendors improve their inline diffs they validate the need — but a vendor-neutral, best-of-breed surface across *all* agents is structurally hard for any one vendor to build.

## 4. Positioning

> **lazygit is where you drive git. cv is where you read code.** delta renders diffs; cv reviews them. Session managers tell you *which* agent worked; cv shows you *what it did* — live — and carries your verdict back.

Risks we track: an agent vendor ships a great built-in reviewer (mitigation: vendor-neutrality + reading-mode value beyond agents); revdiff/diffai reach critical mass first (mitigation: out-execute on live/turn-aware review and raw rendering quality — neither is live-first today); category consolidates into GUIs (mitigation: the terminal is where agents run; proximity wins).

## 5. Sources

- [Terminal Trove — diff category](https://terminaltrove.com/categories/diff/)
- [Introducing diffai (Josh Finnie)](https://www.joshfinnie.com/blog/introducing-diffai/)
- [revdiff](https://revdiff.com/)
- [diffity (GitHub)](https://github.com/nilbuild/diffity)
- [Nimbalyst — Best session managers for Claude Code & Codex](https://nimbalyst.com/blog/best-session-managers-for-claude-code-and-codex/)
- [Nimbalyst — AI diff review](https://nimbalyst.com/blog/ai-diff-review-visual-agent-changes/)
- [Nimbalyst — Best Claude Code GUI 2026](https://nimbalyst.com/blog/best-claude-code-gui-tools-2026/)
- [Agent Deck review (vibecodinghub)](https://vibecodinghub.org/tools/agent-deck)
- [awesome-cli-coding-agents (GitHub)](https://github.com/bradagi/awesome-cli-coding-agents)
- [Difftastic — pawelgrzybek](https://pawelgrzybek.com/difftastic-my-new-favourite-diff-viewer/)
- [Better diffs in Lazygit with delta](https://www.lorenzobettini.it/2025/06/better-diffs-in-lazygit-with-delta/)
- [Warp — reviewing AI-generated code](https://docs.warp.dev/guides/agent-workflows/how-to-review-ai-generated-code/)
