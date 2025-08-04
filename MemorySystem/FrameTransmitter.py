import logging
import struct
from typing import Generator

from Utils.constants import FRAME_HEADER_SIZE, FRAME_PAYLOAD_SIZE

logger = logging.getLogger("infra_logger." + __name__)


class FrameTransmitter:
    """
    Reads and transmits frames from a binary file according to simulated time.

    Responsible for reading frames from disk, timing frame transmission
    with the simulation clock, and yielding serialized frame data for processing.
    """
    def __init__(self, system_clock, frames_path: str) -> None:
        """
        Initializes the FrameTransmitter.

        Args:
            system_clock: The simulation clock object used to coordinate timing.
            frames_path (str): Path to the binary file containing the frames.
        """
        self.__frames_path = frames_path
        self.__system_clock = system_clock

    def start_frame_transmission(self) -> Generator[bytes, None, None]:
        """
        Reads and transmits frames from the binary file, yielding one frame at a time.

        Each frame consists of a header (contains address) and a payload.
        The function synchronizes with the simulation clock before yielding each frame.

        Yields:
            bytes: Serialized frame data (header + payload).

        Logs:
            - When all frames are transmitted or if an incomplete frame is encountered.
            - If a frame header cannot be unpacked due to file corruption or truncation.
        """
        with open(self.__frames_path, "rb") as f:
            while True:
                header_bytes = f.read(FRAME_HEADER_SIZE)
                payload_bytes = f.read(FRAME_PAYLOAD_SIZE)
                if len(header_bytes) < FRAME_HEADER_SIZE or len(payload_bytes) < FRAME_PAYLOAD_SIZE:
                    logger.info(f"Finished transmitting frames from: {self.__frames_path}")
                    break

                try:
                    address, transmission_time = struct.unpack('<If', header_bytes)
                except struct.error as e:
                    logger.error(f"Failed to unpack header at position {f.tell() - FRAME_HEADER_SIZE}: {e}")
                    break

                header_bytes = struct.pack('<I', address)

                self.__system_clock.wait_until(transmission_time)

                yield header_bytes + payload_bytes
