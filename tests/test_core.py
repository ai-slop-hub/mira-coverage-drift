from coverage_drift.core import analyze, parse_coverage_json, parse_diff


def test_regression_detected():
    r = analyze({1, 2, 3}, {1, 2}, {2, 3})
    assert r.regressed == {3}
    assert r.ok is False


def test_improvement_and_stable():
    r = analyze({1}, {1, 2}, {1, 2, 4})
    assert r.improved == {2}
    assert r.stable_covered == {1}
    assert r.ok is True


def test_unchanged_lines_ignored():
    r = analyze({10}, set(), {1})
    assert r.regressed == frozenset()
    assert r.ok is True


def test_qualified_keys():
    base = {("a.py", 1), ("a.py", 2)}
    head = {("a.py", 1)}
    changed = {("a.py", 2)}
    assert analyze(base, head, changed).regressed == {("a.py", 2)}


def test_parse_coverage_json():
    text = '{"files": {"m.py": {"executed_lines": [1, 3]}}}'
    assert parse_coverage_json(text) == {("m.py", 1), ("m.py", 3)}


def test_parse_diff_and_integration():
    diff = "--- a/m.py\n+++ b/m.py\n@@ -1,2 +1,3 @@\n x\n-y\n+z\n+w\n"
    changed = parse_diff(diff)
    assert changed == {("m.py", 2), ("m.py", 3)}
    cov = parse_coverage_json('{"files": {"m.py": {"executed_lines": [1, 2]}}}')
    assert analyze(cov, cov, changed).ok is True
