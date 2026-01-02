"""Network information capture module."""

from __future__ import annotations

import re
import socket
import subprocess
from dataclasses import dataclass
from typing import Optional

import httpx

from netspecs.utils.platform import get_system, run_command


@dataclass
class NetworkInfo:
    """Captured network information."""
    
    # Public IP info
    public_ip: Optional[str] = None
    isp: Optional[str] = None
    
    # Local network info
    local_ip: Optional[str] = None
    default_gateway: Optional[str] = None
    dns_servers: list[str] = None
    
    # Connection info
    hostname: Optional[str] = None
    interface_type: Optional[str] = None  # wifi, ethernet, cellular
    
    # Traceroute (first few hops)
    traceroute_hops: list[dict] = None
    
    def __post_init__(self):
        if self.dns_servers is None:
            self.dns_servers = []
        if self.traceroute_hops is None:
            self.traceroute_hops = []
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "public_ip": self.public_ip,
            "isp": self.isp,
            "local_ip": self.local_ip,
            "default_gateway": self.default_gateway,
            "dns_servers": self.dns_servers,
            "hostname": self.hostname,
            "interface_type": self.interface_type,
            "traceroute_hops": self.traceroute_hops,
        }


def get_public_ip() -> tuple[Optional[str], Optional[str]]:
    """
    Get public IP address and ISP info.
    
    Returns:
        Tuple of (public_ip, isp_name)
    """
    try:
        with httpx.Client(timeout=10) as client:
            # Use ipinfo.io for IP and ISP info
            response = client.get("https://ipinfo.io/json")
            if response.status_code == 200:
                data = response.json()
                return data.get("ip"), data.get("org")
    except Exception:
        pass
    
    # Fallback to simpler service
    try:
        with httpx.Client(timeout=10) as client:
            response = client.get("https://api.ipify.org")
            if response.status_code == 200:
                return response.text.strip(), None
    except Exception:
        pass
    
    return None, None


def get_local_ip() -> Optional[str]:
    """Get local IP address."""
    try:
        # Create a socket to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return None


def get_default_gateway() -> Optional[str]:
    """Get default gateway IP."""
    system = get_system()
    
    try:
        if system == "Windows":
            result = run_command(["ipconfig"], timeout=10)
            # Look for "Default Gateway"
            for line in result.stdout.split("\n"):
                if "Default Gateway" in line:
                    match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
                    if match:
                        return match.group(1)
        elif system == "Darwin":  # macOS
            result = run_command(["netstat", "-nr"], timeout=10)
            for line in result.stdout.split("\n"):
                if line.startswith("default"):
                    parts = line.split()
                    if len(parts) >= 2:
                        return parts[1]
        else:  # Linux
            result = run_command(["ip", "route"], timeout=10)
            for line in result.stdout.split("\n"):
                if line.startswith("default"):
                    parts = line.split()
                    if len(parts) >= 3:
                        return parts[2]
    except Exception:
        pass
    
    return None


def get_dns_servers() -> list[str]:
    """Get configured DNS servers."""
    system = get_system()
    dns_servers = []
    
    try:
        if system == "Windows":
            result = run_command(["ipconfig", "/all"], timeout=10)
            capture_next = False
            for line in result.stdout.split("\n"):
                if "DNS Servers" in line:
                    match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
                    if match:
                        dns_servers.append(match.group(1))
                    capture_next = True
                elif capture_next and line.strip():
                    match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
                    if match:
                        dns_servers.append(match.group(1))
                    else:
                        capture_next = False
        elif system == "Darwin":  # macOS
            result = run_command(["scutil", "--dns"], timeout=10)
            for line in result.stdout.split("\n"):
                if "nameserver" in line:
                    match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
                    if match and match.group(1) not in dns_servers:
                        dns_servers.append(match.group(1))
        else:  # Linux
            try:
                with open("/etc/resolv.conf") as f:
                    for line in f:
                        if line.startswith("nameserver"):
                            parts = line.split()
                            if len(parts) >= 2:
                                dns_servers.append(parts[1])
            except Exception:
                pass
    except Exception:
        pass
    
    return dns_servers[:4]  # Limit to 4 servers


def detect_interface_type() -> Optional[str]:
    """Detect the type of network interface being used."""
    system = get_system()
    
    try:
        if system == "Darwin":  # macOS
            result = run_command(["networksetup", "-listallhardwareports"], timeout=10)
            # Check which interface is active by looking at default route
            route_result = run_command(["route", "get", "default"], timeout=10)
            interface = None
            for line in route_result.stdout.split("\n"):
                if "interface:" in line:
                    interface = line.split(":")[1].strip()
                    break
            
            if interface:
                if interface.startswith("en0"):
                    return "wifi"
                elif interface.startswith("en"):
                    return "ethernet"
                elif interface.startswith("pdp") or interface.startswith("utun"):
                    return "cellular"
        
        elif system == "Linux":
            # Check for wifi
            result = run_command(["iwconfig"], timeout=10)
            if "ESSID" in result.stdout and "off" not in result.stdout:
                return "wifi"
            return "ethernet"
        
        elif system == "Windows":
            result = run_command(["netsh", "wlan", "show", "interfaces"], timeout=10)
            if "State" in result.stdout and "connected" in result.stdout.lower():
                return "wifi"
            return "ethernet"
    
    except Exception:
        pass
    
    return None


def run_traceroute(host: str, max_hops: int = 5) -> list[dict]:
    """
    Run a limited traceroute to capture first few hops.
    
    Args:
        host: Target host
        max_hops: Maximum number of hops to trace
        
    Returns:
        List of hop dictionaries with hop number, IP, and RTT
    """
    system = get_system()
    hops = []
    
    try:
        if system == "Windows":
            cmd = ["tracert", "-d", "-h", str(max_hops), host]
        else:
            cmd = ["traceroute", "-n", "-m", str(max_hops), "-q", "1", host]
        
        result = run_command(cmd, timeout=30)
        
        for line in result.stdout.split("\n"):
            # Parse hop lines (format varies by OS)
            # Windows: "  1    <1 ms    <1 ms    <1 ms  192.168.1.1"
            # Unix: " 1  192.168.1.1  1.234 ms"
            
            if system == "Windows":
                match = re.match(r"\s*(\d+)\s+.*?(\d+\.\d+\.\d+\.\d+|\*)", line)
            else:
                match = re.match(r"\s*(\d+)\s+(\d+\.\d+\.\d+\.\d+|\*)", line)
            
            if match:
                hop_num = int(match.group(1))
                ip = match.group(2) if match.group(2) != "*" else None
                
                # Try to extract RTT
                rtt_match = re.search(r"([\d.]+)\s*ms", line)
                rtt = float(rtt_match.group(1)) if rtt_match else None
                
                hops.append({
                    "hop": hop_num,
                    "ip": ip,
                    "rtt_ms": rtt,
                })
                
                if hop_num >= max_hops:
                    break
    
    except Exception:
        pass
    
    return hops


def capture_network_info(
    include_traceroute: bool = True,
    traceroute_host: str = "8.8.8.8",
) -> NetworkInfo:
    """
    Capture comprehensive network information.
    
    Args:
        include_traceroute: Whether to run traceroute
        traceroute_host: Host to traceroute to
        
    Returns:
        NetworkInfo with all captured data
    """
    # Get public IP and ISP
    public_ip, isp = get_public_ip()
    
    # Get local network info
    local_ip = get_local_ip()
    gateway = get_default_gateway()
    dns_servers = get_dns_servers()
    
    # Get connection info
    hostname = socket.gethostname()
    interface_type = detect_interface_type()
    
    # Traceroute
    traceroute_hops = []
    if include_traceroute:
        traceroute_hops = run_traceroute(traceroute_host, max_hops=5)
    
    return NetworkInfo(
        public_ip=public_ip,
        isp=isp,
        local_ip=local_ip,
        default_gateway=gateway,
        dns_servers=dns_servers,
        hostname=hostname,
        interface_type=interface_type,
        traceroute_hops=traceroute_hops,
    )

