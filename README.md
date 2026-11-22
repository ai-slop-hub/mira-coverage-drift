# mira-coverage-drift
Aggregate coverage percentages and delta-verify/mutation-audit miss the case where a PR raises overall coverage while silently dropping coverage on the specific lines it touched — engineers approve with false confidence because the headline number went up. This tool answers 'did coverage of the code you changed actually improve or regress?' by diff
