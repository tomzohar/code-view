//! Ratatui widget set: `FileTree`, `CodeView`, `DiffView`, `HunkBar`,
//! `CommandPalette`, `StatusLine`, `HelpOverlay`.
//!
//! Rendering is virtualized — only visible lines are laid out and highlighted —
//! because the keystroke-to-paint budget is 16 ms on files of any size.
//!
//! Widgets land in CV-004 (tree + code view) and CV-010 (diff view). Every one
//! of them starts with a `TestBackend` snapshot test: that rendered text is both
//! the regression gate and the "screenshot" a human reviews (docs/SDLC.md §2).

/// Renders `frame`'s full area as plain text, one line per row.
///
/// This is the seam the snapshot harness (CV-005) builds on: it turns any screen
/// state into a diffable string, so agents can inspect their own UI without a
/// terminal.
pub fn buffer_to_lines(buffer: &ratatui::buffer::Buffer) -> Vec<String> {
    let area = buffer.area();
    (0..area.height)
        .map(|y| {
            (0..area.width)
                .map(|x| buffer[(area.x + x, area.y + y)].symbol())
                .collect::<String>()
                .trim_end()
                .to_string()
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    use ratatui::{Terminal, backend::TestBackend, widgets::Paragraph};

    #[test]
    fn test_backend_round_trips_to_text() {
        let mut terminal = Terminal::new(TestBackend::new(12, 2)).unwrap();
        terminal
            .draw(|frame| frame.render_widget(Paragraph::new("cv"), frame.area()))
            .unwrap();

        let lines = buffer_to_lines(terminal.backend().buffer());
        assert_eq!(lines, vec!["cv".to_string(), String::new()]);
    }
}
