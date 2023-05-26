"""Roll up dependency checks using criticality and explicit freshness policy."""
import argparse
from dataclasses import asdict, dataclass
import json
import math


STATUSES = {"healthy", "degraded", "unhealthy", "unknown"}


