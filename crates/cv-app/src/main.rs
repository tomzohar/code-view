//! The `cv` binary: CLI parsing, config, session wiring.
//!
//! Zero-config is a product invariant — `cv` with no arguments does the right
//! thing in any git repo. The full surface (`cv diff <range>`, pager mode,
//! `--mcp`) arrives with CV-011 and CV-023; today it resolves the repository and
//! reports what it found, which is enough to prove the crate graph end to end.

use clap::Parser;

#[derive(Debug, Parser)]
#[command(name = "cv", version, about, long_about = None)]
struct Cli {
    /// Path inside the repository to open. Defaults to the current directory.
    path: Option<std::path::PathBuf>,
}

fn main() -> anyhow::Result<()> {
    let cli = Cli::parse();
    let start = cli.path.unwrap_or_else(|| std::path::PathBuf::from("."));

    let root = cv_vcs::discover(&start)?;
    println!("cv {} (pre-alpha)", cv_core::VERSION);
    println!("repository: {}", root.display());
    println!("The TUI is not built yet — see .project/BACKLOG.md (CV-004).");

    Ok(())
}
