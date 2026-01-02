"""
bc_trb SDK - Python bindings for EEG-CES device communication.

This package provides a Python interface to the bc_trb SDK for EEG data acquisition.

Example:
    >>> from bc_trb_sdk import open_triggerhub_device
    >>> device = open_triggerhub_device()
    >>> print("TriggerHub device connected")
"""

__version__ = "0.1.0"

# Import from the extension module
from ._native import (
    # Enums
    LogLevel,

    # Model types
    DeviceApi,
    DeviceInfo,

    # Trigger types
    TrbAdcValue,
    TrbConfig,
    TrbStatus,
    TriggerApi,

    # DeviceApi functions - TriggerHub
    open_triggerhub_device,

)

__all__ = [
    # Enums
    "LogLevel",

    # Model types
    "DeviceApi",
    "DeviceInfo",

    # TriggerHub types
    "TrbAdcValue",
    "TrbConfig",
    "TrbStatus",
    "TriggerApi",

    # DeviceApi functions - TriggerHub
    "open_triggerhub_device",

]