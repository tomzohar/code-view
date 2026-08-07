# ADR-0001: Rust + Ratatui as the implementation stack

- **Status:** accepted
- **Date:** 2026-08-07
- **Deciders:** Tom (maintainer); drafted by agent session (cowork/claude)

## Context
code-view's core promises are extreme rendering performance (50 ms cold start, 60 fps on 10k-line diffs, <100 ms live updates), single-binary distribution, and reliability inside other people's terminals. The TUI must virtualize rendering, run tree-sitter and diff computation off the render path, and never leak or crash the TTY.

## Decision
Rust with Ratatui (crossterm backend), tokio for the async runtime, gitoxide for VCS access, tree-sitter for syntax, notify for file watching, imara-diff for line diffing.

## Alternatives considered
- **Go + Bubble Tea:** excellent productivity and precedent (lazygit, glow), but weaker raw rendering throughput, GC pauses risk frame budget on giant diffs, and the tree-sitter/gitoxide-equivalent ecosystem is thinner.
- **TypeScript + Ink/OpenTUI:** lowest contributor barrier and matches agent-CLI stacks, but requires a Node runtime or heavyweight bundling, and per-frame performance on 100k-line files is not credible against our budgets.
- **Zig / C++:** performance parity but ecosystem (TUI frameworks, git libraries, contributor pool, agent training data) far behind Rust's.

## Consequences
Easier: hitting performance budgets; static binaries via cargo-dist; riding the proven ratatui/tree-sitter/gitoxide stack (gitui, helix, yazi precedent); strong typing helps agent-generated code fail at compile time rather than runtime. Harder: steeper contributor curve than Go/TS; compile times (mitigate with workspace splitting and sccache in CI). Revisit-trigger: none anticipated; superseding this ADR means rewriting the product.
