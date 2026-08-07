# ci/

Gate scripts invoked by the justfile. Nothing here is called directly by
`.github/workflows/ci.yml` — CI runs `just` recipes only, so that any CI failure
reproduces locally with one command (docs/SDLC.md §2).

| Script | Recipe | Gate |
|---|---|---|
| `bench_gate.py` | `just bench-gate` | criterion regression > 5% (docs/SDLC.md §1) |
| `coldstart_gate.py` | `just coldstart` | cold start < 50 ms (docs/ARCHITECTURE.md §4) |

Both are plain Python 3 with no third-party imports — Python ships on all three
GitHub runner images and on macOS/Linux dev machines, so there is nothing to
install. See `.project/specs/002-ci-pipeline.md` for the alternatives considered
(`jq`, `critcmp`, a Rust `xtask`) and why they lost.

## Testing the gates

`just perf-gate-selftest` proves both gates can still fail: `bench_gate.py
--selftest` runs synthetic criterion trees through the comparison, and the
cold-start gate is run against an impossible 0 ms budget and expected to reject
it. CI runs this before it trusts either gate to pass.

## The rule that matters

An agent may not weaken a gate to make it pass — no raised thresholds, no
`#[ignore]`, no deleted assertions. That requires a human-approved ADR
(docs/SDLC.md §1 Stage 4). `CV_COLDSTART_BUDGET_MS` exists so the gate can be
tested, not so it can be relaxed.
