"""Bufferbloat detection module - tests latency under load."""

from __future__ import annotations

import re
import statistics
import subprocess
import threading
import time
from dataclasses import dataclass, field
from typing import Optional

import httpx

from netspecs.utils.platform import get_ping_command, get_system, run_command


@dataclass
class BufferbloatResult:
    """Result of a bufferbloat (latency under load) test."""
    
    host: str
    duration_seconds: int
    
    # Baseline (idle) statistics
    baseline_avg_ms: float
    baseline_p50_ms: float
    baseline_p95_ms: float
    baseline_p99_ms: float
    baseline_samples: int
    
    # Under load statistics
    loaded_avg_ms: float
    loaded_p50_ms: float
    loaded_p95_ms: float
    loaded_p99_ms: float
    loaded_samples: int
    loaded_max_ms: float
    
    # Analysis
    bloat_increase_ms: float  # loaded_p95 - baseline_p95
    bloat_factor: float  # loaded_p95 / baseline_p95
    grade: str  # A, B, C, D, F based on bloat
    
    success: bool
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert result to dictionary."""
        return {
            "host": self.host,
            "duration_seconds": self.duration_seconds,
            "baseline_avg_ms": self.baseline_avg_ms,
            "baseline_p50_ms": self.baseline_p50_ms,
            "baseline_p95_ms": self.baseline_p95_ms,
            "baseline_p99_ms": self.baseline_p99_ms,
            "baseline_samples": self.baseline_samples,
            "loaded_avg_ms": self.loaded_avg_ms,
            "loaded_p50_ms": self.loaded_p50_ms,
            "loaded_p95_ms": self.loaded_p95_ms,
            "loaded_p99_ms": self.loaded_p99_ms,
            "loaded_samples": self.loaded_samples,
            "loaded_max_ms": self.loaded_max_ms,
            "bloat_increase_ms": self.bloat_increase_ms,
            "bloat_factor": self.bloat_factor,
            "grade": self.grade,
            "success": self.success,
            "error": self.error,
        }


def _extract_latency(output: str) -> Optional[float]:
    """Extract single latency value from ping output."""
    system = get_system()
    
    if system == "Windows":
        match = re.search(r"time[=<](\d+)ms", output)
        if match:
            return float(match.group(1))
    else:
        match = re.search(r"time=([\d.]+)\s*ms", output)
        if match:
            return float(match.group(1))
    
    return None


def _percentile(data: list[float], p: int) -> float:
    """Calculate percentile of a list."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * p / 100
    f = int(k)
    c = f + 1 if f + 1 < len(sorted_data) else f
    return sorted_data[f] + (sorted_data[c] - sorted_data[f]) * (k - f)


def _measure_latency_series(
    host: str,
    duration: int,
    interval: float = 0.5,
) -> list[float]:
    """Measure a series of latency samples."""
    latencies = []
    start_time = time.time()
    end_time = start_time + duration
    
    while time.time() < end_time:
        try:
            cmd = get_ping_command(host, count=1, timeout=2)
            result = run_command(cmd, timeout=5)
            output = result.stdout + result.stderr
            
            latency = _extract_latency(output)
            if latency is not None:
                latencies.append(latency)
        except Exception:
            pass
        
        # Short interval for more samples
        time.sleep(interval)
    
    return latencies


def _generate_download_load(duration: int, stop_event: threading.Event):
    """Generate download traffic to create network load."""
    urls = [
        "http://speedtest.tele2.net/100MB.zip",
        "http://ipv4.download.thinkbroadband.com/100MB.zip",
    ]
    
    start_time = time.time()
    while time.time() - start_time < duration and not stop_event.is_set():
        for url in urls:
            if stop_event.is_set():
                break
            try:
                with httpx.Client(timeout=30, follow_redirects=True) as client:
                    with client.stream("GET", url) as response:
                        for chunk in response.iter_bytes(chunk_size=65536):
                            if stop_event.is_set() or time.time() - start_time >= duration:
                                break
            except Exception:
                pass


def _generate_upload_load(duration: int, stop_event: threading.Event):
    """Generate upload traffic to create network load."""
    # Create a chunk of data to upload
    data = b"0" * (1024 * 1024)  # 1MB
    
    start_time = time.time()
    while time.time() - start_time < duration and not stop_event.is_set():
        try:
            with httpx.Client(timeout=30) as client:
                # httpbin.org accepts POST data
                client.post("https://httpbin.org/post", content=data)
        except Exception:
            pass
        
        if time.time() - start_time >= duration:
            break


def _calculate_grade(bloat_increase_ms: float) -> str:
    """
    Calculate bufferbloat grade based on latency increase.
    
    Grading (based on DSLReports methodology):
    A: < 5ms increase
    B: 5-30ms increase
    C: 30-60ms increase
    D: 60-200ms increase
    F: > 200ms increase
    """
    if bloat_increase_ms < 5:
        return "A"
    elif bloat_increase_ms < 30:
        return "B"
    elif bloat_increase_ms < 60:
        return "C"
    elif bloat_increase_ms < 200:
        return "D"
    else:
        return "F"


def test_bufferbloat(
    host: str = "1.1.1.1",
    baseline_duration: int = 15,
    load_duration: int = 30,
    include_upload: bool = True,
) -> BufferbloatResult:
    """
    Test for bufferbloat by measuring latency under network load.
    
    This test:
    1. Measures baseline latency (idle connection)
    2. Generates download/upload load
    3. Measures latency while under load
    4. Compares to detect bufferbloat
    
    Args:
        host: Target host for latency measurement
        baseline_duration: Duration of baseline measurement in seconds
        load_duration: Duration of loaded measurement in seconds
        include_upload: Whether to include upload in load generation
        
    Returns:
        BufferbloatResult with analysis
    """
    # Phase 1: Baseline measurement
    baseline_latencies = _measure_latency_series(host, baseline_duration)
    
    if len(baseline_latencies) < 5:
        return BufferbloatResult(
            host=host,
            duration_seconds=baseline_duration + load_duration,
            baseline_avg_ms=0, baseline_p50_ms=0, baseline_p95_ms=0, baseline_p99_ms=0,
            baseline_samples=len(baseline_latencies),
            loaded_avg_ms=0, loaded_p50_ms=0, loaded_p95_ms=0, loaded_p99_ms=0,
            loaded_samples=0, loaded_max_ms=0,
            bloat_increase_ms=0, bloat_factor=0, grade="?",
            success=False,
            error="Insufficient baseline samples",
        )
    
    # Calculate baseline stats
    baseline_avg = statistics.mean(baseline_latencies)
    baseline_p50 = _percentile(baseline_latencies, 50)
    baseline_p95 = _percentile(baseline_latencies, 95)
    baseline_p99 = _percentile(baseline_latencies, 99)
    
    # Phase 2: Measurement under load
    stop_event = threading.Event()
    
    # Start load generators
    download_thread = threading.Thread(
        target=_generate_download_load,
        args=(load_duration, stop_event),
        daemon=True,
    )
    download_thread.start()
    
    upload_thread = None
    if include_upload:
        upload_thread = threading.Thread(
            target=_generate_upload_load,
            args=(load_duration, stop_event),
            daemon=True,
        )
        upload_thread.start()
    
    # Measure latency while under load
    time.sleep(2)  # Let traffic ramp up
    loaded_latencies = _measure_latency_series(host, load_duration - 4)
    
    # Stop load generators
    stop_event.set()
    download_thread.join(timeout=5)
    if upload_thread:
        upload_thread.join(timeout=5)
    
    if len(loaded_latencies) < 5:
        return BufferbloatResult(
            host=host,
            duration_seconds=baseline_duration + load_duration,
            baseline_avg_ms=round(baseline_avg, 2),
            baseline_p50_ms=round(baseline_p50, 2),
            baseline_p95_ms=round(baseline_p95, 2),
            baseline_p99_ms=round(baseline_p99, 2),
            baseline_samples=len(baseline_latencies),
            loaded_avg_ms=0, loaded_p50_ms=0, loaded_p95_ms=0, loaded_p99_ms=0,
            loaded_samples=len(loaded_latencies), loaded_max_ms=0,
            bloat_increase_ms=0, bloat_factor=0, grade="?",
            success=False,
            error="Insufficient loaded samples",
        )
    
    # Calculate loaded stats
    loaded_avg = statistics.mean(loaded_latencies)
    loaded_p50 = _percentile(loaded_latencies, 50)
    loaded_p95 = _percentile(loaded_latencies, 95)
    loaded_p99 = _percentile(loaded_latencies, 99)
    loaded_max = max(loaded_latencies)
    
    # Calculate bloat metrics
    bloat_increase = loaded_p95 - baseline_p95
    bloat_factor = loaded_p95 / baseline_p95 if baseline_p95 > 0 else 0
    grade = _calculate_grade(bloat_increase)
    
    return BufferbloatResult(
        host=host,
        duration_seconds=baseline_duration + load_duration,
        baseline_avg_ms=round(baseline_avg, 2),
        baseline_p50_ms=round(baseline_p50, 2),
        baseline_p95_ms=round(baseline_p95, 2),
        baseline_p99_ms=round(baseline_p99, 2),
        baseline_samples=len(baseline_latencies),
        loaded_avg_ms=round(loaded_avg, 2),
        loaded_p50_ms=round(loaded_p50, 2),
        loaded_p95_ms=round(loaded_p95, 2),
        loaded_p99_ms=round(loaded_p99, 2),
        loaded_samples=len(loaded_latencies),
        loaded_max_ms=round(loaded_max, 2),
        bloat_increase_ms=round(bloat_increase, 2),
        bloat_factor=round(bloat_factor, 2),
        grade=grade,
        success=True,
    )

