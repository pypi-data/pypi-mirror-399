"""
Netspecs - Cross-platform internet diagnostics with AI-powered analysis.
"""

__version__ = "0.1.0"
__author__ = "developer@dev.com"

from netspecs.core.latency import test_latency, LatencyResult
from netspecs.core.speed import test_speed, SpeedResult
from netspecs.core.jitter import measure_jitter, JitterResult
from netspecs.core.connectivity import check_connectivity, ConnectivityResult
from netspecs.core.prioritization import detect_prioritization, PrioritizationResult

__all__ = [
    "__version__",
    "test_latency",
    "LatencyResult",
    "test_speed",
    "SpeedResult",
    "measure_jitter",
    "JitterResult",
    "check_connectivity",
    "ConnectivityResult",
    "detect_prioritization",
    "PrioritizationResult",
]

