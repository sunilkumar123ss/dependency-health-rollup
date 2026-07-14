# Dependency Health Rollup

Summarize dependency status using criticality and observation freshness.

All bundled examples use synthetic data.

## Run

Requires Python 3.9 or later; no third-party packages or network access are needed.

```sh
python3 main.py
python3 main.py --help
python3 -m unittest -v
```

Run these commands from this repository's directory. The demo can also be launched from any directory by passing the absolute path to `main.py`.

## How it works

Each dependency reports `healthy`, `degraded`, `unhealthy`, or `unknown`, with a timestamp and critical flag. A check older than `max_age_seconds` becomes effectively unknown while retaining its reported status. An unhealthy or unknown critical dependency makes the service unhealthy. Other nonhealthy dependencies make it degraded. An empty input reports unknown.

Results are sorted by dependency name so explanations do not depend on input order. Validation rejects duplicate names, invalid statuses, and future observations. Runtime is O(n log n) due to sorting, with O(n) result memory.

## Reuse

```python
from main import DependencyCheck, rollup

checks = [DependencyCheck("database", "healthy", True, 95),
          DependencyCheck("recommendations", "unhealthy", False, 99)]
summary = rollup(checks, now=100, max_age_seconds=30)
assert summary.status == "degraded"
assert "optional" in summary.reasons[0]
```

## Demo behavior

The demo has healthy critical database/payment dependencies and one unhealthy optional recommendation dependency. The resulting degraded status explains that optional failure.

## Boundaries

This is a policy function, not an active health probe. It does not perform HTTP calls, infer topology, or apply hysteresis. Freshness is inclusive at the exact age boundary; future observations are rejected rather than adjusted for clock skew. The caller chooses criticality and supplies timestamps from a consistent clock. Applications may need a different policy for startup, partial service availability, or cascading dependencies.

## Verification

`test_main.py` exercises boundary conditions, invalid inputs, and meaningful behavior specific to this implementation. The default demo is deterministic and completes without external services. See the collection's verification report for the recorded run; run the commands above to verify this repository independently.

## Repository checks

```sh
python3 verify.py
```

This runs the isolated test suite, synthetic example, and CLI help. The included GitHub Actions workflow repeats these checks when the repository is published. No hosted CI result is claimed by the local verification report.
