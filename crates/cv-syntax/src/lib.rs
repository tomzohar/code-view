//! Syntax highlighting and diff computation.
//!
//! Two tiers, and the split matters: the line diff (`imara-diff`) renders
//! *instantly*, while structural refinement (moved code, syntax-aware intra-line
//! spans) computes asynchronously and upgrades the view when ready. First paint
//! is never blocked on the fancy pass.
//!
//! Highlighting lands in CV-004, structural refinement in CV-018.

/// Line-diff algorithm used for the instant tier.
///
/// Histogram beats Myers by 10–100% on real-world code and is what git uses for
/// `--histogram`; the choice matters because this runs on the render path.
pub const LINE_DIFF_ALGORITHM: imara_diff::Algorithm = imara_diff::Algorithm::Histogram;

/// Number of tree-sitter grammars linked into this build.
///
/// Zero today — grammars are bundled and lazy-loaded starting with CV-004.
pub fn grammar_count() -> usize {
    0
}

#[cfg(test)]
mod tests {
    use super::*;
    use imara_diff::{Diff, InternedInput};

    #[test]
    fn line_diff_finds_the_changed_line() {
        let input = InternedInput::new("fn a() {}\nfn b() {}\n", "fn a() {}\nfn c() {}\n");
        let mut diff = Diff::compute(LINE_DIFF_ALGORITHM, &input);
        diff.postprocess_lines(&input);

        assert!(!diff.is_removed(0) && !diff.is_added(0));
        assert!(diff.is_removed(1) && diff.is_added(1));
    }

    #[test]
    fn tree_sitter_parser_constructs() {
        // Proves the tree-sitter C runtime is linked; grammars arrive with CV-004.
        let parser = tree_sitter::Parser::new();
        assert!(parser.language().is_none());
    }
}
