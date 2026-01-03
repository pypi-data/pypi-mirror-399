"""
UCUP Plugin System

Extensible plugin architecture for UCUP framework allowing dynamic
loading of benchmarks, coordinators, and custom functionality.
"""

from .base import (
    AgentPlugin,
    MonitorPlugin,
    Plugin,
    PluginConfig,
    PluginError,
    PluginMetadata,
    StrategyPlugin,
)

# Import donation plugin
from .donation_plugin import DonationPlugin

# Import existing plugins
from .example_agent import CustomerServiceAgentPlugin
from .example_strategy import CreativeBrainstormingStrategyPlugin
from .monitoring_plugin import MetricsMonitorPlugin, TracingMonitorPlugin

__all__ = [
    # Base classes
    "Plugin",
    "PluginMetadata",
    "PluginConfig",
    "PluginError",
    # Existing plugins
    "CustomerServiceAgentPlugin",
    "CreativeBrainstormingStrategyPlugin",
    "MetricsMonitorPlugin",
    "TracingMonitorPlugin",
    # Donation plugin
    "DonationPlugin",
]

__version__ = "1.0.0"
