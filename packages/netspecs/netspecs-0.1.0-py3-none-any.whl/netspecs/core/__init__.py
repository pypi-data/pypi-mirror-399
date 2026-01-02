"""Core diagnostic modules for netspecs."""

from netspecs.core.latency import test_latency, LatencyResult
from netspecs.core.speed import test_speed, SpeedResult
from netspecs.core.jitter import measure_jitter, JitterResult
from netspecs.core.connectivity import check_connectivity, ConnectivityResult
from netspecs.core.prioritization import detect_prioritization, PrioritizationResult
from netspecs.core.bufferbloat import test_bufferbloat, BufferbloatResult
from netspecs.core.network_info import capture_network_info, NetworkInfo
from netspecs.core.monitor import long_monitor, MonitoringResult

__all__ = [
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
    "test_bufferbloat",
    "BufferbloatResult",
    "capture_network_info",
    "NetworkInfo",
    "long_monitor",
    "MonitoringResult",
]

