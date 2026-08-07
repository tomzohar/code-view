//! Validation ladder L2: end-to-end scenarios driving the real `cv` binary
//! inside a PTY (docs/SDLC.md §1).
//!
//! A PTY is not optional here — cv behaves differently when stdout is a pipe,
//! and terminal-restoration bugs only reproduce against a real terminal.
//!
//! The scenario suite proper (fixture repos, scripted key sequences, screen
//! assertions) lands with CV-005; this is the harness smoke test.

use std::path::PathBuf;

/// Absolute path to the `cv` binary built for this test run.
///
/// Cargo guarantees this binary exists and is up to date before the test starts.
fn cv_binary() -> PathBuf {
    PathBuf::from(env!("CARGO_BIN_EXE_cv"))
}

#[test]
fn binary_reports_its_version_in_a_pty() {
    let cmd = format!("{} --version", cv_binary().display());
    let mut session = expectrl::spawn(&cmd).expect("spawn cv in a pty");

    session.expect("cv").expect("version line mentions cv");
}

#[test]
fn opening_a_repository_reports_its_root() {
    let repo_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../..")
        .canonicalize()
        .expect("workspace root");

    let cmd = format!("{} {}", cv_binary().display(), repo_root.display());
    let mut session = expectrl::spawn(&cmd).expect("spawn cv in a pty");

    session
        .expect("repository:")
        .expect("cv reports the repo it opened");
}
