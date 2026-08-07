//! Filesystem and git-state watching.
//!
//! `notify` events are debounced and coalesced into batches, then handed to
//! `cv-core` as `FileChanged` / `GitStateChanged`. The budget for the whole
//! chain — fs event to updated diff on screen — is 100 ms
//! (docs/ARCHITECTURE.md §4).
//!
//! Implementation lands in CV-014.

use std::time::Duration;

/// Default debounce window for coalescing filesystem events.
///
/// Agents write files in bursts; without coalescing every save would trigger a
/// full diff recompute.
pub const DEFAULT_DEBOUNCE: Duration = Duration::from_millis(30);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn debounce_stays_within_the_live_update_budget() {
        assert!(DEFAULT_DEBOUNCE < Duration::from_millis(100));
    }
}
