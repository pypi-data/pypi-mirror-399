
import asyncio
import struct
import random
import logging
from typing import Optional, Tuple
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class UdpTrackerProtocol(asyncio.DatagramProtocol):
    """AsyncIO Protocol for UDP Tracker communication."""

    def __init__(self):
        self.transport = None
        self.response_future = asyncio.get_running_loop().create_future()

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data: bytes, addr: Tuple[str, int]):
        if not self.response_future.done():
            self.response_future.set_result(data)

    def error_received(self, exc):
        if not self.response_future.done():
            self.response_future.set_exception(exc)

    def connection_lost(self, exc):
        if not self.response_future.done():
            self.response_future.set_exception(exc or Exception("Connection lost"))

    def send(self, data: bytes):
        if self.transport:
            self.transport.sendto(data)

    def reset_future(self):
        """Reset future for next response."""
        self.response_future = asyncio.get_running_loop().create_future()


class UdpTrackerClient:
    """BitTorrent UDP Tracker Protocol Client (BEP 15)."""

    MAGIC_CONSTANT = 0x41727101980

    def __init__(self, timeout: float = 3.0):
        self.timeout = timeout

    async def announce(self, tracker_url: str, info_hash: bytes) -> Tuple[int, int, bool, Optional[str]]:
        """
        Query UDP tracker for seeder/leecher count.

        Args:
            tracker_url: UDP tracker URL (e.g., udp://tracker.opentrackr.org:1337)
            info_hash: 20-byte info hash

        Returns:
            (seeders, leechers, success, error_message)
        """
        # Parse URL
        try:
            parsed = urlparse(tracker_url)
            host = parsed.hostname
            port = parsed.port or 80
            if not host:
                return 0, 0, False, "Invalid hostname"
        except Exception as e:
            return 0, 0, False, f"URL parse error: {e}"

        transport = None
        try:
            # 1. Connect
            loop = asyncio.get_running_loop()
            transport, protocol = await asyncio.wait_for(
                loop.create_datagram_endpoint(
                    lambda: UdpTrackerProtocol(),
                    remote_addr=(host, port)
                ),
                timeout=self.timeout
            )

            try:
                # -------------------------------------------------------------
                # Step 1: Send Connect Request
                # -------------------------------------------------------------
                trans_id = random.getrandbits(32)
                # Format: magic_constant (8 bytes), action (4 bytes), trans_id (4 bytes)
                connect_req = struct.pack("!QII", self.MAGIC_CONSTANT, 0, trans_id)
                protocol.send(connect_req)

                # Wait for Connect Response
                # Format: action (4), trans_id (4), connection_id (8)
                data = await asyncio.wait_for(protocol.response_future, timeout=self.timeout)
                protocol.reset_future()

                if len(data) < 16:
                     return 0, 0, False, "Truncated connect response"

                action, res_trans_id, conn_id = struct.unpack("!IIQ", data[:16])

                # Check for Error Action (3)
                if action == 3:
                     # Error message is remaining bytes
                    error_msg = data[8:].decode("utf-8", errors="ignore")
                    return 0, 0, False, f"Tracker Error: {error_msg}"

                if res_trans_id != trans_id:
                     return 0, 0, False, "Transaction ID mismatch (connect)"

                # -------------------------------------------------------------
                # Step 2: Send Announce Request
                # -------------------------------------------------------------
                trans_id = random.getrandbits(32)
                peer_id = b"-TC0100-" + bytes([random.randint(0, 255) for _ in range(12)])
                key = random.getrandbits(32)

                # Action=1 (Announce)
                # Format:
                #  conn_id (8), action (4), trans_id (4), info_hash (20), peer_id (20),
                #  downloaded (8), left (8), uploaded (8), event (4), ip (4), key (4), num_want (4), port (2)
                announce_req = struct.pack(
                    "!QII20s20sQQQIIIiH",
                    conn_id, 1, trans_id, info_hash, peer_id,
                    0, 0, 0, 0, 0, key, -1, 6881
                )
                protocol.send(announce_req)

                # Wait for Announce Response
                # Format: action (4), trans_id (4), interval (4), leechers (4), seeders (4) ... peers
                data = await asyncio.wait_for(protocol.response_future, timeout=self.timeout)

                if len(data) < 20:
                     return 0, 0, False, "Truncated announce response"

                action, res_trans_id, interval, leechers, seeders = struct.unpack("!IIIII", data[:20])

                if action == 3: # Error
                    error_msg = data[8:].decode("utf-8", errors="ignore")
                    return 0, 0, False, f"Tracker Error: {error_msg}"

                if action == 1 and res_trans_id == trans_id:
                     return seeders, leechers, True, None

                return 0, 0, False, "Invalid announce response or transaction ID mismatch"

            finally:
                transport.close()

        except asyncio.TimeoutError:
            return 0, 0, False, "Timeout"
        except Exception as e:
            # logger.debug(f"UDP Tracker Error ({tracker_url}): {e}")
            return 0, 0, False, str(e)
