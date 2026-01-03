"""
A Python abstraction layer for GW-Instek GPP series power supplies.

This package provides a unified driver for GPP-3060, GPP-3650, and GPP-6030
units via VISA (USB/LAN/RS232).
"""


from .gpp import (GPP,
                  GPP3060,
                  GPP3650,
                  GPP6030,
                  ChannelMode,
                  Measurement,
                  TrackingMode,
                  Terminal)

__all__ = [
    "GPP",
    "Measurement",
    "TrackingMode",
    "ChannelMode",
    "Terminal",
    "GPP3060",
    "GPP3650",
    "GPP6030",
]