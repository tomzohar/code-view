# code-view — Design & UX

## 1. Design philosophy

**Calm surface, instant depth.** A reviewer's attention is the scarcest resource in agentic development. The default screen shows exactly three things — where you are (tree), what changed (diff), what to do (action bar) — and everything else is one keystroke away, then gone again.

Guiding rules:

1. **Zero to oriented in one second.** Launch `cv` and the most important change is already on screen, cursor on the first unreviewed hunk. No empty states that make you configure before you can look.
2. **The diff is the hero.** Maximum horizontal space to code; chrome is thin (1-char borders, single status line). Panels collapse; the diff never does.
3. **Motion communicates.** When a file changes live, it doesn't teleport — a subtle gutter pulse marks fresh edits, and the tree badges update. The user should *feel* the agent working without being distracted by it.
4. **Progressive disclosure of power.** Beginners use arrows and `?`. Experts get vim-grammar composability, a command palette (`:`/`Ctrl-p`), and full remapping. No feature may exist *only* in config.
5. **Honest rendering.** Truncation, binary files, huge files, mid-rebase states — always labeled, never silently wrong. Trust in a review tool is binary; one lie and it's gone.
6. **Accessible by default.** Full functionality in 16-color terminals and screen-reader-friendly modes; color is never the only carrier of meaning (added/removed also get `+/-` signs and distinct gutter glyphs). Respects reduced-motion preferences (`CV_NO_ANIMATE`).

## 2. Interaction model

### Modes (few, obvious)
- **Browse** — repo is clean or user chose `cv <path>`: file tree + syntax-highlighted code reading, jump-to-symbol.
- **Review** — dirty worktree or diff range: tree shows changed files with hunk counts; main pane is diff; verdict keys active.
- **Live** — review mode with the watcher hot (default in a repo an agent is editing): view updates in place, "turn markers" segment the diff timeline when an agent adapter is connected.

The mode is *inferred*, shown in the status line, and switchable — never a setup question.

### Keybinding philosophy
Vim-flavored where it's free (`j/k/g/G`, `/` search), plain-English mnemonics for review verbs, arrows always work:

| Key | Action |
|---|---|
| `j/k`, arrows | move line / hunk cursor |
| `n/p` | next / previous hunk |
| `Tab` | cycle panes (tree ⇄ diff) |
| `Enter` | open file / expand hunk context |
| `u` / `s` | unified ⇄ side-by-side diff |
| `a` / `r` | approve / reject hunk |
| `c` | comment on line/hunk (opens inline input) |
| `A` / `R` | approve / reject whole file |
| `f` | finish review → write feedback file, show summary |
| `t` | jump to last agent-turn marker |
| `z` | toggle tree collapse |
| `:` or `Ctrl-p` | command palette |
| `?` | help overlay (searchable) |
| `q` | quit (never loses verdicts — session state persists in `.cv/`) |

Every action in the palette shows its keybinding — the palette *is* the tutorial.

### The review grammar
The core loop is deliberately console-game simple: **`n` → look → `a`/`c`/`r` → repeat → `f`.** A competent reviewer should sustain 10+ hunks/minute on routine changes. The status line shows review progress (`7/12 hunks · 2 ✗ · 1 💬`) so finishing feels like clearing a level.

## 3. Visual language

- **Layout:** two-pane default (tree 24 cols, diff rest); tree auto-hides under 100 cols; everything usable at 80×24.
- **Color:** semantic roles, not decoration — additions green, deletions red, modifications in intra-line amber highlights, unreviewed hunks bright / reviewed dimmed, agent-fresh edits with a cyan gutter tick. Built-in themes: `cv-dark`, `cv-light`, `ansi` (16-color), plus popular ports (catppuccin, gruvbox).
- **Typography within constraints:** careful use of dim/bold/italic, box-drawing, and spacing; no nerd-font requirement (glyphs degrade to ASCII automatically).

## 4. User stories (v1 scope, with acceptance criteria)

**US-01 — Instant orientation.** As an agent supervisor, when I run `cv` in a repo Claude Code just edited, I see the changed-files tree and the first unreviewed hunk within 100 ms, so I never wonder what the agent did.
*Accept:* cold start < 50 ms to first paint on 10k-file fixture; cursor lands on first unreviewed hunk; changed files badged with hunk counts.

**US-02 — Live updates.** As a supervisor watching an agent work, edits appear in my open diff within 100 ms without any keypress, and my cursor/scroll position is preserved, so I can read while the agent writes.
*Accept:* PTY test — external file write updates view < 100 ms; cursor stays on the same (content-anchored) hunk; fresh-edit gutter pulse appears and fades.

**US-03 — Hunk-by-hunk review.** As a reviewer, I can walk hunks with `n/p` and verdict each with `a/c/r`, so reviewing a 15-file agent change takes minutes, not a context switch to an IDE.
*Accept:* verdicts persist across restart; progress indicator correct; snapshot tests for all verdict visual states.

**US-04 — Structured feedback to the agent.** As a supervisor, when I press `f`, cv writes a feedback file (approvals, rejections, per-line comments with file:line anchors) and prints/copies the one-liner to paste into my agent (e.g. `@.cv/review-2026-08-07T10-14.md address the rejected hunks`), so my review becomes the agent's next prompt with zero transcription.
*Accept:* file format matches documented schema (golden test); rejected hunks include surrounding context lines; a Claude Code session given the file can locate every referenced hunk (manual E2E per release).

**US-05 — Diff any range.** As a developer, `cv diff main..feature` (or `git diff | cv -`) gives me the same review UX for branches, PRs checked out locally, or piped diffs, so cv replaces my pager, not just my agent viewer.
*Accept:* works as `core.pager`; handles renames, mode changes, submodule bumps without crashing (fixture corpus).

**US-06 — Turn-aware history.** As a multi-turn session driver, I can press `t` to jump between agent-turn markers and view "diff since turn N", so I can review incrementally instead of re-reading the whole worktree diff after every prompt.
*Accept:* with the Claude Code hook adapter installed, Stop events create markers; range view "since marker" matches `git diff` of the snapshot refs; works with ≥ 20 turns.

**US-07 — Reading, not just diffing.** As a terminal-native developer, in a clean repo `cv` is a fast, beautiful code reader — tree, syntax highlighting, `/` search, `gd`-style jump to definition within the file — so the tool earns a place in my muscle memory outside review sessions.
*Accept:* opens and scrolls a 100k-line file at 60 fps; search hits highlighted; works over SSH in 256-color mode.

**US-08 — Multi-session awareness (stretch, v1.x).** As a parallel-agent operator with three worktrees, `cv --sessions` shows which session changed which files and lets me enter each review, so I catch spec drift before merge time.
*Accept:* deferred to M4 spec.

## 5. Anti-goals in UX

No mouse-first flows (mouse works, but nothing requires it). No modal dialog stacks. No onboarding wizard. No telemetry prompts (no telemetry at all — see VISION). No feature that requires a nerd font, a specific terminal emulator, or a config file to be usable.

## 6. Design debt policy

UX papercuts are tracked in the backlog with a `ux` tag and reviewed monthly; any papercut hit twice by a maintainer during dogfooding is auto-promoted to the next milestone. The dogfood loop (SDLC §2) is the primary input to this list.
