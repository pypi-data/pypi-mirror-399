"""Basic connectivity testing module for netspecs."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Optional

from netspecs.utils.platform import get_ping_command, run_command


@dataclass
class ConnectivityResult:
    """Result of a connectivity check."""
    
    host: str
    reachable: bool
    response_time_ms: Optional[float] = None
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert result to dictionary."""
        return {
            "host": self.host,
            "reachable": self.reachable,
            "response_time_ms": self.response_time_ms,
            "error": self.error,
        }


def check_connectivity(
    host: str,
    timeout: int = 2,
) -> ConnectivityResult:
    """
    Check basic connectivity to a host with a single ping.
    
    Args:
        host: Target host to check
        timeout: Timeout in seconds
        
    Returns:
        ConnectivityResult indicating if host is reachable
    """
    cmd = get_ping_command(host, count=1, timeout=timeout)
    
    try:
        result = run_command(cmd, timeout=timeout + 5)
        
        # Check if ping succeeded (return code 0)
        if result.returncode == 0:
            # Try to extract response time
            import re
            output = result.stdout + result.stderr
            
            # Try Windows format: time=XXms
            match = re.search(r"time[=<](\d+)ms", output)
            if match:
                response_time = float(match.group(1))
            else:
                # Try Unix format: time=XX.XX ms
                match = re.search(r"time=([\d.]+)\s*ms", output)
                response_time = float(match.group(1)) if match else None
            
            return ConnectivityResult(
                host=host,
                reachable=True,
                response_time_ms=response_time,
            )
        else:
            return ConnectivityResult(
                host=host,
                reachable=False,
                error="Host unreachable",
            )
            
    except subprocess.TimeoutExpired:
        return ConnectivityResult(
            host=host,
            reachable=False,
            error="Connection timeout",
        )
    except Exception as e:
        return ConnectivityResult(
            host=host,
            reachable=False,
            error=str(e),
        )


def check_connectivity_batch(
    hosts: list[str],
    timeout: int = 2,
) -> list[ConnectivityResult]:
    """
    Check connectivity to multiple hosts.
    
    Args:
        hosts: List of target hosts to check
        timeout: Timeout in seconds per host
        
    Returns:
        List of ConnectivityResult objects
    """
    results = []
    for host in hosts:
        result = check_connectivity(host, timeout)
        results.append(result)
    return results


def get_connectivity_summary(results: list[ConnectivityResult]) -> dict:
    """
    Get summary statistics for connectivity results.
    
    Args:
        results: List of ConnectivityResult objects
        
    Returns:
        Dictionary with summary statistics
    """
    total = len(results)
    reachable = sum(1 for r in results if r.reachable)
    unreachable = total - reachable
    
    response_times = [
        r.response_time_ms for r in results
        if r.reachable and r.response_time_ms is not None
    ]
    
    return {
        "total_hosts": total,
        "reachable": reachable,
        "unreachable": unreachable,
        "success_rate": (reachable / total * 100) if total > 0 else 0,
        "avg_response_ms": (
            sum(response_times) / len(response_times)
            if response_times else None
        ),
    }

