"""Jitter measurement module for netspecs."""

from __future__ import annotations

import re
import statistics
import subprocess
import time
from dataclasses import dataclass
from typing import Optional

from netspecs.utils.platform import get_ping_command, get_system, run_command


def _percentile(data: list[float], p: int) -> float:
    """Calculate percentile of a sorted list."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * p / 100
    f = int(k)
    c = f + 1 if f + 1 < len(sorted_data) else f
    return sorted_data[f] + (sorted_data[c] - sorted_data[f]) * (k - f)


@dataclass
class JitterResult:
    """Result of a jitter measurement."""
    
    host: str
    duration_seconds: int
    samples: int
    jitter_ms: float  # Standard deviation (true jitter)
    min_ms: float
    max_ms: float
    avg_ms: float
    std_dev_ms: float
    
    # Percentile metrics (more useful than range)
    p50_ms: float = 0.0  # Median
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    
    # Packet loss during measurement
    timeouts: int = 0
    loss_percent: float = 0.0
    
    success: bool = True
    latencies: list[float] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.latencies is None:
            self.latencies = []
    
    def to_dict(self) -> dict:
        """Convert result to dictionary."""
        return {
            "host": self.host,
            "duration_seconds": self.duration_seconds,
            "samples": self.samples,
            "jitter_ms": self.jitter_ms,
            "min_ms": self.min_ms,
            "max_ms": self.max_ms,
            "avg_ms": self.avg_ms,
            "std_dev_ms": self.std_dev_ms,
            "p50_ms": self.p50_ms,
            "p95_ms": self.p95_ms,
            "p99_ms": self.p99_ms,
            "timeouts": self.timeouts,
            "loss_percent": self.loss_percent,
            "success": self.success,
            "error": self.error,
        }
    
    @property
    def status(self) -> str:
        """Get status indicator based on jitter."""
        if not self.success:
            return "error"
        elif self.jitter_ms > 30:
            return "warning"
        elif self.jitter_ms > 10:
            return "moderate"
        else:
            return "ok"


def _extract_latency_from_ping(output: str) -> Optional[float]:
    """Extract single latency value from ping output."""
    system = get_system()
    
    if system == "Windows":
        # Windows: time=XXms or time<1ms
        match = re.search(r"time[=<](\d+)ms", output)
        if match:
            return float(match.group(1))
    else:
        # Unix: time=XX.XX ms
        match = re.search(r"time=([\d.]+)\s*ms", output)
        if match:
            return float(match.group(1))
    
    return None


def measure_jitter(
    host: str,
    duration: int = 60,
    interval: float = 1.0,
) -> JitterResult:
    """
    Measure jitter (latency variation) over time.
    
    Jitter is calculated as the standard deviation of latency samples,
    which is the proper definition used in networking (not max - min).
    
    Args:
        host: Target host to ping
        duration: Measurement duration in seconds (default increased to 60)
        interval: Interval between pings in seconds
        
    Returns:
        JitterResult with jitter statistics including percentiles
    """
    latencies: list[float] = []
    timeouts = 0
    total_attempts = 0
    
    start_time = time.time()
    end_time = start_time + duration
    
    while time.time() < end_time:
        total_attempts += 1
        try:
            cmd = get_ping_command(host, count=1, timeout=2)
            result = run_command(cmd, timeout=5)
            output = result.stdout + result.stderr
            
            latency = _extract_latency_from_ping(output)
            if latency is not None:
                latencies.append(latency)
            else:
                timeouts += 1
                
        except Exception:
            timeouts += 1
        
        # Wait for next interval
        elapsed = time.time() - start_time
        next_ping = ((elapsed // interval) + 1) * interval
        sleep_time = next_ping - elapsed
        if sleep_time > 0 and time.time() + sleep_time < end_time:
            time.sleep(sleep_time)
    
    # Calculate loss percentage
    loss_percent = (timeouts / total_attempts * 100) if total_attempts > 0 else 0
    
    if len(latencies) < 2:
        return JitterResult(
            host=host,
            duration_seconds=duration,
            samples=len(latencies),
            jitter_ms=0.0,
            min_ms=latencies[0] if latencies else 0.0,
            max_ms=latencies[0] if latencies else 0.0,
            avg_ms=latencies[0] if latencies else 0.0,
            std_dev_ms=0.0,
            timeouts=timeouts,
            loss_percent=round(loss_percent, 2),
            success=False,
            latencies=latencies,
            error="Insufficient samples for jitter calculation",
        )
    
    # Calculate statistics
    min_ms = min(latencies)
    max_ms = max(latencies)
    avg_ms = statistics.mean(latencies)
    std_dev_ms = statistics.stdev(latencies)
    
    # Calculate percentiles
    p50_ms = _percentile(latencies, 50)
    p95_ms = _percentile(latencies, 95)
    p99_ms = _percentile(latencies, 99)
    
    # Jitter is the standard deviation of latency (NOT max - min)
    jitter_ms = std_dev_ms
    
    return JitterResult(
        host=host,
        duration_seconds=duration,
        samples=len(latencies),
        jitter_ms=round(jitter_ms, 2),
        min_ms=round(min_ms, 2),
        max_ms=round(max_ms, 2),
        avg_ms=round(avg_ms, 2),
        std_dev_ms=round(std_dev_ms, 2),
        p50_ms=round(p50_ms, 2),
        p95_ms=round(p95_ms, 2),
        p99_ms=round(p99_ms, 2),
        timeouts=timeouts,
        loss_percent=round(loss_percent, 2),
        success=True,
        latencies=latencies,
    )


def measure_jitter_batch(
    hosts: list[str],
    duration: int = 30,
    interval: int = 1,
) -> list[JitterResult]:
    """
    Measure jitter for multiple hosts sequentially.
    
    Args:
        hosts: List of target hosts
        duration: Measurement duration per host in seconds
        interval: Interval between pings in seconds
        
    Returns:
        List of JitterResult objects
    """
    results = []
    for host in hosts:
        result = measure_jitter(host, duration, interval)
        results.append(result)
    return results

