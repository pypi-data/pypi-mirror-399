"""Speed testing module for netspecs."""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from dataclasses import dataclass
from typing import Optional

import httpx

from netspecs.utils.platform import run_command


# Test file URLs for HTTP speed tests
SPEED_TEST_URLS = [
    {"url": "http://speedtest.tele2.net/10MB.zip", "size_mb": 10, "name": "Tele2 (10MB)"},
    {"url": "http://speedtest.tele2.net/100MB.zip", "size_mb": 100, "name": "Tele2 (100MB)"},
    {"url": "http://ipv4.download.thinkbroadband.com/10MB.zip", "size_mb": 10, "name": "ThinkBroadband (10MB)"},
]


@dataclass
class SpeedResult:
    """Result of a speed test."""
    
    # HTTP test results
    http_download_mbps: Optional[float] = None
    http_upload_mbps: Optional[float] = None
    http_tests: list[dict] = None
    
    # Ookla results (if available)
    ookla_download_mbps: Optional[float] = None
    ookla_upload_mbps: Optional[float] = None
    ookla_ping_ms: Optional[float] = None
    ookla_jitter_ms: Optional[float] = None
    ookla_server: Optional[str] = None
    ookla_available: bool = False
    
    # Comparison
    speed_difference_percent: Optional[float] = None
    
    success: bool = True
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.http_tests is None:
            self.http_tests = []
    
    def to_dict(self) -> dict:
        """Convert result to dictionary."""
        return {
            "http_download_mbps": self.http_download_mbps,
            "http_upload_mbps": self.http_upload_mbps,
            "http_tests": self.http_tests,
            "ookla_download_mbps": self.ookla_download_mbps,
            "ookla_upload_mbps": self.ookla_upload_mbps,
            "ookla_ping_ms": self.ookla_ping_ms,
            "ookla_jitter_ms": self.ookla_jitter_ms,
            "ookla_server": self.ookla_server,
            "ookla_available": self.ookla_available,
            "speed_difference_percent": self.speed_difference_percent,
            "success": self.success,
            "error": self.error,
        }


def _test_http_download(url: str, size_mb: int, timeout: int = 60) -> Optional[float]:
    """
    Test download speed using HTTP.
    
    Args:
        url: URL to download
        size_mb: Expected file size in MB
        timeout: Timeout in seconds
        
    Returns:
        Speed in Mbps or None if failed
    """
    try:
        start_time = time.time()
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(url)
            response.read()  # Ensure full download
        end_time = time.time()
        
        duration = end_time - start_time
        if duration > 0:
            speed_mbps = (size_mb * 8) / duration
            return round(speed_mbps, 2)
    except Exception:
        pass
    
    return None


def _test_ookla_speedtest() -> Optional[dict]:
    """
    Run Ookla Speedtest CLI if available.
    
    Returns:
        Dictionary with Ookla results or None if not available
    """
    # Check if speedtest CLI is available
    speedtest_cmd = shutil.which("speedtest")
    if not speedtest_cmd:
        return None
    
    try:
        result = run_command(
            [speedtest_cmd, "--format=json", "--accept-license", "--accept-gdpr"],
            timeout=120,
        )
        
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            
            # Convert bytes/sec to Mbps
            download_mbps = round(data.get("download", {}).get("bandwidth", 0) / 125000, 2)
            upload_mbps = round(data.get("upload", {}).get("bandwidth", 0) / 125000, 2)
            ping_ms = round(data.get("ping", {}).get("latency", 0), 2)
            jitter_ms = round(data.get("ping", {}).get("jitter", 0), 2)
            
            server = data.get("server", {})
            server_name = f"{server.get('name', 'Unknown')} ({server.get('location', 'Unknown')}, {server.get('country', 'Unknown')})"
            
            return {
                "download_mbps": download_mbps,
                "upload_mbps": upload_mbps,
                "ping_ms": ping_ms,
                "jitter_ms": jitter_ms,
                "server": server_name,
            }
    except Exception:
        pass
    
    return None


def test_speed(
    include_ookla: bool = True,
    http_tests: Optional[list[dict]] = None,
) -> SpeedResult:
    """
    Run comprehensive speed tests.
    
    Args:
        include_ookla: Whether to run Ookla Speedtest CLI if available
        http_tests: Custom list of HTTP test URLs (uses defaults if None)
        
    Returns:
        SpeedResult with all test results
    """
    test_urls = http_tests or SPEED_TEST_URLS
    
    result = SpeedResult()
    http_results = []
    
    # Run HTTP download tests
    for test in test_urls:
        speed = _test_http_download(test["url"], test["size_mb"])
        test_result = {
            "name": test["name"],
            "size_mb": test["size_mb"],
            "speed_mbps": speed,
            "success": speed is not None,
        }
        http_results.append(test_result)
    
    result.http_tests = http_results
    
    # Calculate average HTTP speed
    successful_speeds = [t["speed_mbps"] for t in http_results if t["speed_mbps"]]
    if successful_speeds:
        result.http_download_mbps = round(sum(successful_speeds) / len(successful_speeds), 2)
    
    # Run Ookla Speedtest if requested
    if include_ookla:
        ookla_result = _test_ookla_speedtest()
        if ookla_result:
            result.ookla_available = True
            result.ookla_download_mbps = ookla_result["download_mbps"]
            result.ookla_upload_mbps = ookla_result["upload_mbps"]
            result.ookla_ping_ms = ookla_result["ping_ms"]
            result.ookla_jitter_ms = ookla_result["jitter_ms"]
            result.ookla_server = ookla_result["server"]
            
            # Calculate difference between Ookla and HTTP speeds
            if result.http_download_mbps and result.http_download_mbps > 0:
                diff = ((result.ookla_download_mbps - result.http_download_mbps) 
                        / result.http_download_mbps * 100)
                result.speed_difference_percent = round(diff, 2)
    
    result.success = bool(successful_speeds) or result.ookla_available
    
    return result


def test_bandwidth_variability(
    iterations: int = 5,
    test_url: str = "http://speedtest.tele2.net/10MB.zip",
    size_mb: int = 10,
) -> dict:
    """
    Test bandwidth variability over multiple iterations.
    
    Args:
        iterations: Number of test iterations
        test_url: URL to use for testing
        size_mb: Size of the test file in MB
        
    Returns:
        Dictionary with variability statistics
    """
    speeds = []
    
    for i in range(iterations):
        speed = _test_http_download(test_url, size_mb)
        if speed:
            speeds.append(speed)
        time.sleep(2)  # Wait between tests
    
    if not speeds:
        return {
            "iterations": iterations,
            "successful": 0,
            "min_mbps": None,
            "max_mbps": None,
            "avg_mbps": None,
            "variability_percent": None,
        }
    
    min_speed = min(speeds)
    max_speed = max(speeds)
    avg_speed = sum(speeds) / len(speeds)
    variability = ((max_speed - min_speed) / avg_speed * 100) if avg_speed > 0 else 0
    
    return {
        "iterations": iterations,
        "successful": len(speeds),
        "speeds": speeds,
        "min_mbps": round(min_speed, 2),
        "max_mbps": round(max_speed, 2),
        "avg_mbps": round(avg_speed, 2),
        "variability_percent": round(variability, 2),
    }

