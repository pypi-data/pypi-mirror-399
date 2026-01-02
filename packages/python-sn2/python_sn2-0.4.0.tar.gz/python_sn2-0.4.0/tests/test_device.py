"""
Test suite for the Device class in the SystemNexa2 integration.

This module contains tests for the Device class, including positive and
negative test cases for WebSocket communication, message processing, and
lifecycle events.
"""

import asyncio
import json
import logging
import sys
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, Mock, patch

import pytest
import websockets

from sn2.data_model import InformationData
from sn2.device import (
    ConnectionStatus,
    Device,
    DeviceInitializationError,
    InformationUpdate,
    NotConnectedError,
    OnOffSetting,
    SettingsUpdate,
    StateChange,
    UpdateEvent,
    _is_version_compatible,
)

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture(autouse=True)
def configure_logger() -> None:
    """Configure the logger to output to stdout during tests."""
    logger = logging.getLogger("sn2.device")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.handlers = [handler]


@pytest.mark.asyncio
class TestDevice:
    """Test suite for the Device class."""

    @pytest.fixture
    def device(self) -> Device:
        """Fixture to create a Device instance."""
        self.on_update_mock = AsyncMock()
        # Create a proper mock session with async context manager support
        mock_session = AsyncMock()

        # Configure get method to return an async context manager
        mock_response = Mock()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        mock_response.raise_for_status = Mock()
        mock_response.json = AsyncMock(return_value={})
        mock_session.get = Mock(return_value=mock_response)

        # Configure post method similarly
        mock_post_response = Mock()
        mock_post_response.__aenter__ = AsyncMock(return_value=mock_post_response)
        mock_post_response.__aexit__ = AsyncMock(return_value=None)
        mock_post_response.raise_for_status = Mock()
        mock_session.post = Mock(return_value=mock_post_response)

        return Device(
            host="192.168.1.100",
            initial_settings=[],
            initial_info_data=InformationData.from_device_dict(
                {"lcu": "testdeviceid", "hwm": "1.0.0", "n": "test device"}
            ),
            session=mock_session,
            on_update=self.on_update_mock,
        )

    @pytest.fixture
    def mock_websocket(self) -> "Generator":
        """Properly patch websockets.connect to work with any URL."""
        with patch("websockets.connect") as mocked_connect:
            # Create a simple object with the methods we need
            class MockWebSocket:
                def __init__(self) -> None:
                    self.messages_sent: list[str] = []
                    self._close_event = asyncio.Event()

                async def recv(self) -> str:
                    """Simulate receiving - loops until closed (no login response from real device)."""
                    # Just wait until closed - real device doesn't send login response
                    await self._close_event.wait()
                    # Once close event is set, raise ConnectionClosed
                    raise websockets.exceptions.ConnectionClosed(None, None)

                async def send(self, message: str) -> None:
                    """Track sent messages."""
                    self.messages_sent.append(message)

                async def close(self) -> None:
                    """Close the mock websocket."""
                    self._close_event.set()

            # Create the mock websocket instance once
            mock_ws_instance = MockWebSocket()

            # Create async context manager
            class MockContextManager:
                mock_ws = mock_ws_instance  # Store reference for test assertions

                async def __aenter__(self) -> MockWebSocket:
                    mock_ws_instance._close_event.clear()  # Reset for each connection
                    return mock_ws_instance

                async def __aexit__(self, _exc: object, _val: object, _tb: object) -> None:
                    mock_ws_instance._close_event.set()  # Ensure cleanup

            # Make connect return the context manager
            context_manager = MockContextManager()
            mocked_connect.return_value = context_manager

            yield mocked_connect

    async def test_connect_disconnect_success(self, mock_websocket: AsyncMock, device: Device) -> None:
        """Test successful connection and disconnection to the device."""
        mock_ws = mock_websocket.return_value.mock_ws

        await device.connect()
        await asyncio.sleep(0.05)  # Give send_loop time to process
        await asyncio.sleep(0)  # Allow the task to start

        # Verify login message was sent
        assert json.dumps({"type": "login", "value": ""}) in mock_ws.messages_sent

        # Verify connection status callback was called
        latest_update = self.on_update_mock.call_args_list[-1]
        assert isinstance(latest_update.args[0], ConnectionStatus)
        latest_args = latest_update.args[0]
        assert latest_args.connected is True

        # Disconnect
        await device.disconnect()
        await asyncio.sleep(0.1)

        # Verify disconnect callback was called
        latest_update = self.on_update_mock.call_args_list[-1]
        assert isinstance(latest_update.args[0], ConnectionStatus)
        latest_args = latest_update.args[0]
        assert latest_args.connected is False

    async def test_connection_failure(self, device: Device, mock_websocket: AsyncMock) -> None:
        """Test connection failure handling."""
        mock_websocket.side_effect = ConnectionError("Connection error")

        await device.connect()
        await asyncio.sleep(0.05)  # Give send_loop time to process
        await asyncio.sleep(0.1)  # Allow the task to attempt connection

        # Verify disconnect callback was called due to connection failure
        disconnect_calls = [
            call
            for call in self.on_update_mock.call_args_list
            if isinstance(call[0][0], ConnectionStatus) and not call[0][0].connected
        ]
        assert len(disconnect_calls) > 0

    async def test_information_message_processing(self, device: Device, mock_websocket: AsyncMock) -> None:
        """Test processing of information message from device."""
        info_message = json.dumps(
            {
                "type": "information",
                "value": {
                    "fhs": 90752,
                    "u": 261970,
                    "wr": -60,
                    "ss": "0.00",
                    "t": "68.20",
                    "n": "Test Device",
                    "tsc": 3,
                    "lcu": "test-unique-id",
                    "lat": 62,
                    "lon": 15,
                    "cs": True,
                    "sr_h": 8,
                    "sr_m": 1,
                    "ss_h": 15,
                    "ss_m": 25,
                    "tz_o": 3600,
                    "tz_i": 1,
                    "tz_dst": 0,
                    "c": False,
                    "ws": "TestNetwork",
                    "rr": 1,
                    "hwm": "WBD-01",
                    "nhwv": 1,
                    "nswv": "1.1.1",
                    "b": {"s": 1, "v": 0, "bp": 0, "bpr": 0, "bi": 0},
                },
            }
        )

        mock_ws = mock_websocket.return_value.mock_ws
        # Override recv to return message then close connection
        mock_ws.recv = AsyncMock(side_effect=[info_message, websockets.exceptions.ConnectionClosed(None, None)])

        await device.connect()
        await asyncio.sleep(0.05)  # Give send_loop time to process
        await asyncio.sleep(0.1)  # Allow message processing

        # Verify information update callback was called
        info_calls = [call for call in self.on_update_mock.call_args_list if isinstance(call[0][0], InformationUpdate)]
        assert len(info_calls) > 0
        info_data = info_calls[0][0][0].information
        assert info_data.name == "Test Device"
        assert info_data.model == "WBD-01"
        assert info_data.dimmable is True  # WBD-01 is a light model

        await device.disconnect()

    async def test_settings_message_processing(self, device: Device, mock_websocket: AsyncMock) -> None:
        """Test processing of settings message from device."""
        settings_message = json.dumps(
            {
                "type": "settings",
                "value": {
                    "name": "DeviceName",
                    "tz_id": 1,
                    "auto_on_seconds": 0,
                    "auto_off_seconds": 0,
                    "enable_local_security": 0,
                    "vacation_mode": 0,
                    "state_after_powerloss": 2,
                    "disable_physical_button": 0,
                    "disable_433": 1,
                    "disable_multi_press": 0,
                    "disable_network_ctrl": 0,
                    "disable_led": 0,
                    "disable_on_transmitters": 0,
                    "disable_off_transmitters": 0,
                    "dimmer_edge": 0,
                    "blink_on_433_on": 0,
                    "button_type": 0,
                    "diy_mode": 1,
                    "toggle_433": 0,
                    "position_man_set": 0,
                    "dimmer_on_start_level": 0,
                    "dimmer_off_level": 0,
                    "dimmer_min_dim": 0,
                    "remote_log": 1,
                    "notifcation_on": 1,
                    "notifcation_off": 0,
                },
            }
        )

        mock_ws = mock_websocket.return_value.mock_ws
        # Override recv to return message then close connection
        mock_ws.recv = AsyncMock(side_effect=[settings_message, websockets.exceptions.ConnectionClosed(None, None)])

        await device.connect()
        await asyncio.sleep(0.05)  # Give send_loop time to process
        await asyncio.sleep(0.1)  # Allow message processing

        # Verify settings update callback was called
        setting_updates = [
            call.args[0] for call in self.on_update_mock.call_args_list if isinstance(call.args[0], SettingsUpdate)
        ]
        assert len(setting_updates) == 1
        setting_update = setting_updates[0]
        # Filter OnOffSettings from the list
        onoff_settings = [s for s in setting_update.settings if isinstance(s, OnOffSetting)]

        # Verify we have four OnOffSettings
        expected_settings_count = 4
        assert len(onoff_settings) == expected_settings_count

        # Find the 433MHz setting and verify it's off
        # (value == 1 means disabled/off)
        mhz_433_setting = next((s for s in onoff_settings if "433Mhz" in s.name), None)
        assert mhz_433_setting is not None
        assert not mhz_433_setting.is_enabled()
        cloud = next((s for s in onoff_settings if "Cloud Access" in s.name), None)
        assert cloud is not None
        assert not cloud.is_enabled()

        led_setting = next((s for s in onoff_settings if "Led" in s.name), None)
        assert led_setting is not None
        assert led_setting.is_enabled()
        physical_button = next((s for s in onoff_settings if "Physical Button" in s.name), None)
        assert physical_button is not None
        assert physical_button.is_enabled()

        await device.disconnect()

    async def test_state_change_message_processing(self, device: Device, mock_websocket: AsyncMock) -> None:
        """Test processing of state change message from device."""
        state_message = json.dumps({"type": "state", "value": 0.75})

        mock_ws = mock_websocket.return_value.mock_ws
        # Override recv to return message then close connection
        mock_ws.recv = AsyncMock(side_effect=[state_message, websockets.exceptions.ConnectionClosed(None, None)])

        await device.connect()
        await asyncio.sleep(0.05)  # Give send_loop time to process
        await asyncio.sleep(0.1)  # Allow message processing

        # Verify state change callback was called
        expected_brightness = 0.75
        state_calls = [call for call in self.on_update_mock.call_args_list if isinstance(call[0][0], StateChange)]
        assert len(state_calls) > 0
        assert state_calls[0][0][0].state == expected_brightness

        await device.disconnect()

    async def test_get_info_success(self, device: Device) -> None:
        """Test fetching device information via REST API."""
        mock_response_data = {
            "fhs": 90752,
            "u": 261970,
            "wr": -60,
            "ss": "0.00",
            "t": "68.20",
            "n": "Test Device",
            "tsc": 3,
            "lcu": "test-unique-id",
            "lat": 62,
            "lon": 15,
            "cs": True,
            "sr_h": 8,
            "sr_m": 1,
            "ss_h": 15,
            "ss_m": 25,
            "tz_o": 3600,
            "tz_i": 1,
            "tz_dst": 0,
            "c": False,
            "ws": "TestNetwork",
            "rr": 1,
            "hwm": "WBD-01",
            "nhwv": 1,
            "nswv": "1.1.1",
            "b": {"s": 1, "v": 0, "bp": 0, "bpr": 0, "bi": 0},
        }

        # Configure the device's session mock
        mock_response = Mock()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        mock_response.json = AsyncMock(return_value=mock_response_data)
        mock_response.raise_for_status = Mock()
        device._session.get = Mock(return_value=mock_response)

        info = await device.get_info()

        assert info is not None
        assert isinstance(info, InformationUpdate)
        assert info.information.name == "Test Device"
        assert info.information.model == "WBD-01"
        assert info.information.dimmable is True

    async def test_get_info_failure(self, device: Device) -> None:
        """Test failure when fetching device information via REST API."""
        # Configure the device's session mock to raise an error
        device._session.get = Mock(side_effect=RuntimeError("HTTP error"))

        with pytest.raises(RuntimeError, match="HTTP error"):
            await device.get_info()

    async def test_get_settings_success(self, device: Device) -> None:
        """Test fetching device settings via REST API."""
        mock_settings_data = {
            "name": "DeviceName",
            "tz_id": 1,
            "disable_433": 1,
            "diy_mode": 1,
            "disable_led": 0,
        }

        # Configure the device's session mock
        mock_response = Mock()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        mock_response.json = AsyncMock(return_value=mock_settings_data)
        mock_response.raise_for_status = Mock()
        device._session.get = Mock(return_value=mock_response)

        list_of_settings = await device.get_settings()

        assert isinstance(list_of_settings, list)

        # Filter OnOffSettings from the list
        onoff_settings = [s for s in list_of_settings if isinstance(s, OnOffSetting)]

        # We should have four OnOffSettings (433Mhz, diy_mode, disable_led were provided)
        # Note: disable_physical_button is not in mock_settings_data, so it won't be included
        expected_onoff_count = 3
        assert len(onoff_settings) == expected_onoff_count

        # Find the 433MHz setting and verify it's off
        # (value == 1 means disabled/off)
        mhz_433_setting = next((s for s in onoff_settings if "433Mhz" in s.name), None)
        assert mhz_433_setting is not None
        assert not mhz_433_setting.is_enabled()
        cloud = next((s for s in onoff_settings if "Cloud Access" in s.name), None)
        assert cloud is not None
        assert not cloud.is_enabled()

        led_setting = next((s for s in onoff_settings if "Led" in s.name), None)
        assert led_setting is not None
        assert led_setting.is_enabled()

    async def test_get_settings_failure(self, device: Device) -> None:
        """Test failure when fetching device settings via REST API."""
        # Configure the device's session mock to raise an error
        device._session.get = Mock(side_effect=RuntimeError("HTTP error"))

        with pytest.raises(RuntimeError, match="HTTP error"):
            await device.get_settings()

    async def test_turn_on(self, device: Device, mock_websocket: AsyncMock) -> None:
        """Test turning on the device."""
        mock_ws = mock_websocket.return_value.mock_ws

        await device.connect(wait_ready=True)

        await device.turn_on()
        await asyncio.sleep(0.05)  # Give send_loop time to process the command
        await asyncio.sleep(0.05)  # Give send_loop time to process the command

        # Verify turn on command was sent
        turn_on_commands = [
            msg
            for msg in mock_ws.messages_sent
            if json.loads(msg).get("type") == "state" and json.loads(msg).get("value") == -1
        ]
        assert len(turn_on_commands) > 0

        await device.disconnect()

    async def test_turn_off(self, device: Device, mock_websocket: AsyncMock) -> None:
        """Test turning off the device."""
        mock_ws = mock_websocket.return_value.mock_ws

        await device.connect(wait_ready=True)

        await device.turn_off()
        await asyncio.sleep(0.05)  # Give send_loop time to process the command

        # Verify turn off command was sent
        turn_off_commands = [
            msg
            for msg in mock_ws.messages_sent
            if json.loads(msg).get("type") == "state" and json.loads(msg).get("value") == 0
        ]
        assert len(turn_off_commands) > 0

        await device.disconnect()

    async def test_turn_on_v1_1_8(
        self, device: Device, mock_websocket: AsyncMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test turning on the device with version 1.1.8."""
        mock_ws = mock_websocket.return_value.mock_ws

        monkeypatch.setattr(device, "_version", "1.1.8")

        await device.connect(wait_ready=True)

        await device.turn_on()
        await asyncio.sleep(0.05)  # Give send_loop time to process the command

        # Verify turn on command was sent
        turn_on_commands = [
            msg for msg in mock_ws.messages_sent if json.loads(msg).get("type") == "state" and json.loads(msg).get("on")
        ]
        assert len(turn_on_commands) > 0

        await device.disconnect()

    async def test_turn_off_v1_1_8(
        self, device: Device, mock_websocket: AsyncMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test turning off the device with version 1.1.8."""
        mock_ws = mock_websocket.return_value.mock_ws

        monkeypatch.setattr(device, "_version", "1.1.8")

        await device.connect(wait_ready=True)

        await device.turn_off()
        await asyncio.sleep(0.05)  # Give send_loop time to process the command

        # Verify turn off command was sent
        turn_off_commands = [
            msg
            for msg in mock_ws.messages_sent
            if json.loads(msg).get("type") == "state" and not json.loads(msg).get("on")
        ]
        assert len(turn_off_commands) > 0

        await device.disconnect()

    async def test_set_brightness(self, device: Device, mock_websocket: AsyncMock) -> None:
        """Test setting device brightness."""
        mock_ws = mock_websocket.return_value.mock_ws

        await device.connect(wait_ready=True)

        test_brightness = 0.5
        await device.set_brightness(test_brightness)
        await asyncio.sleep(0.05)  # Give send_loop time to process the command

        # Verify brightness command was sent
        brightness_commands = [
            msg
            for msg in mock_ws.messages_sent
            if json.loads(msg).get("type") == "state" and json.loads(msg).get("value") == test_brightness
        ]
        assert len(brightness_commands) > 0

        await device.disconnect()

    async def test_set_brightness_invalid_value(self, device: Device) -> None:
        """Test setting brightness with invalid value."""
        with pytest.raises(ValueError, match="Brightness value must be between"):
            await device.set_brightness(1.5)

        with pytest.raises(ValueError, match="Brightness value must be between"):
            await device.set_brightness(-0.1)

    async def test_toggle(self, device: Device, mock_websocket: AsyncMock) -> None:
        """Test toggling the device."""
        mock_ws = mock_websocket.return_value.mock_ws

        await device.connect(wait_ready=True)

        await device.toggle()
        await asyncio.sleep(0.05)  # Give send_loop time to process the command

        # Verify toggle command was sent (value -1)
        toggle_commands = [
            msg
            for msg in mock_ws.messages_sent
            if json.loads(msg).get("type") == "state" and json.loads(msg).get("value") == -1
        ]
        assert len(toggle_commands) > 0

        await device.disconnect()

    @pytest.mark.usefixtures("mock_websocket")
    async def test_send_command_wait_for_connection_timeout(self, device: Device) -> None:
        """Test send_command timeout when waiting for connection."""
        # Mock the connection_ready event to never be set
        device._connection_ready = asyncio.Event()  # Not set - will timeout
        device._ws_task = asyncio.create_task(asyncio.sleep(0))  # Fake task to bypass check

        # Try to send command with wait - should timeout
        with pytest.raises(TimeoutError):
            await device.send_command({"type": "test"}, wait_for_connection=True)

        await device._ws_task  # Clean up

    async def test_process_message_device_reset(self, device: Device, mock_websocket: AsyncMock) -> None:
        """Test processing device_reset message."""
        reset_message = json.dumps({"type": "device_reset"})
        mock_ws = mock_websocket.return_value.mock_ws
        mock_ws.recv = AsyncMock(side_effect=[reset_message, websockets.exceptions.ConnectionClosed(None, None)])

        await device.connect()
        await asyncio.sleep(0.1)

        # device_reset should not trigger any callbacks
        # Just verify no errors occurred
        await device.disconnect()

    async def test_process_message_ack(self, device: Device, mock_websocket: AsyncMock) -> None:
        """Test processing ack message."""
        ack_message = json.dumps({"type": "ack"})
        mock_ws = mock_websocket.return_value.mock_ws
        mock_ws.recv = AsyncMock(side_effect=[ack_message, websockets.exceptions.ConnectionClosed(None, None)])

        await device.connect()
        await asyncio.sleep(0.1)

        # ack should not trigger callbacks
        await device.disconnect()

    async def test_process_message_unknown_type(self, device: Device, mock_websocket: AsyncMock) -> None:
        """Test processing unknown message type."""
        unknown_message = json.dumps({"type": "unknown_type", "value": "test"})
        mock_ws = mock_websocket.return_value.mock_ws
        mock_ws.recv = AsyncMock(side_effect=[unknown_message, websockets.exceptions.ConnectionClosed(None, None)])

        await device.connect()
        await asyncio.sleep(0.1)

        await device.disconnect()

    async def test_process_message_bytes(self, device: Device, mock_websocket: AsyncMock) -> None:
        """Test processing message received as bytes."""
        state_message_bytes = json.dumps({"type": "state", "value": 0.5}).encode("utf-8")
        mock_ws = mock_websocket.return_value.mock_ws
        mock_ws.recv = AsyncMock(side_effect=[state_message_bytes, websockets.exceptions.ConnectionClosed(None, None)])

        await device.connect()
        await asyncio.sleep(0.1)

        # Verify state change was processed
        state_calls = [call for call in self.on_update_mock.call_args_list if isinstance(call[0][0], StateChange)]
        assert len(state_calls) > 0
        assert state_calls[0][0][0].state == 0.5  # noqa: PLR2004

        await device.disconnect()

    async def test_process_message_invalid_json(self, device: Device, mock_websocket: AsyncMock) -> None:
        """Test processing message with invalid JSON."""
        invalid_json = "not valid json {"
        mock_ws = mock_websocket.return_value.mock_ws
        mock_ws.recv = AsyncMock(side_effect=[invalid_json, websockets.exceptions.ConnectionClosed(None, None)])

        await device.connect()
        await asyncio.sleep(0.1)

        # Should handle the error gracefully
        await device.disconnect()


# Additional Unit Tests


@pytest.mark.asyncio
async def test_cancelled_receive_loop() -> None:
    """Test that CancelledError in receive loop is handled properly."""
    # Create a device with a mock session
    mock_session = AsyncMock()
    device = Device(
        host="192.168.1.100",
        initial_settings=[],
        initial_info_data=InformationData.from_device_dict({"lcu": "testdeviceid", "hwm": "1.0.0", "n": "test device"}),
        session=mock_session,
    )

    # Create a mock websocket that will be cancelled
    mock_ws = AsyncMock()
    mock_ws.close = AsyncMock()

    async def recv_that_gets_cancelled() -> str:
        await asyncio.sleep(10)  # This will be cancelled
        return ""

    mock_ws.recv = AsyncMock(side_effect=recv_that_gets_cancelled)

    # Start receive loop and immediately cancel it
    task = asyncio.create_task(device._receive_loop(mock_ws))
    await asyncio.sleep(0.01)
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_malformed_version_string() -> None:
    """Test that malformed version strings are handled gracefully."""
    assert not _is_version_compatible("not.a.version", "0.9.5")
    assert not _is_version_compatible("1.x.3", "0.9.5")
    assert not _is_version_compatible("", "0.9.5")
    assert not _is_version_compatible(None, "0.9.5")


@pytest.mark.asyncio
async def test_session_ownership() -> None:
    """Test that device tracks session ownership correctly."""
    # Create a device with a provided session - device doesn't own it
    external_session = AsyncMock()
    device = Device(
        host="192.168.1.100",
        initial_settings=[],
        initial_info_data=InformationData.from_device_dict({"lcu": "testdeviceid", "hwm": "1.0.0", "n": "test device"}),
        session=external_session,
    )
    await device.close()
    external_session.close.assert_not_called()
    assert not device._owns_session


@pytest.mark.asyncio
async def test_is_device_supported_missing_model() -> None:
    """Test is_device_supported with missing model."""
    supported, msg = Device.is_device_supported(None, "1.0.0")
    assert not supported
    assert msg == "Missing model information"


@pytest.mark.asyncio
async def test_is_device_supported_unsupported_model() -> None:
    """Test is_device_supported with unsupported model."""
    supported, msg = Device.is_device_supported("UNKNOWN-MODEL", "1.0.0")
    assert not supported
    assert msg == "Unsupported model: UNKNOWN-MODEL"


@pytest.mark.asyncio
async def test_is_device_supported_missing_version() -> None:
    """Test is_device_supported with missing firmware version."""
    supported, msg = Device.is_device_supported("WBD-01", None)
    assert not supported
    assert msg == "Missing firmware version"


@pytest.mark.asyncio
async def test_is_device_supported_incompatible_version() -> None:
    """Test is_device_supported with incompatible firmware version."""
    supported, msg = Device.is_device_supported("WBD-01", "0.9.4")
    assert not supported
    assert "Incompatible firmware version" in msg
    assert "0.9.4" in msg
    assert "0.9.5" in msg


@pytest.mark.asyncio
async def test_is_device_supported_valid() -> None:
    """Test is_device_supported with valid device."""
    supported, msg = Device.is_device_supported("WBD-01", "1.0.0")
    assert supported
    assert msg == ""


@pytest.mark.asyncio
async def test_initiate_device_creates_session() -> None:
    """Test initiate_device creates and manages session when none provided."""
    with (
        patch("sn2.device.Device._get_settings") as mock_settings,
        patch("sn2.device.Device._get_info") as mock_info,
        patch("aiohttp.ClientSession") as mock_session_class,
    ):
        mock_settings.return_value = []
        mock_info.return_value = InformationUpdate(
            InformationData.from_device_dict({"lcu": "testdeviceid", "hwm": "WBD-01", "n": "test device"})
        )
        mock_session_instance = AsyncMock()
        mock_session_class.return_value = mock_session_instance

        device = await Device.initiate_device(host="192.168.1.100")

        assert device._owns_session is True
        assert device.host == "192.168.1.100"
        mock_session_class.assert_called_once()


@pytest.mark.asyncio
async def test_initiate_device_uses_provided_session() -> None:
    """Test initiate_device uses provided session."""
    external_session = AsyncMock()
    with patch("sn2.device.Device._get_settings") as mock_settings, patch("sn2.device.Device._get_info") as mock_info:
        mock_settings.return_value = []
        mock_info.return_value = InformationUpdate(
            InformationData.from_device_dict({"lcu": "testdeviceid", "hwm": "WBD-01", "n": "test device"})
        )

        device = await Device.initiate_device(host="192.168.1.100", session=external_session)

        assert device._owns_session is False
        assert device._session == external_session


@pytest.mark.asyncio
async def test_initiate_device_failure_closes_created_session() -> None:
    """Test initiate_device closes session on failure when it created it."""
    with (
        patch("sn2.device.Device._get_settings") as mock_settings,
        patch("aiohttp.ClientSession") as mock_session_class,
    ):
        mock_settings.side_effect = RuntimeError("Failed to get settings")
        mock_session_instance = AsyncMock()
        mock_session_class.return_value = mock_session_instance

        with pytest.raises(DeviceInitializationError):
            await Device.initiate_device(host="192.168.1.100")

        # Verify session was closed
        mock_session_instance.close.assert_called_once()


@pytest.mark.asyncio
async def test_initiate_device_failure_keeps_external_session() -> None:
    """Test initiate_device doesn't close external session on failure."""
    external_session = AsyncMock()
    with patch("sn2.device.Device._get_settings") as mock_settings:
        mock_settings.side_effect = RuntimeError("Failed to get settings")

        with pytest.raises(DeviceInitializationError):
            await Device.initiate_device(host="192.168.1.100", session=external_session)

        # Verify session was NOT closed
        external_session.close.assert_not_called()


@pytest.mark.asyncio
async def test_send_command_not_connected() -> None:
    """Test send_command raises NotConnectedError when not connected."""
    mock_session = AsyncMock()
    device = Device(
        host="192.168.1.100",
        initial_settings=[],
        initial_info_data=InformationData.from_device_dict(
            {"lcu": "testdeviceid", "hwm": "WBD-01", "n": "test device"}
        ),
        session=mock_session,
    )

    with pytest.raises(NotConnectedError):
        await device.send_command({"type": "test"})


@pytest.mark.asyncio
async def test_update_setting_success() -> None:
    """Test update_setting successfully updates settings."""
    mock_session = AsyncMock()
    mock_response = Mock()
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)
    mock_response.raise_for_status = Mock()
    mock_session.post = Mock(return_value=mock_response)

    device = Device(
        host="192.168.1.100",
        initial_settings=[],
        initial_info_data=InformationData.from_device_dict(
            {"lcu": "testdeviceid", "hwm": "WBD-01", "n": "test device"}
        ),
        session=mock_session,
    )

    await device.update_setting({"disable_led": 1})

    mock_session.post.assert_called_once()
    call_args = mock_session.post.call_args
    assert "192.168.1.100:3000/settings" in call_args[0][0]
    assert call_args[1]["json"] == {"disable_led": 1}


@pytest.mark.asyncio
async def test_update_setting_failure() -> None:
    """Test update_setting handles failures."""
    mock_session = AsyncMock()
    mock_session.post = Mock(side_effect=RuntimeError("HTTP error"))

    device = Device(
        host="192.168.1.100",
        initial_settings=[],
        initial_info_data=InformationData.from_device_dict(
            {"lcu": "testdeviceid", "hwm": "WBD-01", "n": "test device"}
        ),
        session=mock_session,
    )

    with pytest.raises(RuntimeError, match="HTTP error"):
        await device.update_setting({"disable_led": 1})


@pytest.mark.asyncio
async def test_onoff_setting_enable() -> None:
    """Test OnOffSetting.enable() method."""
    mock_session = AsyncMock()
    mock_response = Mock()
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)
    mock_response.raise_for_status = Mock()
    mock_session.post = Mock(return_value=mock_response)

    device = Device(
        host="192.168.1.100",
        initial_settings=[],
        initial_info_data=InformationData.from_device_dict(
            {"lcu": "testdeviceid", "hwm": "WBD-01", "n": "test device"}
        ),
        session=mock_session,
    )

    setting = OnOffSetting(name="Test Setting", param_key="test_param", current=0, on_value=1, off_value=0)

    await setting.enable(device)

    mock_session.post.assert_called_once()
    call_args = mock_session.post.call_args
    assert call_args[1]["json"] == {"test_param": 1}


@pytest.mark.asyncio
async def test_onoff_setting_disable() -> None:
    """Test OnOffSetting.disable() method."""
    mock_session = AsyncMock()
    mock_response = Mock()
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)
    mock_response.raise_for_status = Mock()
    mock_session.post = Mock(return_value=mock_response)

    device = Device(
        host="192.168.1.100",
        initial_settings=[],
        initial_info_data=InformationData.from_device_dict(
            {"lcu": "testdeviceid", "hwm": "WBD-01", "n": "test device"}
        ),
        session=mock_session,
    )

    setting = OnOffSetting(name="Test Setting", param_key="test_param", current=1, on_value=1, off_value=0)

    await setting.disable(device)

    mock_session.post.assert_called_once()
    call_args = mock_session.post.call_args
    assert call_args[1]["json"] == {"test_param": 0}


@pytest.mark.asyncio
async def test_async_context_manager() -> None:
    """Test Device as async context manager."""
    mock_session = AsyncMock()
    mock_session.close = AsyncMock()

    device = Device(
        host="192.168.1.100",
        initial_settings=[],
        initial_info_data=InformationData.from_device_dict(
            {"lcu": "testdeviceid", "hwm": "WBD-01", "n": "test device"}
        ),
        session=mock_session,
        owns_session=True,
    )

    async with device as d:
        assert d == device

    # Verify close was called (which closes session when owned)
    mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_information_data_missing_lcu() -> None:
    """Test InformationData.from_device_dict with missing lcu."""
    with pytest.raises(ValueError, match="lcu \\(unique id\\) cannot be None"):
        InformationData.from_device_dict({"hwm": "WBD-01", "n": "test device"})


@pytest.mark.asyncio
async def test_information_data_missing_hwm() -> None:
    """Test InformationData.from_device_dict with missing hwm."""
    with pytest.raises(ValueError, match="hwm \\(model\\) cannot be None"):
        InformationData.from_device_dict({"lcu": "testdeviceid", "n": "test device"})


@pytest.mark.asyncio
async def test_information_data_missing_name() -> None:
    """Test InformationData.from_device_dict with missing name."""
    with pytest.raises(ValueError, match="n \\(name\\) cannot be None"):
        InformationData.from_device_dict({"lcu": "testdeviceid", "hwm": "WBD-01"})


@pytest.mark.asyncio
async def test_version_compatible_with_none_min_version() -> None:
    """Test _is_version_compatible with None min_version."""
    with pytest.raises(ValueError, match="min_version needs to be set"):
        _is_version_compatible("1.0.0", None)  # pyright: ignore[reportArgumentType]


@pytest.mark.asyncio
async def test_version_compatible_greater_version() -> None:
    """Test _is_version_compatible when version is greater."""
    assert _is_version_compatible("1.1.0", "1.0.0") is True
    assert _is_version_compatible("2.0.0", "1.0.0") is True


@pytest.mark.asyncio
async def test_version_compatible_lesser_version() -> None:
    """Test _is_version_compatible when version is less than min."""
    assert _is_version_compatible("0.9.0", "1.0.0") is False
    assert _is_version_compatible("1.0.0", "1.1.0") is False


@pytest.mark.asyncio
async def test_version_compatible_equal_version() -> None:
    """Test _is_version_compatible when versions are equal."""
    assert _is_version_compatible("1.0.0", "1.0.0") is True
    assert _is_version_compatible("0.9.5", "0.9.5") is True


@pytest.mark.asyncio
async def test_version_compatible_with_prerelease() -> None:
    """Test _is_version_compatible with pre-release versions."""
    assert _is_version_compatible("1.0.0-beta.2", "1.0.0") is True
    assert _is_version_compatible("1.0.0+build123", "1.0.0") is True


@pytest.mark.asyncio
async def test_version_compatible_different_lengths() -> None:
    """Test _is_version_compatible with different version component lengths."""
    assert _is_version_compatible("1.0", "1.0.0") is True
    assert _is_version_compatible("1.0.0", "1.0") is True


@pytest.mark.asyncio
async def test_emit_callback_exception() -> None:
    """Test _emit handles callback exceptions gracefully."""

    def failing_callback(_event: UpdateEvent) -> None:
        raise RuntimeError("Callback failed")  # noqa: EM101, TRY003

    mock_session = AsyncMock()
    device = Device(
        host="192.168.1.100",
        initial_settings=[],
        initial_info_data=InformationData.from_device_dict(
            {"lcu": "testdeviceid", "hwm": "WBD-01", "n": "test device"}
        ),
        session=mock_session,
        on_update=failing_callback,
    )

    # Should not raise exception
    await device._emit(ConnectionStatus(connected=True))
