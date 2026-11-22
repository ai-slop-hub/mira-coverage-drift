from __future__ import annotations

import json
import re
from dataclasses import dataclass

Key = tuple[str, int]


@dataclass(frozen=True)
class DriftReport:
    regressed: frozenset[Key]
    improved: frozenset[Key]
    stable_covered: frozenset[Key]
    ok: bool


def analyze(
    base_covered: set[Key] | set[int],
    head_covered: set[Key] | set[int],
    changed_lines: set[Key] | set[int],
) -> DriftReport:
    """Compare per-line coverage restricted to changed lines.

    Accepts either fully-qualified (filename, lineno) keys or bare ints
    for single-file use; all three inputs must use the same shape.
    """
    regressed = frozenset(changed_lines & base_covered - head_covered)
    improved = frozenset(changed_lines & head_covered - base_covered)
    stable = frozenset(changed_lines & base_covered & head_covered)
    return DriftReport(
        regressed=regressed,
        improved=improved,
        stable_covered=stable,
        ok=not regressed,
    )


def parse_coverage_json(text: str) -> set[Key]:
    """Parse a coverage.py JSON report into covered (file, line) keys."""
    data = json.loads(text)
    result: set[Key] = set()
    for filename, info in data.get("files", {}).items():
        for lineno in info.get("executed_lines", []):
            result.add((filename, int(lineno)))
    return result


_HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def parse_diff(text: str) -> set[Key]:
    """Parse a unified diff into changed (file, line) keys on the new side."""
    result: set[Key] = set()
    filename: str | None = None
    new_line = 0
    for line in text.splitlines():
        if line.startswith("+++ b/"):
            filename = line[6:]
        elif line.startswith("@@"):
            m = _HUNK.match(line)
            if m:
                new_line = int(m.group(1))
        elif filename and line.startswith("+") and not line.startswith("+++"):
            result.add((filename, new_line))
            new_line += 1
        elif filename and line.startswith(" ") and not line.startswith("---") and new_line:
            new_line += 1
    return result
