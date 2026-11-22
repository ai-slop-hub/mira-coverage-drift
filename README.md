# coverage-drift

Fail a PR when the lines it changed lose coverage, even if the aggregate percentage rose.

## Purpose
A headline coverage number can go up while the specific lines a PR touched go dark. coverage-drift diffs line-level coverage between two git refs (base vs head) and reports regressions on the changed lines only. It consumes coverage artifacts — it never runs tests — so it is fast, deterministic, and CI-friendly.

## Usage
```python
from coverage_drift.core import analyze

result = analyze(
    base_covered={1, 2, 3},
    head_covered={1, 2},
    changed_lines={2, 3},
)
assert result.regressed == {3}   # changed line 3 went dark
assert result.improved == set()
assert result.ok is False
```
`analyze()` returns a `DriftReport` with `regressed`, `improved`, `stable_covered`, and `ok`. Regressed = changed lines covered at base but not head. Improved = changed lines uncovered at base but covered at head.

Parse coverage.py JSON reports and unified diffs:
```python
from coverage_drift.core import parse_coverage_json, parse_diff
```

## Design
All state is sets of integer line numbers — no dicts as dict keys, no hashability traps. Coverage is keyed by `(filename, lineno)`; diff parsing yields changed line sets per file. The core has no I/O beyond parsing strings, making it directly testable. Exit code 1 when `ok` is False, suitable as a CI gate.
