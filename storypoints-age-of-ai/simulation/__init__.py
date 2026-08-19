"""Route B synthetic evaluation utilities.

This package supports design-science evaluation only.  It does not validate the
framework against people, teams, or organizations.
"""

from .comparators import ComparatorSuite, ComparatorParameters
from .evaluation import evaluate_forecasts
from .seeds import SeedManifest, build_seed_manifest
from .verification import HardStopError, run_hard_stop_checks
from .engine import SimulationResult, run_truth

__all__ = [
    "ComparatorParameters",
    "ComparatorSuite",
    "HardStopError",
    "SeedManifest",
    "build_seed_manifest",
    "evaluate_forecasts",
    "run_hard_stop_checks",
    "SimulationResult",
    "run_truth",
]
