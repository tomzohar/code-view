# Specs

One file per work item bigger than ~half a day: `<id>-<slug>.md` (e.g. `004-file-tree.md`).

Contents, per [docs/SDLC.md](../../docs/SDLC.md) §1 Stage 1:

- **Problem** — what's broken or missing, for whom.
- **Non-goals** — what this explicitly does not do.
- **Acceptance criteria** — numbered, testable by a command an agent can run.
  *"Given fixture repo `fixtures/rename-heavy`, pressing `n` three times lands on hunk 4 (snapshot test)"* — not *"navigation feels smooth."*
- **UX notes** — keybindings, screen states.
- **Performance constraints** — which budget from [ARCHITECTURE §4](../../docs/ARCHITECTURE.md) applies.

The maintainer approves a spec before any build session starts. Ambiguity found
mid-build goes back into the spec, not into improvisation.
