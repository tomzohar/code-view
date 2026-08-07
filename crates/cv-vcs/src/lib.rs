//! Version-control access for code-view.
//!
//! gitoxide (`gix`) is the primary backend; the `git` CLI is the escape hatch for
//! exotic cases. Everything is exposed behind a `Vcs` trait so another backend
//! (jujutsu, CV-025) can arrive without touching `cv-core`.
//!
//! Implementation lands in CV-008.

/// Opens the repository containing `path`, walking upwards like `git` does.
///
/// Returns the working-directory root as an absolute path. gitoxide reports it
/// relative to whatever it was handed (`.` in, `.` out), and every caller
/// downstream — window titles, feedback-file headers, session identity — wants
/// something stable instead.
pub fn discover(path: &std::path::Path) -> Result<std::path::PathBuf, Error> {
    let repo = gix::discover(path)?;
    let workdir = repo.workdir().ok_or(Error::BareRepository)?;
    workdir
        .canonicalize()
        .map_err(|source| Error::Canonicalize {
            path: workdir.to_path_buf(),
            source,
        })
}

/// Failures surfaced by the VCS layer. cv renders a degraded-but-honest view
/// rather than exiting, so these are always recoverable at the call site.
#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("no git repository found")]
    Discover(#[from] Box<gix::discover::Error>),
    #[error("repository has no working directory (bare repo)")]
    BareRepository,
    #[error("cannot resolve repository root {path}")]
    Canonicalize {
        path: std::path::PathBuf,
        source: std::io::Error,
    },
}

impl From<gix::discover::Error> for Error {
    fn from(err: gix::discover::Error) -> Self {
        Self::Discover(Box::new(err))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn discovers_this_repository() {
        let here = std::path::Path::new(env!("CARGO_MANIFEST_DIR"));
        let root = discover(here).expect("code-view is itself a git repo");
        assert!(root.join("Cargo.toml").is_file());
    }

    #[test]
    fn root_is_absolute_even_for_a_relative_input() {
        let root = discover(std::path::Path::new(".")).expect("cwd is inside a git repo");
        assert!(root.is_absolute(), "got {}", root.display());
    }
}
