//! The agent bridge: how human review leaves cv and reaches an agent.
//!
//! Three surfaces, all optional and additive (docs/ARCHITECTURE.md §2):
//! 1. feedback files in `.cv/` — works with every agent, ships first (CV-016);
//! 2. hook adapters over a unix socket — turn boundaries (CV-021);
//! 3. MCP server mode — agents pull review state (CV-023).
//!
//! The feedback-file format is public API: changing it requires an ADR.

/// Directory, relative to the repository root, that cv writes review output to.
///
/// cv is read-only over source and write-only over this directory — the trust
/// boundary the product is built on (docs/VISION.md, principle 4).
pub const FEEDBACK_DIR: &str = ".cv";

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn feedback_dir_is_repo_relative() {
        assert!(!std::path::Path::new(FEEDBACK_DIR).is_absolute());
    }
}
