//! Domain model for code-view: `AppState`, events, and the pure reducer.
//!
//! This crate is deliberately **pure** — no filesystem, no git, no terminal, no
//! async runtime. Everything is a function of the events fed in, which is what
//! makes the app unit-testable, replayable and fuzzable without a TTY.
//!
//! The reducer itself lands in CV-003; this crate currently only pins the shape.

/// Semantic version of the running `cv` build, taken from the workspace manifest.
pub const VERSION: &str = env!("CARGO_PKG_VERSION");

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn version_is_populated() {
        assert!(!VERSION.is_empty());
    }
}
