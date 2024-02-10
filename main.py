"""Roll up dependency checks using criticality and explicit freshness policy."""
import argparse
from dataclasses import asdict, dataclass
import json
import math


STATUSES = {"healthy", "degraded", "unhealthy", "unknown"}


def finite(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(name + " must be finite")
    return value


@dataclass(frozen=True)
class DependencyCheck:
    name: str
    status: str
    critical: bool
    observed_at: float


@dataclass(frozen=True)
class HealthSummary:
    status: str
    reasons: tuple
    dependencies: tuple


def rollup(checks, now, max_age_seconds=30):
    finite(now, "now")
    finite(max_age_seconds, "max_age_seconds")
    if max_age_seconds < 0:
        raise ValueError("max_age_seconds must be nonnegative")
    checks = list(checks)
    names = set()
    for check in checks:
        if not isinstance(check, DependencyCheck):
            raise ValueError("checks must be DependencyCheck instances")
        if not isinstance(check.name, str) or not check.name.strip() or check.name in names:
            raise ValueError("dependency names must be nonempty and unique")
        names.add(check.name)
        if check.status not in STATUSES or type(check.critical) is not bool:
            raise ValueError("invalid dependency status or criticality")
        finite(check.observed_at, "observed_at")
        if check.observed_at > now:
            raise ValueError("observation cannot be in the future")
    if not checks:
        return HealthSummary("unknown", ("no dependency checks supplied",), ())
    severity = 0
    reasons, details = [], []
    for check in sorted(checks, key=lambda item: item.name):
        age = now - check.observed_at
        stale = age > max_age_seconds
        effective = "unknown" if stale else check.status
        details.append({"name": check.name, "reported_status": check.status,
                        "effective_status": effective, "critical": check.critical,
                        "age_seconds": age, "stale": stale})
        if effective == "healthy":
            continue
        if check.critical and effective in {"unhealthy", "unknown"}:
            severity = 2
        else:
            severity = max(severity, 1)
        reason = "stale check" if stale else effective
        reasons.append("{}: {} ({})".format(check.name, reason, "critical" if check.critical else "optional"))
    return HealthSummary(("healthy", "degraded", "unhealthy")[severity], tuple(reasons), tuple(details))


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    checks = [DependencyCheck("database", "healthy", True, 95),
              DependencyCheck("payments", "healthy", True, 99),
              DependencyCheck("recommendations", "unhealthy", False, 98)]
    print(json.dumps(asdict(rollup(checks, now=100, max_age_seconds=30)), indent=2))


if __name__ == "__main__":
    main()
