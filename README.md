# code-view (`cv`)

> A state-of-the-art code and diff viewer for your terminal — built for the age of AI coding agents.

Agents write code faster than you can read it. **code-view** fixes the reading part: a live, keyboard-driven TUI that shows your repo's files and diffs as they change, and turns your review into structured feedback your agent can act on.

```
┌ files ──────────┬ diff: src/render/gutter.rs ─────────────────────────┐
│ ▾ src           │  @@ -41,6 +41,14 @@ impl Gutter {                   │
│   ▾ render      │  41   fn width(&self) -> u16 {                      │
│     gutter.rs ● │  42 -     self.digits + 1                           │
│     view.rs   ● │  42 +     self.digits + self.sign_width + 1         │
│   watcher.rs    │  43 +     // sign column reserved for diff markers  │
│ ▸ tests         │  ...                                                │
│                 │                                                     │
│ 2 files changed │  [a]pprove  [c]omment  [r]eject  [n]ext hunk  [?]   │
└─────────────────┴─────────────────────────────────────────────────────┘
```

**Status: pre-alpha — design phase.** The project bible lives in [`docs/`](docs/):

- [Vision](docs/VISION.md) — why this exists and what it optimizes for
- [Architecture](docs/ARCHITECTURE.md) — Rust + Ratatui, crate layout, rendering pipeline
- [Design & UX](docs/DESIGN.md) — interaction model, keybindings, user stories
- [SDLC](docs/SDLC.md) — how we build this with agents, and the validation loops that keep quality high
- [Landscape](docs/LANDSCAPE.md) — the competitive field: what we adapt, what we disrupt
- [Plan](docs/PLAN.md) — phased roadmap to v1
- [Rust for TS devs](docs/RUST_FOR_TS_DEVS.md) — onboarding dictionary: language mapping, our libraries, house patterns

Project working memory (backlog, decisions, progress log) lives in [`.project/`](.project/MEMORY.md). Agent contributors: read [`CLAUDE.md`](CLAUDE.md) first.

## License

MIT
