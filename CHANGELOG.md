# Changelog

## 1.1.1 - 2026-10-18

- Refuse existing output files, source aliases and symlink destinations; report file errors with exit code 2.
- Preserve already accepted checked Markdown tasks in reports and support their boolean JSON completion value.
- Reject non-text and blank task fields instead of coercing them or silently dropping blank dependencies.
- Diagnose long cyclic checklists iteratively and return deterministic concrete cycle witnesses.
- Escape multiline text in DOT labels and document report/interchange limits.

## 1.1.0 - 2026-10-15

- Add opt-in dependency layers in text, Markdown and JSON, preserving the default stable order.
- Refuse complete layer claims for missing references or cyclic graphs; preserve diagnostics and exit codes.


## 1.0.0 - 2026-07-18

- Added deterministic dependency ordering for JSON and Markdown checklists.
- Added explicit missing-reference and cycle-path diagnostics.
- Added text, Markdown, JSON, and Graphviz DOT reports.
- Added tests, packaging, and cross-platform CI.
