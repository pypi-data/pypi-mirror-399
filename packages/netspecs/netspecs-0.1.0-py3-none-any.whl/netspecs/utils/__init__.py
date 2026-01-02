"""Utility modules for netspecs."""

from netspecs.utils.platform import (
    get_ping_command,
    parse_ping_output,
    get_system_info,
)
from netspecs.utils.config import Config, load_config

__all__ = [
    "get_ping_command",
    "parse_ping_output",
    "get_system_info",
    "Config",
    "load_config",
]

