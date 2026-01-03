from dataclasses import dataclass
import queue
import struct
import threading
from typing import Callable, Any, Dict, List, Union


import httpx
from httpx_ws import connect_ws

@dataclass
class WSSubscription:
    _stop: Callable[[], None]

    def stop(self) -> None:
        self._stop()



class EMGeniusClient:
    endpoint: str
    app_name: str
    _client: httpx.Client

    def __init__(
        self,
        app_name: str = "EMGeniusPySDK/0.0.1",
        endpoint: str = "127.0.0.1:64209",
    ):
        self.endpoint = endpoint
        self.app_name = app_name
        self._client = httpx.Client()

    def get_connected_devices(self) -> str:
        result = self._client.get(
            f"http://{self.endpoint}/connections/get_connected_devices"
        )
        return result.json()

    def subscribe_emg_websocket(
        self,
        device: dict,
        callback: Callable[[str], None],
        *,
        receive_timeout_s: float = 0.5,
    ) -> WSSubscription:
        """
            Non-blocking for sync apps: starts a daemon thread that reads the websocket.
            callback(message) is invoked on that background thread.
            Call .stop() to shut down.
        """
        stop_event = threading.Event()

        address = device["address"]

        def run():

            def parse_binary_message(message: bytes) -> str:
                    """
                    Parses the binary websocket message (little-endian) and returns a dict.

                    Returns (for type == 0):
                    {
                        "type": 0,
                        "timestamp": <float>,
                        "number_of_samples": <int>,
                        "channels": {
                            0: [float, ...],
                            1: [float, ...],
                            ...
                        }
                    }

                    For other types:
                    {
                        "type": <int>,
                        "timestamp": <float>,
                        "number_of_samples": <int>,
                        "channels": {}
                    }
                    """
                    offset = 0

                    (msg_type,) = struct.unpack_from("<I", message, offset); offset += 4
                    (timestamp,) = struct.unpack_from("<d", message, offset); offset += 8
                    (number_of_samples,) = struct.unpack_from("<I", message, offset); offset += 4

                    out: Dict[str, Any] = {
                        "type": msg_type,
                        "timestamp": timestamp,
                        "number_of_samples": number_of_samples,
                        "channels": {},
                    }

                    if msg_type != 0:
                        # Not EMG payload in your original code
                        return out

                    number_of_channels = (
                        device["device_settings"]["connection_info"]["emg_ic"]["number_of_active_channels"]
                    )

                    # Read per-channel float32 samples
                    channels: Dict[int, List[float]] = {}
                    for ch in range(number_of_channels):
                        fmt = f"<{number_of_samples}f"
                        samples = list(struct.unpack_from(fmt, message, offset))
                        offset += 4 * number_of_samples
                        channels[ch] = samples

                    out["channels"] = channels
                    return out

            with httpx.Client() as client:
                with connect_ws(
                    f"ws://{self.endpoint}/ws/{address}?dtype=emg&app_name={self.app_name}",
                    client,
                ) as ws:
                    while not stop_event.is_set():
                        try:
                            msg = ws.receive_bytes()
                            msg = parse_binary_message(msg)
                        except queue.Empty:
                            continue
                        callback(msg)

        t = threading.Thread(target=run, name="emg-ws-reader", daemon=True)
        t.start()

        def stop():
            stop_event.set()
            t.join(timeout=2.0)

        return WSSubscription(_stop=stop)
