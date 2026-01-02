"""Long-duration monitoring module for netspecs."""

from __future__ import annotations

import csv
import re
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from netspecs.utils.platform import get_ping_command, get_system, run_command


def _percentile(data: list[float], p: int) -> float:
    """Calculate percentile of a list."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * p / 100
    f = int(k)
    c = f + 1 if f + 1 < len(sorted_data) else f
    return sorted_data[f] + (sorted_data[c] - sorted_data[f]) * (k - f)


@dataclass
class MonitoringSample:
    """A single monitoring sample."""
    
    timestamp: datetime
    host: str
    latency_ms: Optional[float]
    success: bool
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "host": self.host,
            "latency_ms": self.latency_ms,
            "success": self.success,
        }


@dataclass
class MonitoringInterval:
    """Statistics for a monitoring interval (e.g., 1 minute)."""
    
    start_time: datetime
    end_time: datetime
    host: str
    samples: int
    successes: int
    failures: int
    
    avg_ms: float
    min_ms: float
    max_ms: float
    p50_ms: float
    p95_ms: float
    p99_ms: float
    jitter_ms: float
    loss_percent: float
    
    def to_dict(self) -> dict:
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "host": self.host,
            "samples": self.samples,
            "successes": self.successes,
            "failures": self.failures,
            "avg_ms": self.avg_ms,
            "min_ms": self.min_ms,
            "max_ms": self.max_ms,
            "p50_ms": self.p50_ms,
            "p95_ms": self.p95_ms,
            "p99_ms": self.p99_ms,
            "jitter_ms": self.jitter_ms,
            "loss_percent": self.loss_percent,
        }


@dataclass
class MonitoringResult:
    """Result of a long-duration monitoring session."""
    
    host: str
    total_duration_seconds: int
    interval_seconds: int
    
    # Overall statistics
    total_samples: int
    total_successes: int
    total_failures: int
    overall_loss_percent: float
    
    overall_avg_ms: float
    overall_min_ms: float
    overall_max_ms: float
    overall_p50_ms: float
    overall_p95_ms: float
    overall_p99_ms: float
    overall_jitter_ms: float
    
    # Interval data
    intervals: list[MonitoringInterval] = field(default_factory=list)
    
    # Worst spikes
    worst_latencies: list[float] = field(default_factory=list)
    spike_count: int = 0  # Number of samples > 2x median
    
    success: bool = True
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "host": self.host,
            "total_duration_seconds": self.total_duration_seconds,
            "interval_seconds": self.interval_seconds,
            "total_samples": self.total_samples,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "overall_loss_percent": self.overall_loss_percent,
            "overall_avg_ms": self.overall_avg_ms,
            "overall_min_ms": self.overall_min_ms,
            "overall_max_ms": self.overall_max_ms,
            "overall_p50_ms": self.overall_p50_ms,
            "overall_p95_ms": self.overall_p95_ms,
            "overall_p99_ms": self.overall_p99_ms,
            "overall_jitter_ms": self.overall_jitter_ms,
            "intervals": [i.to_dict() for i in self.intervals],
            "worst_latencies": self.worst_latencies,
            "spike_count": self.spike_count,
            "success": self.success,
            "error": self.error,
        }


def _extract_latency(output: str) -> Optional[float]:
    """Extract latency from ping output."""
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


def _calculate_interval_stats(
    samples: list[MonitoringSample],
    host: str,
    start_time: datetime,
    end_time: datetime,
) -> MonitoringInterval:
    """Calculate statistics for an interval."""
    successes = [s for s in samples if s.success and s.latency_ms is not None]
    failures = [s for s in samples if not s.success]
    latencies = [s.latency_ms for s in successes]
    
    if not latencies:
        return MonitoringInterval(
            start_time=start_time,
            end_time=end_time,
            host=host,
            samples=len(samples),
            successes=len(successes),
            failures=len(failures),
            avg_ms=0, min_ms=0, max_ms=0,
            p50_ms=0, p95_ms=0, p99_ms=0,
            jitter_ms=0,
            loss_percent=100.0 if samples else 0,
        )
    
    avg_ms = statistics.mean(latencies)
    jitter_ms = statistics.stdev(latencies) if len(latencies) > 1 else 0
    loss_percent = (len(failures) / len(samples) * 100) if samples else 0
    
    return MonitoringInterval(
        start_time=start_time,
        end_time=end_time,
        host=host,
        samples=len(samples),
        successes=len(successes),
        failures=len(failures),
        avg_ms=round(avg_ms, 2),
        min_ms=round(min(latencies), 2),
        max_ms=round(max(latencies), 2),
        p50_ms=round(_percentile(latencies, 50), 2),
        p95_ms=round(_percentile(latencies, 95), 2),
        p99_ms=round(_percentile(latencies, 99), 2),
        jitter_ms=round(jitter_ms, 2),
        loss_percent=round(loss_percent, 2),
    )


def long_monitor(
    host: str = "1.1.1.1",
    duration_minutes: int = 60,
    ping_interval: float = 1.0,
    stats_interval_seconds: int = 60,
    output_csv: Optional[Path] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> MonitoringResult:
    """
    Run long-duration monitoring with periodic statistics.
    
    Args:
        host: Target host to monitor
        duration_minutes: Total monitoring duration in minutes
        ping_interval: Seconds between pings
        stats_interval_seconds: Interval for calculating stats (default 1 minute)
        output_csv: Optional path to save raw samples as CSV
        progress_callback: Optional callback(elapsed_seconds, total_seconds)
        
    Returns:
        MonitoringResult with detailed statistics
    """
    total_duration = duration_minutes * 60
    all_samples: list[MonitoringSample] = []
    all_latencies: list[float] = []
    intervals: list[MonitoringInterval] = []
    
    interval_samples: list[MonitoringSample] = []
    interval_start = datetime.now()
    
    # CSV writer setup
    csv_file = None
    csv_writer = None
    if output_csv:
        csv_file = open(output_csv, "w", newline="")
        csv_writer = csv.DictWriter(
            csv_file,
            fieldnames=["timestamp", "host", "latency_ms", "success"],
        )
        csv_writer.writeheader()
    
    try:
        start_time = time.time()
        last_interval_time = start_time
        
        while time.time() - start_time < total_duration:
            # Take a sample
            timestamp = datetime.now()
            try:
                cmd = get_ping_command(host, count=1, timeout=2)
                result = run_command(cmd, timeout=5)
                output = result.stdout + result.stderr
                latency = _extract_latency(output)
                
                sample = MonitoringSample(
                    timestamp=timestamp,
                    host=host,
                    latency_ms=latency,
                    success=latency is not None,
                )
            except Exception:
                sample = MonitoringSample(
                    timestamp=timestamp,
                    host=host,
                    latency_ms=None,
                    success=False,
                )
            
            all_samples.append(sample)
            interval_samples.append(sample)
            
            if sample.latency_ms is not None:
                all_latencies.append(sample.latency_ms)
            
            # Write to CSV if enabled
            if csv_writer:
                csv_writer.writerow(sample.to_dict())
                csv_file.flush()
            
            # Check if interval complete
            if time.time() - last_interval_time >= stats_interval_seconds:
                interval = _calculate_interval_stats(
                    interval_samples,
                    host,
                    interval_start,
                    datetime.now(),
                )
                intervals.append(interval)
                interval_samples = []
                interval_start = datetime.now()
                last_interval_time = time.time()
            
            # Progress callback
            if progress_callback:
                elapsed = int(time.time() - start_time)
                progress_callback(elapsed, total_duration)
            
            time.sleep(ping_interval)
        
        # Final interval
        if interval_samples:
            interval = _calculate_interval_stats(
                interval_samples,
                host,
                interval_start,
                datetime.now(),
            )
            intervals.append(interval)
    
    finally:
        if csv_file:
            csv_file.close()
    
    # Calculate overall statistics
    if not all_latencies:
        return MonitoringResult(
            host=host,
            total_duration_seconds=total_duration,
            interval_seconds=stats_interval_seconds,
            total_samples=len(all_samples),
            total_successes=0,
            total_failures=len(all_samples),
            overall_loss_percent=100.0,
            overall_avg_ms=0, overall_min_ms=0, overall_max_ms=0,
            overall_p50_ms=0, overall_p95_ms=0, overall_p99_ms=0,
            overall_jitter_ms=0,
            intervals=intervals,
            success=False,
            error="No successful samples",
        )
    
    # Calculate spike count (samples > 2x median)
    median = _percentile(all_latencies, 50)
    spike_threshold = median * 2
    spikes = [l for l in all_latencies if l > spike_threshold]
    
    # Get worst 10 latencies
    worst = sorted(all_latencies, reverse=True)[:10]
    
    successes = sum(1 for s in all_samples if s.success)
    failures = len(all_samples) - successes
    
    return MonitoringResult(
        host=host,
        total_duration_seconds=total_duration,
        interval_seconds=stats_interval_seconds,
        total_samples=len(all_samples),
        total_successes=successes,
        total_failures=failures,
        overall_loss_percent=round(failures / len(all_samples) * 100, 2),
        overall_avg_ms=round(statistics.mean(all_latencies), 2),
        overall_min_ms=round(min(all_latencies), 2),
        overall_max_ms=round(max(all_latencies), 2),
        overall_p50_ms=round(_percentile(all_latencies, 50), 2),
        overall_p95_ms=round(_percentile(all_latencies, 95), 2),
        overall_p99_ms=round(_percentile(all_latencies, 99), 2),
        overall_jitter_ms=round(statistics.stdev(all_latencies), 2) if len(all_latencies) > 1 else 0,
        intervals=intervals,
        worst_latencies=worst,
        spike_count=len(spikes),
        success=True,
    )

