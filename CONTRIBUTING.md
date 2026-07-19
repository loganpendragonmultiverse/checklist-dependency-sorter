# Contributing

Bug reports, focused feature proposals, documentation improvements, and pull requests are welcome. Please open an issue before adding a new input format or changing ordering semantics.

For code changes:

1. Fork the repository and create a focused branch.
2. Install with `python -m pip install -e . pytest build`.
3. Add behavior-oriented tests for ordering and diagnostics.
4. Run `python -m pytest` and `python -m build`.
5. Update the README and changelog when public behavior changes.
6. Submit a pull request explaining the input, expected order, edge cases, and verification performed.

Ordering must remain deterministic, and errors must remain actionable. A maintainer reviews every pull request; passing checks do not guarantee merge.
