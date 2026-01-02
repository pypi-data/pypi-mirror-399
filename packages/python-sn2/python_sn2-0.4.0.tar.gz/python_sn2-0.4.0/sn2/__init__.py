"""Python library for SystemNexa2 device integration."""

from sn2.device import (
    ConnectionStatus,
    Device,
    DeviceInitializationError,
    InformationData,
    InformationUpdate,
    NotConnectedError,
    OnOffSetting,
    SettingsUpdate,
    StateChange,
)

__version__ = "0.4.0"
__all__ = [
    "ConnectionStatus",
    "Device",
    "DeviceInitializationError",
    "InformationData",
    "InformationUpdate",
    "NotConnectedError",
    "OnOffSetting",
    "SettingsUpdate",
    "StateChange",
]
