# etsi/watchdog/__init__.py

"""
etsi.watchdog — v3.0.0
Real-time Data Drift Detection & Monitoring
"""

from .drift_check import DriftCheck
from .monitor import Monitor
from .compare import DriftComparator
from .drift.base import DriftResult
from .drift.factory import register_drift_algorithm, get_drift_function
from .slack_notifier import SlackNotifier
from .config import WatchdogConfig, quick_setup

# Expose new models
from .models.isolation_forest import IsolationForestModel

__version__ = "3.0.0"

__all__ = [
    "DriftCheck",
    "Monitor",
    "DriftComparator",
    "DriftResult",
    "SlackNotifier",
    "WatchdogConfig",
    "quick_setup",
    "IsolationForestModel",
    "register_drift_algorithm",
    "get_drift_function",
]
