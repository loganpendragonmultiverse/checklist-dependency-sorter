# Changelog

## 1.1.0 - 2026-10-15

- Add opt-in dependency layers in text, Markdown and JSON, preserving the default stable order.
- Refuse complete layer claims for missing references or cyclic graphs; preserve diagnostics and exit codes.


## 1.0.0 - 2026-07-18

- Added deterministic dependency ordering for JSON and Markdown checklists.
- Added explicit missing-reference and cycle-path diagnostics.
- Added text, Markdown, JSON, and Graphviz DOT reports.
- Added tests, packaging, and cross-platform CI.
