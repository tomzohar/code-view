# .project/ — Project Memory

This directory is the persistent memory of code-view. Agent sessions are amnesiac; this is how context, decisions, and progress survive. **Reading the relevant parts of this directory at session start, and updating it at session end, is part of the definition of done** (see docs/SDLC.md §1, Stage 5).

## Index

| File | Purpose | Who writes |
|---|---|---|
| [BACKLOG.md](BACKLOG.md) | Prioritized work items (Now / Next / Later / Icebox) | Humans prioritize; anyone may append to Icebox with `[proposed]` |
| [PROGRESS.md](PROGRESS.md) | Append-only log: what shipped, what surprised us, retro notes | Every session that merges work appends an entry |
| [decisions/](decisions/) | ADRs — numbered, append-only. Template: [decisions/ADR-TEMPLATE.md](decisions/ADR-TEMPLATE.md) | New ADR per significant decision; never edit accepted ADRs (supersede instead) |
| specs/ | One spec per work item > ~half a day: `<id>-<slug>.md` | Author (human or agent), approved by maintainer before build |

## Rules

1. **Append, don't rewrite.** PROGRESS.md and accepted ADRs are history. Correct by adding, not editing.
2. **Backlog IDs are permanent.** `CV-042` never gets reused, even if the item dies.
3. **Every merged PR leaves a trace:** a PROGRESS entry, a backlog tick, and any follow-up items filed. A session that learned something non-obvious (a footgun, a constraint, a rejected approach) writes it down — in PROGRESS for events, in an ADR for decisions, in CLAUDE.md for conventions.
4. **Keep entries compact.** Three lines that get read beat thirty that don't.

## Formats

**PROGRESS entry:**
```
## 2026-08-07 · CV-003 · feat: hunk navigation (session: claude-code)
- Shipped: n/p navigation with stable hunk IDs; snapshot tests.
- Surprise: crossterm key repeat on Windows needed debouncing (see CV-019).
- Follow-ups filed: CV-019, CV-020.
```

**Backlog item:**
```
- [ ] CV-042 (ux, M3) Command palette fuzzy match is case-sensitive — should be smart-case. Spec: specs/042-palette-smartcase.md
```
