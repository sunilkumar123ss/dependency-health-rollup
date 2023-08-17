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
