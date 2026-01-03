import sys
import unittest
from pathlib import Path
from unittest import mock

from src.emgeniussdk.client import EMGeniusClient
from src.emgeniussdk import client


class TestEMGeniusClient(unittest.TestCase):
    def test_get_connected_devices_sync(self) -> None:
        sdk = EMGeniusClient()
        sdk._client = mock.Mock()

        response = mock.Mock()
        response.json.return_value = ["device-a", "device-b"]
        sdk._client.get.return_value = response

        result = sdk.get_connected_devices()

        sdk._client.get.assert_called_once_with(
            f"{sdk.endpoint}/connections/get_connected_devices"
        )
        self.assertEqual(result, ["device-a", "device-b"])

    def test_connect_emg_websocket_invokes_callback(self) -> None:
        sdk = EMGeniusClient(app_name="TestApp", endpoint="http://example.local")
        sdk._client = mock.Mock()

        messages = []

        def callback(message: str) -> None:
            messages.append(message)

        ws = mock.Mock()
        ws.receive_text.side_effect = ["hello", RuntimeError("stop")]

        ws_context = mock.Mock()
        ws_context.__enter__ = mock.Mock(return_value=ws)
        ws_context.__exit__ = mock.Mock(return_value=False)

        with mock.patch.object(client, "connect_ws", return_value=ws_context) as connect_ws:
            with self.assertRaises(RuntimeError):
                sdk.connect_emg_websocket("127.0.0.1:9999", callback)

        connect_ws.assert_called_once_with(
            "ws://127.0.0.1:9999/ws/127.0.0.1:9999?dtype=emg&app_id=TestApp",
            sdk._client,
        )
        self.assertEqual(messages, ["hello"])


class TestEMGeniusClientAsync(unittest.IsolatedAsyncioTestCase):
    async def test_get_connected_devices_async_context(self) -> None:
        sdk = EMGeniusClient()
        sdk._client = mock.Mock()

        response = mock.Mock()
        response.json.return_value = ["device-x"]
        sdk._client.get.return_value = response

        result = sdk.get_connected_devices()

        sdk._client.get.assert_called_once_with(
            f"{sdk.endpoint}/connections/get_connected_devices"
        )
        self.assertEqual(result, ["device-x"])
