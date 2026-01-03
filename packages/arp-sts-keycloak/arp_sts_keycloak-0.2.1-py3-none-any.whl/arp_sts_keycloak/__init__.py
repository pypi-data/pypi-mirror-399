from __future__ import annotations

__all__ = ["__version__", "DEFAULT_REALM", "DEFAULT_CLIENTS"]

__version__ = "0.2.1"
DEFAULT_REALM = "arp-dev"
DEFAULT_CLIENTS = (
    "arp-daemon",
    "arp-runtime",
    "arp-tool-registry",
    "arp-run-gateway",
    "arp-run-coordinator",
    "arp-composite-executor",
    "arp-atomic-executor",
    "arp-node-registry",
    "arp-selection-service",
    "arp-pdp",
)
