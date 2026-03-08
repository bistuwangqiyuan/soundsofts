"""TCP client for real-time data streaming from LabVIEW B/S acquisition."""

from __future__ import annotations

import socket
import struct
from dataclasses import dataclass

import numpy as np


@dataclass
class StreamPacket:
    """One packet from the LabVIEW TCP data stream."""
    timestamp: float
    position_mm: float
    force_n: float
    waveform_length: int
    waveform: np.ndarray


class StreamClient:
    """Connect to LabVIEW real-time TCP data stream.

    Protocol: Each packet consists of:
    - 4 bytes: packet length (uint32, big-endian)
    - 8 bytes: timestamp (float64)
    - 4 bytes: position (float32, mm)
    - 4 bytes: force (float32, N)
    - 4 bytes: waveform_length (uint32)
    - N*4 bytes: waveform samples (float32 array)
    """

    HEADER_SIZE = 24  # 4 + 8 + 4 + 4 + 4

    def __init__(self, host: str = "127.0.0.1", port: int = 5000) -> None:
        self.host = host
        self.port = port
        self._socket: socket.socket | None = None

    def connect(self) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self.host, self.port))

    def disconnect(self) -> None:
        if self._socket:
            self._socket.close()
            self._socket = None

    def read_packet(self) -> StreamPacket:
        """Read one complete packet from the stream."""
        assert self._socket is not None

        header = self._recv_exact(self.HEADER_SIZE)
        pkt_len, timestamp, position, force, wf_len = struct.unpack(">IdffI", header)

        wf_bytes = self._recv_exact(wf_len * 4)
        waveform = np.frombuffer(wf_bytes, dtype=np.float32)

        return StreamPacket(
            timestamp=timestamp,
            position_mm=position,
            force_n=force,
            waveform_length=wf_len,
            waveform=waveform,
        )

    def _recv_exact(self, n: int) -> bytes:
        """Receive exactly n bytes from the socket."""
        assert self._socket is not None
        data = b""
        while len(data) < n:
            chunk = self._socket.recv(n - len(data))
            if not chunk:
                raise ConnectionError("Connection closed")
            data += chunk
        return data

    def __enter__(self) -> StreamClient:
        self.connect()
        return self

    def __exit__(self, *args: object) -> None:
        self.disconnect()
