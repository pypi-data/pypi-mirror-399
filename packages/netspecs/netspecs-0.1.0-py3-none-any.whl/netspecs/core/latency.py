"""Latency testing module for netspecs."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Optional

from netspecs.utils.platform import (
    get_ping_command,
    parse_ping_output,
    run_command,
)


@dataclass
class LatencyResult:
    """Result of a latency test."""
    
    host: str
    packets_sent: int
    packets_received: int
    packet_loss_percent: float
    min_ms: float
    avg_ms: float
    max_ms: float
    jitter_ms: float
    success: bool
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert result to dictionary."""
        return {
            "host": self.host,
            "packets_sent": self.packets_sent,
            "packets_received": self.packets_received,
            "packet_loss_percent": self.packet_loss_percent,
            "min_ms": self.min_ms,
            "avg_ms": self.avg_ms,
            "max_ms": self.max_ms,
            "jitter_ms": self.jitter_ms,
            "success": self.success,
            "error": self.error,
        }
    
    @property
    def status(self) -> str:
        """Get status indicator based on results."""
        if not self.success or self.packet_loss_percent >= 100:
            return "error"
        elif self.packet_loss_percent > 5:
            return "warning"
        elif self.avg_ms > 100:
            return "warning"
        else:
            return "ok"


def test_latency(
    host: str,
    count: int = 20,
    timeout: int = 2,
) -> LatencyResult:
    """
    Test latency to a host using ping.
    
    Args:
        host: Target host to ping
        count: Number of ping packets to send
        timeout: Timeout in seconds for each ping
        
    Returns:
        LatencyResult with ping statistics
    """
    cmd = get_ping_command(host, count, timeout)
    
    try:
        result = run_command(cmd, timeout=count * timeout + 10)
        output = result.stdout + result.stderr
        
        stats = parse_ping_output(output, count)
        
        if stats:
            return LatencyResult(
                host=host,
                packets_sent=stats.packets_sent,
                packets_received=stats.packets_received,
                packet_loss_percent=stats.packet_loss_percent,
                min_ms=stats.min_ms,
                avg_ms=stats.avg_ms,
                max_ms=stats.max_ms,
                jitter_ms=stats.jitter_ms,
                success=stats.packets_received > 0,
            )
        else:
            return LatencyResult(
                host=host,
                packets_sent=count,
                packets_received=0,
                packet_loss_percent=100.0,
                min_ms=0.0,
                avg_ms=0.0,
                max_ms=0.0,
                jitter_ms=0.0,
                success=False,
                error="Failed to parse ping output",
            )
            
    except subprocess.TimeoutExpired:
        return LatencyResult(
            host=host,
            packets_sent=count,
            packets_received=0,
            packet_loss_percent=100.0,
            min_ms=0.0,
            avg_ms=0.0,
            max_ms=0.0,
            jitter_ms=0.0,
            success=False,
            error="Ping timeout",
        )
    except Exception as e:
        return LatencyResult(
            host=host,
            packets_sent=count,
            packets_received=0,
            packet_loss_percent=100.0,
            min_ms=0.0,
            avg_ms=0.0,
            max_ms=0.0,
            jitter_ms=0.0,
            success=False,
            error=str(e),
        )


def test_latency_batch(
    hosts: list[str],
    count: int = 20,
    timeout: int = 2,
) -> list[LatencyResult]:
    """
    Test latency to multiple hosts.
    
    Args:
        hosts: List of target hosts to ping
        count: Number of ping packets to send per host
        timeout: Timeout in seconds for each ping
        
    Returns:
        List of LatencyResult objects
    """
    results = []
    for host in hosts:
        result = test_latency(host, count, timeout)
        results.append(result)
    return results

