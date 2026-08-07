# CV-002 — CI pipeline

Status: **draft, awaiting maintainer approval**
Backlog: `CV-002 (infra, M0)`
Depends on: CV-001 (done)

## Problem

The validation ladder (docs/SDLC.md §1 Stage 4) exists as `just` recipes and every
rung is green locally — but nothing enforces it. Any push, from a human or an
agent, can land red code on `main`. That inverts the core belief the project is
built on: *"validation loops beat supervision."* Right now the loop is
supervision, and the supervisor is whoever remembers to type `just check`.

This is more acute for this repo than most, because most commits here will be
written by agents in fresh, amnesiac sessions. An agent that never sees a red
build has no feedback signal at all.

## Non-goals

Explicitly out of scope; each has a follow-up where relevant.

1. **L4 adversarial agent review.** Deserves its own spec (prompt design, how
   findings get posted, cost control). Filed as CV-033.
2. **L5 human review in cv.** Blocked on M2 — cv cannot render its own diffs yet.
3. **Release / publishing.** `cargo-dist`, Friday pre-releases, CHANGELOG
   generation are CV-007.
4. **`cargo deny`.** Already tracked as CV-027; slots into the `check` job when
   approved.
5. **Windows PTY e2e (L2).** See "Platform scope" below. Filed as CV-030.
6. **The real cold-start budget.** ARCHITECTURE §4 specifies < 50 ms *on a
   10k-file repo*. That fixture does not exist until CV-006. v1 of this gate
   measures `cv --version` against the same 50 ms ceiling, which is a floor, not
   the budget. Tightening it to the specified workload is CV-031.
7. **Branch protection.** Required-check configuration is a GitHub repo setting,
   not a file in this repo. It is a maintainer action, listed under "Handoff".

## Design

### Command parity is the load-bearing constraint

docs/SDLC.md §2: *"the justfile is the single entry point so every agent uses
identical commands — no drift between what CI runs and what the agent ran."*

Therefore **every CI step that gates anything invokes a `just` recipe.** The
workflow file contains no `cargo` invocations. Where a gate needed logic that
didn't exist yet (a cold-start threshold, a criterion comparison), the logic went
into the justfile and `ci/`, not into YAML. A reviewer should be able to
reproduce any CI failure by running one `just` command locally.

### Jobs

| Job | Rung | Platforms | Gate |
|---|---|---|---|
| `check` | L0 + L1 | ubuntu, macos, windows | `just lock-check` + `just check` |
| `e2e` | L2 | ubuntu, macos | `just e2e` |
| `perf` | L3 | ubuntu | `just bench-gate` + `just coldstart` |
| `workflows` | — | ubuntu | `just lint-workflows` (actionlint) |

### Platform scope

L0/L1 run on all three target platforms from day one — cheap, and cross-platform
breakage is much cheaper to catch at introduction than at release.

L2 (PTY) runs on unix only. `expectrl`'s Windows ConPTY support is the least
mature part of that crate, and a flaky gate is a P1 bug per SDLC §1 — a gate
everyone learns to re-run teaches everyone to ignore red. Windows PTY coverage is
CV-030, to be added when it can be added *reliably*, not sooner.

L3 runs on ubuntu only: one platform, one baseline, one set of numbers to reason
about.

`lock-check` (`cargo fetch --locked`) was not in the original backlog line but
belongs here: `Cargo.lock` is committed, and without this gate CI would silently
resolve different dependency versions than the ones a contributor tested
against — which quietly defeats the point of committing the lockfile.

### A bug this work surfaced

`cargo bench --workspace` runs libtest's harness against every lib, bin and
integration-test target in addition to the criterion benches. libtest rejects
criterion's `--save-baseline`, so the regression gate failed outright the first
time it ran for real. `--benches` does not exclude those targets; `bench = false`
on each non-criterion target does.

This never surfaced before because the existing `just bench` passes no arguments,
so the stray libtest harnesses ran zero benchmarks and exited 0. The recipe
looked green while benchmarking nothing but criterion by luck. Every crate
manifest therefore gains a `bench = false` stanza.

### The criterion regression gate, and why it is not a naive 5% check

The backlog says "criterion regression gate", SDLC §1 says "regressions > 5%
fail". The naive implementation — compare point estimates, fail at +5% — will
flake constantly on GitHub's shared runners, where 5-10% run-to-run variance from
noisy neighbours is normal. That gate would be red often enough to be ignored,
which is worse than no gate.

`ci/bench_gate.py` therefore uses a **conservative significance test**: a
benchmark fails only when

```
new.mean.confidence_interval.lower_bound  >  base.mean.confidence_interval.upper_bound × 1.05
```

i.e. even the most optimistic reading of the new measurement is more than 5%
slower than the most pessimistic reading of the baseline. This is strictly
*stronger* evidence than a point-estimate comparison, not a weaker threshold —
it cannot pass a real 5% regression that criterion measured with confidence, and
it does not fire on runner noise. The 5% figure from SDLC §1 is unchanged.

Baselines flow through the GitHub Actions cache: a push to `main` saves
`criterion-main-<os>-<sha>`; a PR restores the newest `criterion-main-<os>-*` and
compares against it.

**Known soft spot:** on a repo with no baseline yet (today), the gate has nothing
to compare against and exits 0. It prints `NO BASELINE` loudly and the job
summary says so, but it is a gate that can no-op. It self-heals on the first push
to `main` after this lands. Alternatives (committing baselines, failing closed)
are worse: committed numbers go stale silently, and failing closed blocks the
very push that would create the baseline.

### The cold-start gate

`hyperfine --export-json` → `ci/coldstart_gate.py` asserts mean < budget.
Budget defaults to 50 ms (ARCHITECTURE §4) and is overridable via
`CV_COLDSTART_BUDGET_MS` — which exists so the gate itself can be tested
(AC-4), not so anyone can raise it. Raising the committed default is a
gate weakening and needs an ADR.

Current measured value is ~1.6 ms with no TUI. Expect this number to move a lot
when CV-004 lands; the headroom is real but unearned.

### Why Python for the two gate scripts

Both gates need to read JSON, do arithmetic, and exit non-zero. Options
considered:

- **`jq` + shell** — jq is on GitHub runners but not on every dev machine, which
  breaks reproduce-locally.
- **`critcmp`** — the natural tool, but it renders a comparison table and always
  exits 0; the fail decision would still need parsing on top.
- **A Rust `xtask` crate** — best long-term fit for a Rust repo, but adds a crate
  and compile time to every CI run for ~80 lines of arithmetic.
- **Python 3** — present on all three GitHub runner images and on macOS/Linux dev
  machines out of the box; zero install; readable by any reviewer.

Python was chosen for v1. **This is the one decision in this spec I'd most like
a second opinion on** — if the preference is zero non-Rust tooling in the repo,
the `xtask` route is the alternative and the scripts port more or less
line-for-line. Note the perf job is ubuntu-only, so Windows Python is not a
concern.

### Supply chain

Third-party actions are referenced by version tag (`@v2`, `@v4`), not by commit
SHA. Tag references are mutable and are a real supply-chain risk. I did not pin
SHAs here because I will not write hashes I have not verified against the
upstream repos. Pinning is filed as CV-032 and should be done before the repo
accepts external contributions.

Workflow permissions are `contents: read` at the top level. No secrets are used
or needed (SDLC §3).

## Acceptance criteria

Each is checkable by a command.

1. **Parity.** Every *gate* step in `.github/workflows/ci.yml` invokes a `just`
   recipe. Check: `grep -nE 'run:' .github/workflows/ci.yml` shows only `just …`
   lines plus `rustup show`, which is toolchain setup, not a gate.
2. **The full ladder runs locally in CI's order.** `just ci` passes on a clean
   checkout and covers L0, L1, L2, workflow linting, and benches.
3. **The workflow file is valid.** `just lint-workflows` exits 0 (actionlint).
4. **The cold-start gate actually gates.**
   `CV_COLDSTART_BUDGET_MS=0 just coldstart` exits non-zero;
   `just coldstart` (50 ms default) exits 0. Wrapped as
   `just coldstart-gate-selftest`.
5. **The bench gate actually gates.** `just bench-gate-selftest` exits 0 — it
   asserts, against synthetic criterion output, that a 20% regression fails, a
   20% improvement passes, a noise-level 1% delta passes, an 8% delta measured
   with wide confidence intervals passes (the case a naive point-estimate gate
   gets wrong), a missing baseline exits 0 with a `NO BASELINE` notice, and an
   empty candidate is an error rather than a silent pass.
   `just perf-gate-selftest` runs AC-4 and AC-5 together; CI runs it before it
   trusts either gate to pass.
6. **The gate works against real criterion output, not just fixtures.**
   `just bench-baseline` then `just bench-gate` completes and reports a
   comparison — proving the assumed on-disk layout
   (`target/criterion/<bench id>/<baseline>/estimates.json`) is the real one.
7. **Cross-platform L0/L1.** The `check` job matrix contains
   `ubuntu-latest`, `macos-latest`, `windows-latest`.
8. **Toolchain fidelity.** CI resolves its toolchain from `rust-toolchain.toml`
   (1.97.1) rather than pinning a version in YAML, so a toolchain bump is a
   one-line PR that cannot drift from what agents run locally.
9. **Least privilege.** The workflow declares `permissions: contents: read` and a
   `concurrency` group that cancels superseded PR runs.
10. **Lockfile fidelity.** `just lock-check` exits 0, and would fail if
    `Cargo.lock` were stale relative to the manifests.

## Performance constraints

From docs/ARCHITECTURE.md §4, enforced by this pipeline:

- Cold start to first paint: **< 50 ms** (measured today as `cv --version`; see
  non-goal 6).
- Criterion regressions **> 5%** fail (see the significance test above).

The other §4 budgets (FS event → screen, keystroke → paint, scroll fps, memory)
have no code to measure yet and gate nothing in v1.

## Files

New:
- `.github/workflows/ci.yml`
- `ci/bench_gate.py`
- `ci/coldstart_gate.py`
- `ci/README.md`

Modified:
- `justfile` — `coldstart` now asserts a budget; adds `lock-check`,
  `bench-baseline`, `bench-gate`, `perf-gate-selftest` (+ the two it composes),
  `lint-workflows`; `bench` gains `--benches`; `ci` recipe extended.
- `crates/*/Cargo.toml` — `bench = false` on every non-criterion target (see
  "A bug this work surfaced").

`.gitignore` needs no change: hyperfine's JSON export lands in `target/`, which
is already ignored.

## Verification status

Run locally on macOS at the time of writing: AC-1, AC-2 (minus AC-3), AC-4,
AC-5, AC-6, AC-7 (by inspection), AC-8, AC-9 (by inspection), AC-10. Ladder green
— 15 test binaries pass, clippy clean at `-D warnings`.

**Not verified:** AC-3 — `actionlint` is not installed on this machine and I
would not install it or fetch a binary unprompted. The YAML is hand-checked
against the Actions schema but has not been machine-linted. **Nor has any of
this ever executed on GitHub**, because the repo has no remote yet. Treat the
workflow as reviewed-and-locally-reasoned, not proven green.

## Handoff — maintainer actions this spec cannot perform

1. Create the GitHub remote and push (`git remote add origin …`). None of this
   has ever executed; it is reviewed, locally-verified YAML, not proven-green CI.
2. After the first successful run, mark `check`, `e2e`, `perf`, `workflows` as
   required status checks on `main`.
3. Push to `main` once to seed the criterion baseline cache.

## Follow-ups filed

CV-030 (Windows PTY e2e), CV-031 (cold-start against the 10k-file fixture),
CV-032 (pin actions by SHA), CV-033 (L4 adversarial review).
