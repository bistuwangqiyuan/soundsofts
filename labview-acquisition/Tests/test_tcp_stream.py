"""Tests for tcp_stream module."""

from __future__ import annotations

import socket
import struct
import threading

import numpy as np
import pytest

from python_interface.tcp_stream import StreamClient, StreamPacket


def _run_server(port: int, send_packet: bytes) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("127.0.0.1", port))
        s.listen(1)
        conn, _ = s.accept()
        with conn:
            conn.sendall(send_packet)


def test_stream_client_read_packet() -> None:
    """Client receives one packet from a mock server."""
    wf = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    wf_len = len(wf)
    pkt_len = 24 + wf_len * 4
    payload = struct.pack(">IdffI", pkt_len, 12345.67, 10.5, 50.0, wf_len) + wf.tobytes()

    port = 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    server_thread = threading.Thread(target=_run_server, args=(port, payload))
    server_thread.start()

    client = StreamClient(host="127.0.0.1", port=port)
    client.connect()
    try:
        pkt = client.read_packet()
        assert pkt.timestamp == 12345.67
        assert pkt.position_mm == 10.5
        assert pkt.force_n == 50.0
        assert pkt.waveform_length == 3
        np.testing.assert_array_almost_equal(pkt.waveform, [1.0, 2.0, 3.0])
    finally:
        client.disconnect()
    server_thread.join(timeout=2)


def test_stream_client_context_manager() -> None:
    wf = np.array([0.0], dtype=np.float32)
    pkt_len = 24 + 4
    payload = struct.pack(">IdffI", pkt_len, 0.0, 0.0, 0.0, 1) + wf.tobytes()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    server_thread = threading.Thread(target=_run_server, args=(port, payload))
    server_thread.start()

    with StreamClient(host="127.0.0.1", port=port) as client:
        pkt = client.read_packet()
        assert pkt.waveform_length == 1
    server_thread.join(timeout=2)
