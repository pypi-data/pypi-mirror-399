"""Cross-platform utilities for netspecs."""

from __future__ import annotations

import platform
import re
import subprocess
from dataclasses import dataclass
from typing import Optional


def get_system() -> str:
    """Get the current operating system name."""
    return platform.system()


def get_system_info() -> dict:
    """Get system information for diagnostic reports."""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
    }


def get_ping_command(host: str, count: int, timeout: int = 2) -> list[str]:
    """
    Get the appropriate ping command for the current platform.
    
    Args:
        host: Target host to ping
        count: Number of ping packets to send
        timeout: Timeout in seconds for each ping
        
    Returns:
        List of command arguments for subprocess
    """
    system = get_system()
    
    if system == "Windows":
        # Windows: -n for count, -w for timeout in milliseconds
        return ["ping", "-n", str(count), "-w", str(timeout * 1000), host]
    else:
        # Linux/macOS: -c for count, -W for timeout in seconds
        return ["ping", "-c", str(count), "-W", str(timeout), host]


@dataclass
class PingStats:
    """Parsed ping statistics."""
    packets_sent: int
    packets_received: int
    packet_loss_percent: float
    min_ms: float
    avg_ms: float
    max_ms: float
    jitter_ms: float


def parse_ping_output(output: str, count: int) -> Optional[PingStats]:
    """
    Parse ping command output across platforms.
    
    Args:
        output: Raw output from ping command
        count: Number of packets that were sent
        
    Returns:
        PingStats object or None if parsing failed
    """
    system = get_system()
    
    try:
        if system == "Windows":
            return _parse_windows_ping(output, count)
        else:
            return _parse_unix_ping(output, count)
    except Exception:
        return None


def _parse_windows_ping(output: str, count: int) -> Optional[PingStats]:
    """Parse Windows ping output."""
    # Extract packet statistics
    # "Packets: Sent = 10, Received = 10, Lost = 0 (0% loss)"
    packet_match = re.search(
        r"Sent = (\d+), Received = (\d+), Lost = (\d+)",
        output
    )
    
    if not packet_match:
        return None
    
    sent = int(packet_match.group(1))
    received = int(packet_match.group(2))
    lost = int(packet_match.group(3))
    loss_percent = (lost / sent * 100) if sent > 0 else 100.0
    
    # Extract timing statistics
    # "Minimum = 10ms, Maximum = 15ms, Average = 12ms"
    timing_match = re.search(
        r"Minimum = (\d+)ms, Maximum = (\d+)ms, Average = (\d+)ms",
        output
    )
    
    if timing_match:
        min_ms = float(timing_match.group(1))
        max_ms = float(timing_match.group(2))
        avg_ms = float(timing_match.group(3))
        jitter_ms = max_ms - min_ms
    else:
        min_ms = avg_ms = max_ms = jitter_ms = 0.0
    
    return PingStats(
        packets_sent=sent,
        packets_received=received,
        packet_loss_percent=loss_percent,
        min_ms=min_ms,
        avg_ms=avg_ms,
        max_ms=max_ms,
        jitter_ms=jitter_ms,
    )


def _parse_unix_ping(output: str, count: int) -> Optional[PingStats]:
    """Parse Linux/macOS ping output."""
    # Extract packet statistics
    # "10 packets transmitted, 10 received, 0% packet loss"
    packet_match = re.search(
        r"(\d+) packets transmitted, (\d+) (?:packets )?received",
        output
    )
    
    if not packet_match:
        return None
    
    sent = int(packet_match.group(1))
    received = int(packet_match.group(2))
    lost = sent - received
    loss_percent = (lost / sent * 100) if sent > 0 else 100.0
    
    # Extract timing statistics
    # "rtt min/avg/max/mdev = 10.123/12.456/15.789/1.234 ms"
    # or "round-trip min/avg/max/stddev = 10.123/12.456/15.789/1.234 ms"
    timing_match = re.search(
        r"(?:rtt|round-trip) min/avg/max/(?:mdev|stddev) = "
        r"([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+) ms",
        output
    )
    
    if timing_match:
        min_ms = float(timing_match.group(1))
        avg_ms = float(timing_match.group(2))
        max_ms = float(timing_match.group(3))
        jitter_ms = float(timing_match.group(4))
    else:
        min_ms = avg_ms = max_ms = jitter_ms = 0.0
    
    return PingStats(
        packets_sent=sent,
        packets_received=received,
        packet_loss_percent=loss_percent,
        min_ms=min_ms,
        avg_ms=avg_ms,
        max_ms=max_ms,
        jitter_ms=jitter_ms,
    )


def run_command(
    cmd: list[str],
    timeout: Optional[int] = None,
    capture_output: bool = True,
) -> subprocess.CompletedProcess:
    """
    Run a command with cross-platform compatibility.
    
    Args:
        cmd: Command and arguments as a list
        timeout: Timeout in seconds
        capture_output: Whether to capture stdout/stderr
        
    Returns:
        CompletedProcess instance
    """
    return subprocess.run(
        cmd,
        capture_output=capture_output,
        text=True,
        timeout=timeout,
    )

