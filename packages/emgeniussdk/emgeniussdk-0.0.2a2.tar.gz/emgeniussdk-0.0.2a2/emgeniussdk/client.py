from typing import Callable

import httpx
from httpx_ws import connect_ws


class EMGeniusClient:
    endpoint: str
    app_name: str
    _client: httpx.Client

    def __init__(
        self,
        app_name: str = "EMGeniusPySDK/0.0.1",
        endpoint: str = "http://127.0.0.1:64209",
    ):
        self.endpoint = endpoint
        self.app_name = app_name
        self._client = httpx.Client()

    def get_connected_devices(self) -> str:
        result = self._client.get(
            f"{self.endpoint}/connections/get_connected_devices"
        )
        return result.json()

    def connect_emg_websocket(self, address: str, callback: Callable[[str], None]):
        with connect_ws(
            f"ws://{address}/ws/" + address + "?dtype=emg&app_id=" + self.app_name,
            self._client,
        ) as ws:
            while True:
                message = ws.receive_text()
                callback(message)
