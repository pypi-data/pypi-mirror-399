"""
Device client for SystemNexa2 integration.

Handles connection, message processing, and lifecycle events for devices.
"""

import asyncio
import contextlib
import json
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

import aiohttp
import websockets

from .constants import (
    CONNECTION_TIMEOUT_IN_SECONDS,
    DEVICE_PORT,
    IN_WALL_MODELS,
    LIGHT_MODELS,
    PLUG_MODELS,
    SWITCH_MODELS,
)
from .data_model import InformationData, Settings

_LOGGER = logging.getLogger(__name__)


class DeviceInitializationError(Exception):
    """Exception raised when device initialization fails."""


class NotConnectedError(Exception):
    """Exception raised when device has not been connected before running commands."""


@dataclass
class ConnectionStatus:
    """Connection status event."""

    connected: bool


@dataclass
class InformationUpdate:
    """Information status event."""

    information: InformationData


@dataclass
class StateChange:
    """
    State change event.

    Attributes
    ----------
    state : float
        The new state value of the device.

    """

    state: float


class Setting:
    """
    Base class for device settings.

    Attributes
    ----------
    name : str
        The display name of the setting.

    """

    name: str


class OnOffSetting(Setting):
    """
    A setting that represents an on/off state with configurable values.

    This class extends the Setting base class to provide a binary state setting
    that can be toggled between two predefined values (on and off).

    Args:
        name (str): The display name for this setting.
        param_key (str): The parameter key to use when communicating with the device.
        current: The current value/state of the setting.
        on_value: The value that represents the enabled/on state.
        off_value: The value that represents the disabled/off state.

    """

    def __init__(self, name: str, param_key: str, current: Any, on_value: Any, off_value: Any) -> None:
        """
        Initialize a Device instance.

        Args:
            name (str): The name of the device.
            param_key (str): The parameter key used to identify the device
                parameter.
            current (Any): The current state/value of the device.
            on_value (Any): The value that represents the device being in an
                "on" state.
            off_value (Any): The value that represents the device being in an
                "off" state.

        Returns:
            None

        """
        self.name = name
        self._param_key = param_key
        self._enable_value = on_value
        self._disable_value = off_value
        self._current_state = current

    async def enable(self, device: "Device") -> None:
        """
        Enable a setting with the enable value.

        Args:
            device (Device): The device instance to which the setting should be enabled.

        """
        await device.update_setting({self._param_key: self._enable_value})

    async def disable(self, device: "Device") -> None:
        """
        Disable the setting.

        Args:
            device (Device): The device instance to which the setting should be
                disabled.

        """
        await device.update_setting({self._param_key: self._disable_value})

    def is_enabled(self) -> bool:
        """
        Check if the setting is currently enabled.

        Returns:
            bool: True if the device's current state matches the enable value,
                False otherwise.

        """
        return self._current_state == self._enable_value


@dataclass
class SettingsUpdate:
    """Settings update event."""

    settings: list[Setting]


UpdateEvent = ConnectionStatus | InformationUpdate | SettingsUpdate | StateChange


def _is_version_compatible(version: str | None, min_version: str) -> bool:
    """Check if a version string meets minimum version requirements."""
    if version is None:
        return False
    if min_version is None:
        msg = "min_version needs to be set when comparing"
        raise ValueError(msg)
    try:
        # Clean up version strings - remove any pre-release indicators
        # Example: "0.9.5-beta.2" becomes "0.9.5"
        clean_version = version.split("-")[0].split("+")[0]
        clean_min_version = min_version.split("-")[0].split("+")[0]

        version_parts = [int(part) for part in clean_version.split(".")]
        min_version_parts = [int(part) for part in clean_min_version.split(".")]

        while len(version_parts) < len(min_version_parts):
            version_parts.append(0)
        while len(min_version_parts) < len(version_parts):
            min_version_parts.append(0)

        # Compare version components
        for v, m in zip(version_parts, min_version_parts, strict=False):
            if v > m:
                return True
            if v < m:
                return False

        # All components are equal, so versions are equal

    except (ValueError, IndexError):
        # If parsing fails, log the error and reject the version
        _LOGGER.exception(
            "Error parsing version strings '%s' and '%s'",
            version,
            min_version,
        )
        return False
    return True


class Device:
    """
    Represents a client for SystemNexa2 device integration.

    Handles connection, message processing, and lifecycle events for devices.

    """

    @staticmethod
    def is_device_supported(model: str | None, device_version: str | None) -> tuple[bool, str]:
        """Check if a device is supported based on model and firmware version."""
        # Check if this is a supported device
        if model is None:
            return False, "Missing model information"

        # Verify model is in our supported lists
        if (
            model not in SWITCH_MODELS
            and model not in LIGHT_MODELS
            and model not in PLUG_MODELS
            and model not in IN_WALL_MODELS
        ):
            return False, f"Unsupported model: {model}"

        # Check firmware version requirement
        if device_version is None:
            return False, "Missing firmware version"

        # Version check - require at least 0.9.5
        if not _is_version_compatible(device_version, min_version="0.9.5"):
            return (
                False,
                f"Incompatible firmware version {device_version} (min required: 0.9.5)",
            )

        return True, ""

    def __init__(
        self,
        host: str,
        initial_settings: list[Setting],
        initial_info_data: InformationData,
        session: aiohttp.ClientSession,
        on_update: Callable[[UpdateEvent], Awaitable[None] | None] | None = None,
        *,
        owns_session: bool = False,
    ) -> None:
        """Initialize the Device client. Should not be used see initiate_device."""
        self.host = host
        self._websocket: websockets.ClientConnection | None = None
        self._ws_task: asyncio.Task[None] | None = None
        self._connection_ready = asyncio.Event()
        self._send_queue: asyncio.Queue[str] = asyncio.Queue(maxsize=1)
        self._version = initial_info_data.sw_version
        self.info_data = initial_info_data
        self.settings = initial_settings
        self._session = session
        self._owns_session = owns_session

        # Callbacks
        self._on_update = on_update

    @staticmethod
    async def initiate_device(
        host: str,
        on_update: Callable[[UpdateEvent], Awaitable[None] | None] | None = None,
        session: aiohttp.ClientSession | None = None,
    ) -> "Device":
        """
        Initialize the device by fetching settings and information.

        Args:
            host: The device hostname or IP address.
            on_update: Optional callback for device update events.
            session: Optional aiohttp session. If None, a session will be created
                    and managed internally. The device will close it on cleanup.

        Raises:
            DeviceInitializationError: If fetching settings or information fails.

        """
        owns_session = session is None
        created_session = None

        try:
            if session is None:
                session = aiohttp.ClientSession()
                created_session = session

            settings = await Device._get_settings(host, session)
            info = await Device._get_info(host, session)

            return Device(
                host=host,
                initial_settings=settings,
                initial_info_data=info.information,
                on_update=on_update,
                session=session,
                owns_session=owns_session,
            )
        except Exception as e:
            msg = "Failed to initialize device"
            # Only close session if we created it and initialization failed
            if created_session:
                await created_session.close()
            raise DeviceInitializationError(msg) from e

    async def _emit(self, event: UpdateEvent) -> None:
        """Invoke unified callback if provided."""
        if not self._on_update:
            return
        try:
            result = self._on_update(event)
            if isinstance(result, Awaitable):
                await result
        except Exception:
            _LOGGER.exception("on_update callback failed for %s", event)

    def is_connected(self) -> bool:
        """
        Check if the WebSocket connection is established and ready.

        Returns:
            bool: True if connected and ready to send commands.

        """
        return self._connection_ready.is_set() and self._websocket is not None

    async def connect(self, *, wait_ready: bool = False) -> None:
        """
        Establish a connection to the device via websocket.

        Args:
            wait_ready: If True, wait until the WebSocket connection is established
                       before returning. If False, start the connection task and
                       return immediately.

        Raises:
            TimeoutError: If wait_ready=True and connection is not established within 10 seconds.

        """
        if self._ws_task is None:
            self._ws_task = asyncio.create_task(self._handle_connection())

        if wait_ready:
            try:
                async with asyncio.timeout(CONNECTION_TIMEOUT_IN_SECONDS):
                    await self._connection_ready.wait()
            except TimeoutError as e:
                msg = f"Failed to connect to {self.host} within 10 seconds"
                raise TimeoutError(msg) from e

    # Set up connection and cleanup
    async def _send_loop(self, websocket: websockets.ClientConnection) -> None:
        """Send commands from the queue to the WebSocket."""
        try:
            while True:
                command_str = await self._send_queue.get()
                try:
                    await websocket.send(command_str)
                    if command_str == json.dumps({"type": "login", "value": ""}):
                        self._connection_ready.set()
                    _LOGGER.debug("Sent queued command: %s", command_str)
                except websockets.exceptions.ConnectionClosed:
                    _LOGGER.warning("Connection closed while sending command: %s", command_str)
                    # Put the command back in the queue for retry after reconnection
                    await self._send_queue.put(command_str)
                    break
                except Exception:
                    _LOGGER.exception("Error sending command: %s", command_str)
                finally:
                    self._send_queue.task_done()
        except asyncio.CancelledError:
            _LOGGER.debug("Send loop cancelled")
            raise

    async def _receive_loop(self, websocket: websockets.ClientConnection) -> None:
        """Receive and process messages from the WebSocket."""
        try:
            while True:
                message = await websocket.recv()
                _LOGGER.debug("Received message: %s", message)
                match message:
                    case bytes():
                        await self._process_message(message.decode("utf-8"))
                    case str():
                        await self._process_message(message)
        except websockets.exceptions.ConnectionClosed:
            _LOGGER.debug("WebSocket connection closed")
        except asyncio.CancelledError:
            _LOGGER.debug("Receive loop cancelled")
            raise

    async def _handle_connection(self) -> None:
        """Start the websocket client for the device."""
        uri = f"ws://{self.host}:{DEVICE_PORT}/live"

        def _raise_task_exception(task: asyncio.Task[None]) -> None:
            """Raise exception from a task if present."""
            if not task.cancelled():
                exc = task.exception()
                if exc:
                    raise exc

        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    self._websocket = websocket
                    await self._emit(ConnectionStatus(connected=True))

                    # Queue login message to be sent by send loop
                    login_message = {"type": "login", "value": ""}
                    await self._send_queue.put(json.dumps(login_message))
                    _LOGGER.debug("Queued login message: %s", login_message)

                    # Create send and receive tasks
                    send_task = asyncio.create_task(self._send_loop(websocket))
                    receive_task = asyncio.create_task(self._receive_loop(websocket))

                    # Wait for either task to complete (indicates connection closed)
                    done, pending = await asyncio.wait({send_task, receive_task}, return_when=asyncio.FIRST_COMPLETED)

                    # Cancel remaining tasks
                    for task in pending:
                        task.cancel()
                        with contextlib.suppress(asyncio.CancelledError):
                            await task

                    # Check for exceptions in completed tasks
                    for task in done:
                        _raise_task_exception(task)

            except asyncio.CancelledError:
                break
            except BaseException:
                # Set device as unavailable when connection attempt fails
                await self._emit(ConnectionStatus(connected=False))
                _LOGGER.exception("Lost connection to: %s", self.host)
            finally:
                # Clear connection ready flag
                self._connection_ready.clear()

            # Wait before trying to reconnect
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break

    async def disconnect(self) -> None:
        """Stop the websocket client."""
        self._connection_ready.clear()

        if self._ws_task is not None:
            self._ws_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._ws_task
            self._ws_task = None

        if self._websocket is not None:
            await self._websocket.close()
            self._websocket = None
        await self._emit(ConnectionStatus(connected=False))

    async def close(self) -> None:
        """Close the device connection and clean up resources."""
        await self.disconnect()
        if self._owns_session and self._session:
            await self._session.close()

    async def __aenter__(self) -> "Device":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Async context manager exit."""
        await self.close()

    async def _process_message(self, message: str) -> None:
        """Process a message from the device."""
        try:
            data = json.loads(message)

            # Handle reset message - device wants to be removed
            match data.get("type"):
                case "device_reset":
                    _LOGGER.info("device_reset")
                    return
                case "state":
                    # Handle state updates
                    state_value = float(data.get("value", 0))
                    # Find the entity directly from the device_info
                    await self._emit(StateChange(state_value))
                case "information":
                    info_message = data.get("value")
                    _LOGGER.debug("information received %s", info_message)
                    await self._emit(InformationUpdate(InformationData.from_device_dict(info_message)))
                case "settings":
                    settings = data.get("value")
                    settings = Settings.from_device_dict(settings)
                    await self._emit(SettingsUpdate(settings=await self._parse_settings(settings)))
                case "ack":
                    _LOGGER.debug("Ack received?")
                case unknown:
                    _LOGGER.error("unknown data received %s", unknown)

        except json.JSONDecodeError:
            _LOGGER.exception("Invalid JSON received %s", message)
        except Exception:
            _LOGGER.exception("Error processing message %s", message)

    async def set_brightness(self, value: float) -> None:
        """
        Set the brightness level of the device.

        Parameters
        ----------
        value : float
            The brightness value between 0.0 (off) and 1.0 (full brightness).

        Raises
        ------
        ValueError
            If the brightness value is not between 0 and 1.

        """
        if not 0 <= value <= 1:
            msg = f"Brightness value must be between 0 and 1, got {value}"
            raise ValueError(msg)
        await self.send_command({"type": "state", "value": value})

    async def toggle(self) -> None:
        """Toggle the device state between on and off."""
        await self.send_command({"type": "state", "value": -1})

    async def turn_off(self) -> None:
        """Turn off the device."""
        if _is_version_compatible(self._version, "1.1.8"):
            await self.send_command({"type": "state", "on": False})
        else:
            await self.send_command({"type": "state", "value": 0})

    async def turn_on(self) -> None:
        """Turn on the device."""
        if _is_version_compatible(self._version, "1.1.8"):
            await self.send_command({"type": "state", "on": True})
        else:
            await self.send_command({"type": "state", "value": -1})

    async def send_command(
        self,
        command: dict[str, Any],
        *,
        wait_for_connection: bool = True,
    ) -> None:
        """
        Send a command to the device via WebSocket.

        Commands are queued and sent asynchronously through a dedicated send loop.
        This ensures thread-safe sending and proper command ordering.

        Args:
            command: A dictionary containing the command data to send to the device.
            wait_for_connection: If True, wait for the connection to be ready before
                               queuing the command. If False, queue immediately.
            connection_timeout: Maximum time in seconds to wait for connection when
                              wait_for_connection=True.

        Returns:
            None

        Raises:
            NotConnectedError: If not trying to connect.
            TimeoutError: If wait_for_connection=True and connection is not established
                        within connection_timeout.

        """
        if self._ws_task is None:
            msg = f"Cannot send command to {self.host} - Please connect() first"
            _LOGGER.error(msg)
            raise NotConnectedError(msg)

        # Wait for connection to be ready if requested
        if wait_for_connection and not self.is_connected():
            try:
                async with asyncio.timeout(CONNECTION_TIMEOUT_IN_SECONDS):
                    await self._connection_ready.wait()
            except TimeoutError as e:
                msg = f"Connection to {self.host} not ready within {CONNECTION_TIMEOUT_IN_SECONDS} seconds"
                raise TimeoutError(msg) from e

        # Queue the command for sending
        command_str = json.dumps(command)
        await self._send_queue.put(command_str)
        _LOGGER.debug("Queued command for %s: %s", self.host, command_str)

    @staticmethod
    async def _parse_settings(settings: Settings) -> list[Setting]:
        settings_list: list[Setting] = []
        if settings.disable_433 is not None:
            settings_list.append(
                OnOffSetting(
                    param_key="disable_433",
                    name="433Mhz",
                    off_value=1,
                    on_value=0,
                    current=settings.disable_433,
                )
            )
        if settings.disable_physical_button is not None:
            settings_list.append(
                OnOffSetting(
                    param_key="disable_physical_button",
                    name="Physical Button",
                    off_value=1,
                    on_value=0,
                    current=settings.disable_physical_button,
                )
            )
        if settings.disable_led is not None:
            settings_list.append(
                OnOffSetting(
                    param_key="disable_led",
                    name="Led",
                    off_value=1,
                    on_value=0,
                    current=settings.disable_led,
                )
            )
        if settings.diy_mode is not None:
            settings_list.append(
                OnOffSetting(
                    param_key="diy_mode",
                    name="Cloud Access",
                    off_value=1,
                    on_value=0,
                    current=settings.diy_mode,
                )
            )
        return settings_list

    async def update_setting(self, settings: dict[str, Any]) -> None:
        """Update device settings via REST API."""
        url = f"http://{self.host}:{DEVICE_PORT}/settings"
        try:
            async with self._session.post(url, json=settings) as response:
                response.raise_for_status()
                _LOGGER.debug("Updated settings at %s with %s", url, settings)
        except Exception:
            _LOGGER.exception("Failed to update settings at %s", url)
            raise

    @staticmethod
    async def _get_settings(host: str, session: aiohttp.ClientSession) -> list[Setting]:
        """Fetch device settings via REST API."""
        url = f"http://{host}:{DEVICE_PORT}/settings"
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                json_resp = await response.json()
                return await Device._parse_settings(Settings.from_device_dict(json_resp))
        except Exception:
            _LOGGER.exception("Failed to fetch settings from %s", url)
            raise

    async def get_settings(self) -> list[Setting]:
        """Fetch device settings via REST API."""
        return await self._get_settings(self.host, self._session)

    @staticmethod
    async def _get_info(host: str, session: aiohttp.ClientSession) -> InformationUpdate:
        url = f"http://{host}:{DEVICE_PORT}/info"
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                info_data = InformationData.from_device_dict(await response.json())
                return InformationUpdate(info_data)
        except Exception:
            _LOGGER.exception("Failed to fetch device information from %s:", url)
            raise

    async def get_info(self) -> InformationUpdate:
        """Fetch device information via REST API."""
        return await self._get_info(self.host, self._session)
