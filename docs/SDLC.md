# code-view — SDLC for Agentic Development

code-view is built *by* agents as much as *for* people who use them. We dogfood the workflow we're selling. This document is the contract for how work happens — for humans and for every Claude Code / Codex / OpenCode session that touches this repo.

## 0. Core beliefs

1. **Specs are the source code of agentic development.** An agent with a precise spec and a tight validation loop produces professional work; an agent with a vibe produces slop. We spend our human time on specs and reviews, not keystrokes.
2. **Validation loops beat supervision.** We don't watch agents type; we build automated gates that catch defects, and we review outcomes. Every quality property we care about must be checkable by a command an agent can run.
3. **Memory is infrastructure.** Agent sessions are amnesiac. The `.project/` memory system (backlog, decisions, progress) plus `CLAUDE.md` is how context survives across sessions. Updating it is part of "done", not an afterthought.
4. **Small, verified increments.** One task → one branch/worktree → one PR → merged same day when possible. Long-lived agent branches rot fast because agents can't remember why they diverged.

## 1. The development loop

Every unit of work follows the same five-stage loop, whether executed by a human, one agent, or parallel agents:

```
SPEC ──▶ PLAN ──▶ BUILD ──▶ VALIDATE ──▶ INTEGRATE
  ▲                              │
  └────────── feedback ──────────┘
```

### Stage 1 — SPEC (human-led)
- Work items live in [`.project/BACKLOG.md`](../.project/BACKLOG.md). Anything bigger than ~half a day gets a spec file: `.project/specs/<id>-<slug>.md` containing: problem, non-goals, acceptance criteria (testable, numbered), UX notes (keybindings, screen states), and performance constraints.
- Acceptance criteria are written so an agent can self-check: *"Given fixture repo `fixtures/rename-heavy`, pressing `n` 3 times lands on hunk 4 (snapshot test)"* — not *"navigation feels smooth."*
- The VP RND (or maintainer) approves the spec before any build session starts. Ambiguity discovered mid-build goes back into the spec, not into improvisation.

### Stage 2 — PLAN (agent, reviewed by human)
- The agent session starts by reading `CLAUDE.md`, the spec, `.project/MEMORY.md` and relevant ADRs, then produces a short plan: files to touch, new tests to write, risks. Plan mode / dry-run first for anything touching `cv-core` public types or the bridge format.
- Plans that add dependencies, change public interfaces, or alter the feedback-file format **require an ADR** (template in `.project/decisions/`) before code.

### Stage 3 — BUILD (agent-led)
- One task per session, in a **git worktree** (`git worktree add ../cv-<task-id>`), so parallel sessions never collide.
- Test-first is mandatory where the spec gives acceptance criteria: encode the criteria as failing tests, then make them pass. For UI work, write the `TestBackend` snapshot test first — it doubles as the "screenshot" a human reviews.
- Agents commit early and often with conventional commits (`feat:`, `fix:`, `perf:`, `refactor:`, `test:`, `docs:`). Each commit message's body notes *which acceptance criterion* it advances.

### Stage 4 — VALIDATE (automated + human)
The validation ladder — every rung must pass before the next:

| Rung | Gate | Runs |
|---|---|---|
| L0 | `cargo fmt --check`, `cargo clippy -- -D warnings` | pre-commit + CI |
| L1 | `cargo test` (unit + property + snapshot) | pre-commit + CI |
| L2 | PTY end-to-end scenarios against fixture repos | CI |
| L3 | Performance budgets (criterion regressions > 5% fail; cold-start hyperfine check) | CI |
| L4 | **Agent adversarial review** — a *fresh* agent session, with no memory of the implementation, reviews the diff against the spec and tries to find criterion violations, edge cases, and lies in comments. Its findings are posted on the PR. | CI (scheduled) or manual |
| L5 | **Human review — using cv itself** once it can render its own diffs (M2+). Time-to-judgment on our own PRs is our primary dogfood metric. | required |

Rules: an agent may not weaken a gate to pass it (no `#[ignore]`, no threshold bumps, no deleted assertions) — such changes require an explicit human-approved ADR. Flaky tests are P1 bugs: a flaky gate trains everyone (humans and agents) to ignore red.

### Stage 5 — INTEGRATE
- Squash-merge to `main`; `main` is always releasable. Delete the worktree.
- **Close the loop in memory (definition of done):** update `.project/PROGRESS.md` (what shipped, what surprised us), tick/move the backlog item, file follow-ups discovered during the work, and update `CLAUDE.md` if the session revealed a missing convention. A PR that doesn't update memory is not done.

## 2. Validation loops in depth

### The self-check loop (inner, seconds)
Agents run `just check` (fmt + clippy + test for the touched crates) after every meaningful edit. The `justfile` is the single entry point so every agent uses identical commands — no drift between "what CI runs" and "what the agent ran."

### The visual loop (inner, seconds)
`just snapshot <test>` renders any screen state to text via `TestBackend`. Agents inspect their own UI output and iterate before a human ever looks. `insta` diffs make visual regressions reviewable in a PR as plain text.

### The adversarial loop (outer, per-PR)
Fresh-context agent review (L4) exists because the building agent is systematically blind to its own assumptions. The reviewer session gets: the spec, the diff, the fixture corpus — and an explicit instruction to try to *break* the change, not summarize it.

### The dogfood loop (outer, continuous)
From M2 onward, all maintainers review all PRs *in cv*. Friction felt here is filed into the backlog within the same session. This is our fastest source of real UX signal.

### The release loop (outer, weekly)
- `main` → tagged pre-release every Friday via `cargo-dist` (binaries for macOS/Linux/Windows).
- A release-candidate checklist agent session runs: fresh install on each platform image, smoke script (open repo, navigate, review a diff, emit feedback file), CHANGELOG generation from conventional commits, then a human approves the tag.
- Versioning: SemVer. The feedback-file format and CLI flags are the public API — breaking either bumps major (post-1.0) and requires an ADR + migration note.

## 3. Repo conventions for agents

- **`CLAUDE.md`** (repo root) is the entry point: build commands, architecture map, conventions, links into `.project/`. Kept under ~150 lines; details live in docs it links to. It is loaded by Claude Code automatically and by convention (`AGENTS.md` symlink) by other tools.
- **Never** edit generated files, snapshot files (except via `cargo insta review`), or `.project/decisions/` history (append-only).
- Unsure-about-scope rule: if a change wants to touch more than the spec's listed files ±20%, stop and ask (or file a spec amendment) rather than expanding silently.
- Secrets: none in this repo, ever. cv itself is offline; CI needs no credentials beyond publishing tokens held by maintainers.

## 4. Issue → release traceability

`BACKLOG.md` item → spec file → branch `cv/<id>-slug` → conventional commits referencing `<id>` → PR → CHANGELOG entry. Anyone (human or agent) can walk from a released feature back to the reasoning that produced it. This traceability is exactly what today's agent tooling lacks — we impose it on ourselves first.

## 5. Community contributions

External PRs get the same ladder; L4 adversarial review runs automatically, which lets maintainers spend human review only on PRs that already survived the machine gauntlet. Good-first-issues are backlog items with completed specs — the highest-leverage gift we can give a new contributor (or their agent).
