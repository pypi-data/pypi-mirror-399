"""Configuration management for netspecs."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml
from dotenv import load_dotenv


# Default test endpoints
DEFAULT_ENDPOINTS = [
    "8.8.8.8",              # Google DNS
    "1.1.1.1",              # Cloudflare DNS
    "208.67.222.222",       # OpenDNS
    "google.com",
    "cloudflare.com",
    "steam-chat.com",
    "ping-nae.ds.on.epicgames.com",
    "riotgames.com",
    "blizzard.com",
]

# Default LLM model
DEFAULT_MODEL = "gpt-5.2"

# Default output directory name
DEFAULT_OUTPUT_DIR = "netspecs_reports"

# Config file search paths
CONFIG_FILENAMES = ["netspecs.yaml", "netspecs.yml", ".netspecs.yaml", ".netspecs.yml"]


@dataclass
class OutputConfig:
    """Output configuration."""
    directory: Path = field(default_factory=lambda: Path(f"./{DEFAULT_OUTPUT_DIR}"))
    format: str = "console"
    timestamp_files: bool = True
    include_raw_data: bool = False


@dataclass
class LatencyTestConfig:
    """Latency test configuration."""
    ping_count: int = 20
    timeout_seconds: int = 2


@dataclass
class JitterTestConfig:
    """Jitter test configuration."""
    duration_seconds: int = 60
    interval_seconds: int = 1


@dataclass
class SpeedTestConfig:
    """Speed test configuration."""
    iterations: int = 5
    include_ookla: bool = True


@dataclass
class BufferbloatTestConfig:
    """Bufferbloat test configuration."""
    baseline_duration: int = 15
    load_duration: int = 30
    include_upload: bool = True


@dataclass
class PrioritizationTestConfig:
    """Prioritization test configuration."""
    phase_duration_seconds: int = 120


@dataclass
class MonitorTestConfig:
    """Monitor test configuration."""
    default_duration_minutes: int = 60
    ping_interval_seconds: float = 1.0
    stats_interval_seconds: int = 60


@dataclass
class TestsConfig:
    """All test configurations."""
    latency: LatencyTestConfig = field(default_factory=LatencyTestConfig)
    jitter: JitterTestConfig = field(default_factory=JitterTestConfig)
    speed: SpeedTestConfig = field(default_factory=SpeedTestConfig)
    bufferbloat: BufferbloatTestConfig = field(default_factory=BufferbloatTestConfig)
    prioritization: PrioritizationTestConfig = field(default_factory=PrioritizationTestConfig)
    monitor: MonitorTestConfig = field(default_factory=MonitorTestConfig)


@dataclass
class AIConfig:
    """AI report configuration."""
    model: str = DEFAULT_MODEL
    temperature: float = 0.7
    include_recommendations: bool = True
    api_key: Optional[str] = None


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    log_to_file: bool = True


@dataclass
class Config:
    """Main configuration for netspecs diagnostics."""
    
    # Structured config sections
    output: OutputConfig = field(default_factory=OutputConfig)
    tests: TestsConfig = field(default_factory=TestsConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Endpoints
    endpoints: list[str] = field(default_factory=lambda: DEFAULT_ENDPOINTS.copy())
    
    # Legacy compatibility properties
    @property
    def output_dir(self) -> Path:
        return self.output.directory
    
    @property
    def output_format(self) -> str:
        return self.output.format
    
    @property
    def model(self) -> str:
        return self.ai.model
    
    @property
    def api_key(self) -> Optional[str]:
        return self.ai.api_key
    
    @property
    def ping_count(self) -> int:
        return self.tests.latency.ping_count
    
    @property
    def jitter_duration(self) -> int:
        return self.tests.jitter.duration_seconds
    
    @property
    def jitter_interval(self) -> int:
        return self.tests.jitter.interval_seconds
    
    @property
    def speed_test_iterations(self) -> int:
        return self.tests.speed.iterations
    
    @property
    def prioritization_phase_duration(self) -> int:
        return self.tests.prioritization.phase_duration_seconds


def _find_config_file() -> Optional[Path]:
    """Find configuration file in standard locations."""
    # Check current directory
    for filename in CONFIG_FILENAMES:
        path = Path(filename)
        if path.exists():
            return path
    
    # Check home directory
    home = Path.home()
    for filename in CONFIG_FILENAMES:
        path = home / filename
        if path.exists():
            return path
    
    return None


def _parse_endpoints(data: dict[str, Any]) -> list[str]:
    """Parse endpoints from config data."""
    endpoints_data = data.get("endpoints", {})
    
    if isinstance(endpoints_data, list):
        return endpoints_data
    
    # Flatten nested endpoint categories
    endpoints = []
    for category in ["dns", "general", "gaming", "custom"]:
        category_endpoints = endpoints_data.get(category, [])
        if isinstance(category_endpoints, list):
            endpoints.extend(category_endpoints)
    
    return endpoints if endpoints else DEFAULT_ENDPOINTS.copy()


def _load_yaml_config(path: Path) -> dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        return data
    except Exception:
        return {}


def load_config(
    config_file: Optional[str] = None,
    env_file: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    endpoints: Optional[list[str]] = None,
    output_dir: Optional[str] = None,
    output_format: Optional[str] = None,
) -> Config:
    """
    Load configuration from file, environment, and CLI options.
    
    Priority order (highest to lowest):
    1. Explicit function arguments
    2. Environment variables
    3. Config file (netspecs.yaml)
    4. Defaults
    
    Args:
        config_file: Path to config file (auto-detected if not specified)
        env_file: Path to .env file (defaults to .env.local)
        api_key: Explicit API key
        model: LLM model to use
        endpoints: Custom test endpoints
        output_dir: Output directory for logs
        output_format: Output format (console, json, csv)
        
    Returns:
        Configured Config instance
    """
    # Load environment variables
    env_path = Path(env_file) if env_file else Path(".env.local")
    if env_path.exists():
        load_dotenv(env_path)
    if Path(".env").exists():
        load_dotenv(".env")
    
    # Load config file
    config_path = Path(config_file) if config_file else _find_config_file()
    file_config: dict[str, Any] = {}
    if config_path and config_path.exists():
        file_config = _load_yaml_config(config_path)
    
    # Build output config
    output_data = file_config.get("output", {})
    output_config = OutputConfig(
        directory=Path(output_dir or output_data.get("directory", f"./{DEFAULT_OUTPUT_DIR}")),
        format=output_format or output_data.get("format", "console"),
        timestamp_files=output_data.get("timestamp_files", True),
        include_raw_data=output_data.get("include_raw_data", False),
    )
    
    # Build test configs
    tests_data = file_config.get("tests", {})
    tests_config = TestsConfig(
        latency=LatencyTestConfig(
            ping_count=tests_data.get("latency", {}).get("ping_count", 20),
            timeout_seconds=tests_data.get("latency", {}).get("timeout_seconds", 2),
        ),
        jitter=JitterTestConfig(
            duration_seconds=tests_data.get("jitter", {}).get("duration_seconds", 60),
            interval_seconds=tests_data.get("jitter", {}).get("interval_seconds", 1),
        ),
        speed=SpeedTestConfig(
            iterations=tests_data.get("speed", {}).get("iterations", 5),
            include_ookla=tests_data.get("speed", {}).get("include_ookla", True),
        ),
        bufferbloat=BufferbloatTestConfig(
            baseline_duration=tests_data.get("bufferbloat", {}).get("baseline_duration", 15),
            load_duration=tests_data.get("bufferbloat", {}).get("load_duration", 30),
            include_upload=tests_data.get("bufferbloat", {}).get("include_upload", True),
        ),
        prioritization=PrioritizationTestConfig(
            phase_duration_seconds=tests_data.get("prioritization", {}).get("phase_duration_seconds", 120),
        ),
        monitor=MonitorTestConfig(
            default_duration_minutes=tests_data.get("monitor", {}).get("default_duration_minutes", 60),
            ping_interval_seconds=tests_data.get("monitor", {}).get("ping_interval_seconds", 1.0),
            stats_interval_seconds=tests_data.get("monitor", {}).get("stats_interval_seconds", 60),
        ),
    )
    
    # Resolve API key
    resolved_api_key = api_key
    if not resolved_api_key:
        for key_name in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "LITELLM_API_KEY", "API_KEY"]:
            resolved_api_key = os.getenv(key_name)
            if resolved_api_key:
                break
    
    # Build AI config
    ai_data = file_config.get("ai", {})
    ai_config = AIConfig(
        model=model or os.getenv("NETSPECS_MODEL") or ai_data.get("model", DEFAULT_MODEL),
        temperature=ai_data.get("temperature", 0.7),
        include_recommendations=ai_data.get("include_recommendations", True),
        api_key=resolved_api_key,
    )
    
    # Build logging config
    logging_data = file_config.get("logging", {})
    logging_config = LoggingConfig(
        level=logging_data.get("level", "INFO"),
        log_to_file=logging_data.get("log_to_file", True),
    )
    
    # Build endpoints
    resolved_endpoints = endpoints if endpoints else _parse_endpoints(file_config)
    
    return Config(
        output=output_config,
        tests=tests_config,
        ai=ai_config,
        logging=logging_config,
        endpoints=resolved_endpoints,
    )
