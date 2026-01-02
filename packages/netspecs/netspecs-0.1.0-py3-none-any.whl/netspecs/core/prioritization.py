"""Prioritization/throttling detection module for netspecs."""

from __future__ import annotations

import asyncio
import re
import statistics
import time
from dataclasses import dataclass, field
from typing import Optional

import httpx

from netspecs.utils.platform import get_ping_command, get_system, run_command


@dataclass
class PhaseResult:
    """Result of a single test phase."""
    
    name: str
    avg_ms: float
    min_ms: float
    max_ms: float
    jitter_ms: float
    samples: int
    latencies: list[float] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert result to dictionary."""
        return {
            "name": self.name,
            "avg_ms": self.avg_ms,
            "min_ms": self.min_ms,
            "max_ms": self.max_ms,
            "jitter_ms": self.jitter_ms,
            "samples": self.samples,
        }


@dataclass
class PrioritizationResult:
    """Result of prioritization detection test."""
    
    host: str
    phases: list[PhaseResult]
    baseline_avg_ms: float
    light_traffic_change_ms: Optional[float] = None
    medium_traffic_change_ms: Optional[float] = None
    heavy_traffic_change_ms: Optional[float] = None
    throttling_detected: bool = False
    throttling_severity: str = "none"  # none, mild, moderate, severe
    success: bool = True
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert result to dictionary."""
        return {
            "host": self.host,
            "phases": [p.to_dict() for p in self.phases],
            "baseline_avg_ms": self.baseline_avg_ms,
            "light_traffic_change_ms": self.light_traffic_change_ms,
            "medium_traffic_change_ms": self.medium_traffic_change_ms,
            "heavy_traffic_change_ms": self.heavy_traffic_change_ms,
            "throttling_detected": self.throttling_detected,
            "throttling_severity": self.throttling_severity,
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


def _measure_phase_latency(
    host: str,
    duration: int,
    interval: int = 1,
) -> list[float]:
    """Measure latency during a test phase."""
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
        
        time.sleep(interval)
    
    return latencies


def _generate_background_traffic(
    duration: int,
    intensity: str = "medium",
) -> None:
    """
    Generate background HTTP traffic to simulate network load.
    
    Args:
        duration: Duration in seconds
        intensity: Traffic intensity (low, medium, high)
    """
    urls = [
        "https://www.google.com",
        "https://www.cloudflare.com",
        "https://www.github.com",
        "https://www.microsoft.com",
        "https://www.amazon.com",
    ]
    
    interval_map = {"low": 5, "medium": 3, "high": 1}
    url_count_map = {"low": 2, "medium": 3, "high": 5}
    
    interval = interval_map.get(intensity, 3)
    url_count = url_count_map.get(intensity, 3)
    
    start_time = time.time()
    end_time = start_time + duration
    
    with httpx.Client(timeout=10, follow_redirects=True) as client:
        while time.time() < end_time:
            for url in urls[:url_count]:
                try:
                    client.get(url)
                except Exception:
                    pass
            time.sleep(interval)


def _run_phase(
    name: str,
    host: str,
    duration: int,
    traffic_intensity: Optional[str] = None,
) -> PhaseResult:
    """Run a single test phase with optional background traffic."""
    import threading
    
    # Start background traffic if specified
    traffic_thread = None
    if traffic_intensity:
        traffic_thread = threading.Thread(
            target=_generate_background_traffic,
            args=(duration, traffic_intensity),
            daemon=True,
        )
        traffic_thread.start()
    
    # Measure latency during the phase
    latencies = _measure_phase_latency(host, duration)
    
    # Wait for traffic thread to complete
    if traffic_thread:
        traffic_thread.join(timeout=5)
    
    if not latencies:
        return PhaseResult(
            name=name,
            avg_ms=0.0,
            min_ms=0.0,
            max_ms=0.0,
            jitter_ms=0.0,
            samples=0,
            latencies=[],
        )
    
    avg_ms = statistics.mean(latencies)
    min_ms = min(latencies)
    max_ms = max(latencies)
    jitter_ms = statistics.stdev(latencies) if len(latencies) > 1 else 0.0
    
    return PhaseResult(
        name=name,
        avg_ms=round(avg_ms, 2),
        min_ms=round(min_ms, 2),
        max_ms=round(max_ms, 2),
        jitter_ms=round(jitter_ms, 2),
        samples=len(latencies),
        latencies=latencies,
    )


def detect_prioritization(
    host: str = "8.8.8.8",
    phase_duration: int = 60,
) -> PrioritizationResult:
    """
    Detect connection prioritization/throttling.
    
    Runs 5 phases:
    1. Baseline (idle connection)
    2. Light background traffic
    3. Medium background traffic
    4. Heavy background traffic
    5. Return to baseline
    
    Args:
        host: Target host to test against
        phase_duration: Duration of each phase in seconds
        
    Returns:
        PrioritizationResult with analysis
    """
    phases = []
    
    # Phase 1: Baseline
    baseline = _run_phase("baseline", host, phase_duration)
    phases.append(baseline)
    time.sleep(5)
    
    # Phase 2: Light traffic
    light = _run_phase("light_traffic", host, phase_duration, "low")
    phases.append(light)
    time.sleep(5)
    
    # Phase 3: Medium traffic
    medium = _run_phase("medium_traffic", host, phase_duration, "medium")
    phases.append(medium)
    time.sleep(5)
    
    # Phase 4: Heavy traffic
    heavy = _run_phase("heavy_traffic", host, phase_duration, "high")
    phases.append(heavy)
    time.sleep(5)
    
    # Phase 5: Return to baseline
    baseline2 = _run_phase("baseline_return", host, phase_duration)
    phases.append(baseline2)
    
    # Analyze results
    baseline_avg = baseline.avg_ms if baseline.samples > 0 else 0.0
    
    light_change = (light.avg_ms - baseline_avg) if light.samples > 0 else None
    medium_change = (medium.avg_ms - baseline_avg) if medium.samples > 0 else None
    heavy_change = (heavy.avg_ms - baseline_avg) if heavy.samples > 0 else None
    
    # Determine throttling severity
    throttling_detected = False
    severity = "none"
    
    if heavy_change is not None:
        if heavy_change > 100:
            throttling_detected = True
            severity = "severe"
        elif heavy_change > 50:
            throttling_detected = True
            severity = "moderate"
        elif heavy_change > 20:
            throttling_detected = True
            severity = "mild"
    
    return PrioritizationResult(
        host=host,
        phases=phases,
        baseline_avg_ms=round(baseline_avg, 2),
        light_traffic_change_ms=round(light_change, 2) if light_change else None,
        medium_traffic_change_ms=round(medium_change, 2) if medium_change else None,
        heavy_traffic_change_ms=round(heavy_change, 2) if heavy_change else None,
        throttling_detected=throttling_detected,
        throttling_severity=severity,
        success=baseline.samples > 0,
    )

