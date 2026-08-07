# Rust for TypeScript Developers — the code-view dictionary

A translation guide for contributors coming from TypeScript. It covers the language mapping, the exact libraries this project uses, and the idioms you'll meet in this codebase. Read top to bottom once, then use as a lookup table.

## 1. Mental model shift (read this first)

TypeScript adds types to a garbage-collected, exception-throwing, everything-is-a-reference language. Rust's type system instead tracks **who owns every value and how long it lives** — that's what buys us no GC, no data races, and the performance budgets in ARCHITECTURE.md §4.

Three rules explain 90% of ownership:

1. Every value has exactly **one owner**. Assigning or passing by value **moves** it (the old binding is dead — the compiler stops you from using it).
2. You can lend it out: `&T` = read-only borrow (many at once), `&mut T` = exclusive writable borrow (only one, and no readers while it exists).
3. When the owner goes out of scope, the value is dropped (freed). Deterministic — this is why cv can restore your terminal reliably.

When the borrow checker fights you, it is almost always telling you your data-flow design is ambiguous. In cv-core we sidestep most fights by using the Elm pattern: one owner (`AppState`), changes only inside `update()`.

## 2. Language dictionary

| TypeScript | Rust | Notes |
|---|---|---|
| `interface` / structural typing | `trait` + `impl Trait for Type` | Nominal, explicit. Our `Vcs` trait ≈ an interface `cv-vcs` backends implement |
| `type Shape = Circle \| Square` (discriminated union) | `enum Shape { Circle(f64), Square(f64) }` | Rust enums carry data per variant — the single most-used feature in this repo (`Event`, `Effect`, `Verdict`) |
| `switch` + exhaustiveness via `never` | `match` | Exhaustive by default; compiler errors on missing variants |
| `null` / `undefined` / `?.` | `Option<T>` (`Some`/`None`) | No null. `opt?` doesn't exist; use `if let Some(x)`, `.map()`, `.unwrap_or()` |
| `throw` / `try-catch` | `Result<T, E>` (`Ok`/`Err`) + `?` operator | Errors are values. `?` ≈ "return the error upward" — like `await`-ing a rejected promise but explicit and typed |
| `class` | `struct` + `impl` block | Data and methods are declared separately. No inheritance — composition + traits |
| `constructor` | `fn new(...) -> Self` (convention) or `Default` | Just an associated function |
| `readonly` / `const` | immutable by default; `let mut` opts INTO mutability | Inverse of TS |
| generics `<T extends X>` | generics `<T: X>` (trait bounds) | Monomorphized (zero cost), not erased |
| `Promise<T>` + `async/await` | `Future<T>` + `async/await` (via **tokio**) | Futures are lazy — nothing runs until `.await`ed or spawned. No microtask queue; tokio is the event loop we bring ourselves |
| `import { x } from "./mod"` | `use crate::mod::x;` | `mod.rs`/`mod` declarations define the tree; `crate` = this package, `super` = parent module |
| `npm` workspace packages | cargo **workspace** crates | Our six `cv-*` crates = a monorepo of packages |
| `package.json` | `Cargo.toml` | `cargo add serde` ≈ `npm i serde` |
| `Array<T>`, `.map/.filter/.reduce` | `Vec<T>`, iterators: `.iter().map().filter().collect()` | Lazy until `.collect()`; usually faster than a for-loop, never slower |
| `Record<string, T>` / `Map` | `HashMap<String, T>` / `BTreeMap` | BTreeMap when you need sorted iteration (deterministic snapshots!) |
| `string` | `String` (owned) vs `&str` (borrowed slice) | Function params take `&str`; struct fields store `String`. UTF-8 enforced — you can't index by char position (matters for rendering!) |
| template literals | `format!("{name} has {n}")` | Also `println!`, `write!` |
| `JSON.parse/stringify` + zod | **serde** + `#[derive(Serialize, Deserialize)]` | Parsing IS validation — deserialize straight into typed structs |
| `===` deep-equality libs | `#[derive(PartialEq)]` and `==` | Derive it and structural equality just works |
| spread `{...a, b: 2}` | `Struct { b: 2, ..a }` | Struct update syntax |
| destructuring | pattern matching everywhere: `let Point { x, y } = p;` | Works in `match`, `if let`, function args |
| decorators | attribute macros `#[derive(...)]`, `#[test]`, `#[tokio::main]` | Compile-time codegen, much more powerful |
| `unknown` + narrowing | `match` on enums | Model states as enums up front instead of narrowing later |
| `any` | (don't) | The escape hatches are `unsafe` and `Box<dyn Any>` — neither is welcome in this repo |
| closures `(x) => x + 1` | closures `\|x\| x + 1` | Three flavors (`Fn`/`FnMut`/`FnOnce`) by what they capture — compiler guides you |
| `EventEmitter` / RxJS subject | channels: `tokio::sync::mpsc` | Our whole runtime is "tasks send events into one mpsc channel" (ARCHITECTURE.md §3) |
| Web Worker | `tokio::spawn` / `std::thread` | Shared memory is allowed but the type system polices it (`Send`/`Sync`) |
| `structuredClone` | `.clone()` (explicit, visible cost) | Cloning is fine when measured; don't clone in the render path |
| garbage collector | ownership + `Drop` | RAII: cleanup (restoring the TTY!) runs deterministically |
| `Rc`-like shared refs (implicit in JS) | `Rc<T>` / `Arc<T>` (+ `Mutex`/`RwLock` for mutation) | Reach for these LAST in this codebase — prefer single ownership through `AppState` |

## 3. Error handling, the cv way

```rust
// TS: async function load(p: string): Promise<Config> — throws on failure (invisible in the type)
// Rust: failure is in the signature, and `?` propagates it:
fn load(path: &Path) -> Result<Config, ConfigError> {
    let text = fs::read_to_string(path)?;      // io::Error -> ConfigError via From
    let cfg: Config = toml::from_str(&text)?;  // parse+validate in one step (serde)
    Ok(cfg)
}
```

House rules: library crates (`cv-core`, `cv-vcs`, …) define error enums with **thiserror**; the binary (`cv-app`) may use **anyhow** for top-level plumbing. `unwrap()`/`expect()` are allowed only in tests and for provably-impossible states (comment why) — a panic in production means a corrupted terminal for a user mid-review.

## 4. The libraries we use, in TS terms

| Crate | What it is | Nearest TS analogy |
|---|---|---|
| **ratatui** | Immediate-mode TUI framework: every frame you rebuild the widget tree into a buffer; it diffs against the previous buffer and writes minimal escapes | React's render model (re-render everything, framework diffs) — but no retained components or hooks; state lives in `AppState`, not in widgets |
| **crossterm** | Terminal backend: raw mode, key/mouse events, colors | The DOM/browser APIs under React |
| **tokio** | Async runtime: event loop, task spawning, timers, channels | Node's event loop + `worker_threads` + `EventEmitter`, as an opt-in library |
| **gitoxide (`gix`)** | Pure-Rust git implementation | `isomorphic-git`, but fast enough to be the primary backend |
| **tree-sitter** | Incremental parsing framework for syntax highlighting + structure | Same library VS Code and Neovim use — literally the same C core, Rust bindings |
| **notify** | Cross-platform filesystem watcher | `chokidar` |
| **imara-diff** | High-performance line-diff algorithms (Myers/histogram) | The `diff` npm package, ~100× faster |
| **clap** | CLI argument parsing with derive macros | `commander`/`yargs`, but the args become a typed struct |
| **serde** | (De)serialization framework | `JSON.parse` + `zod`, unified, for any format (JSON/TOML/…) |
| **thiserror / anyhow** | Ergonomic error type derivation / dynamic errors | Typed error classes / a good `unknown`-error wrapper |
| **insta** | Snapshot testing (`cargo insta review` to accept) | Jest snapshots |
| **proptest** | Property-based testing | `fast-check` |
| **criterion** | Statistical benchmarking | `benchmark.js`, with regression detection our CI gates on |
| **expectrl** | Drive a real binary in a pseudo-terminal | Playwright, but for the terminal |
| **just** | Command runner (`justfile`) | npm scripts, in their own file |

## 5. Toolchain dictionary

| You know | You'll use | Notes |
|---|---|---|
| `npm install` | `cargo build` | Deps compile from source; first build is slow, then cached |
| `npm run dev` | `cargo run` / `just check` | Always go through `just` here (SDLC rule) |
| `jest` | `cargo test` | Tests live next to code in `#[cfg(test)] mod tests` or in `tests/` |
| `eslint` | `cargo clippy` | CI runs `-D warnings`: lints are errors |
| `prettier` | `cargo fmt` | Zero-config, non-negotiable formatting |
| `tsc --noEmit` | `cargo check` | Fast type-check without codegen — your inner-loop command |
| `package-lock.json` | `Cargo.lock` | Committed |
| `npx tsx script.ts` | `cargo run -p cv-app --` | `-p` picks the workspace crate |
| TypeDoc / JSDoc | `///` doc comments + `cargo doc --open` | Doc examples compile and run as tests (!) |
| VS Code + TS server | VS Code/Zed/Neovim + **rust-analyzer** | Excellent; inlay hints make ownership visible |

## 6. Patterns you'll meet in this codebase

**The Elm architecture (cv-core).** `update(state, event) -> (state, effects)` — if you know Redux, you know this: events are actions, `update` is the reducer, effects are thunks executed by the runtime, and *no I/O happens inside the reducer*. This is a rule the compiler helps enforce: `cv-core` simply has no I/O dependencies.

**Typestate / make-invalid-states-unrepresentable.** Where TS might use `{ mode: "review", hunks?: Hunk[] }` with optional fields and runtime checks, we write `enum Mode { Browse(BrowseState), Review(ReviewState), Live(LiveState) }` so a `Review` without hunks cannot exist. Prefer adding a variant over adding an `Option` field.

**Newtypes.** `struct HunkId(u64);` instead of passing bare `u64`s — like TS branded types, but free and idiomatic. Used for `HunkId`, `Generation`, `TurnMarker`.

**Interior of the render loop: borrow, don't clone.** Widgets take `&AppState` and return drawing instructions. If you find yourself cloning inside `draw()`, stop — that's a design smell in review.

**Generation counters over cancellation.** Async workers (highlighting, structural diff) can't be "cancelled" mid-CPU-work cheaply, so results carry a generation number and stale results are discarded on arrival (ARCHITECTURE.md §3). Think: ignoring a resolved promise from a superseded request.

**`impl Trait` and trait objects.** `fn watcher() -> impl Stream<Item = Event>` (static, fast) vs `Box<dyn Vcs>` (dynamic, swappable backend). Default to static dispatch; `dyn` at genuine plug-in boundaries only (`Vcs`, theme sources).

## 7. Footguns for TS immigrants (learned the hard way, industry-wide)

1. **Fighting the borrow checker with `clone()` everywhere.** It compiles, but it hides design problems and costs frames. Ask "who should own this?" first.
2. **`Rc<RefCell<T>>` as "objects with shared mutable state."** That's writing JS in Rust; runtime borrow panics replace compile errors. Our architecture exists so you don't need it.
3. **Indexing strings** (`s[0]`) doesn't compile, and `s.chars().nth(i)` is O(n) — and neither is what you want for terminal width anyway. Use the width machinery in `cv-ui` (`unicode-width`); a CJK char or emoji is 2 cells wide. This bites every TUI newcomer.
4. **Async without spawning.** An un-`await`ed future does nothing (no "fire and forget" like a dangling promise). Use `tokio::spawn` deliberately.
5. **Blocking in async.** `std::fs` or heavy CPU inside an async task stalls the event loop, exactly like sync work on Node's loop. Use `spawn_blocking` / worker tasks — the render loop's 16 ms budget depends on it.
6. **Expecting exceptions.** Nothing unwinds past `?` unless someone panics. If a function can fail, its signature says so; read signatures, not docs.
7. **Over-generalizing early.** Generic traits with three bounds where a plain enum would do. Rust rewards concrete-first; make it generic when the second real implementation shows up.
8. **Ignoring `#[must_use]` warnings** on `Result` — that's the compiler telling you an error is being dropped on the floor. Never `let _ =` a `Result` without a comment.

## 8. Learning path (ordered, ~free)

1. **The Rust Book** (doc.rust-lang.org/book) — chapters 1–10 are enough to start; do 13 (iterators/closures) and 16 (concurrency) before touching the runtime.
2. **Rustlings** — small exercises; the ownership/borrowing/enum sections map 1:1 to what this repo needs.
3. **The Ratatui tutorial** (ratatui.rs/tutorials) — build the counter app, then the JSON editor; you'll recognize our architecture immediately.
4. **tokio tutorial** (tokio.rs) — through "channels".
5. Then: pick a `good-first-issue` from `.project/BACKLOG.md` — each has a spec with acceptance criteria, and `just snapshot` lets you *see* your UI as text while you work. The compiler + the test ladder will carry you.

*Meta-tip: Rust's compiler errors are the best teacher in systems programming — read them fully, including the `help:` lines, before reaching for an agent or a search. And when you do use an agent: this repo's CLAUDE.md conventions (test-first, `just check` after every edit) exist precisely because agents write good Rust when the loop is tight.*
