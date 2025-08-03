import logging
import struct
from typing import Generator, Tuple

from Utils.constants import FRAME_HEADER_SIZE, FRAME_PAYLOAD_SIZE

logger = logging.getLogger("infra_logger." + __name__)


class FrameTransmitter:
    def __init__(self, system_clock, frames_path: str) -> None:
        self.__frames_path = frames_path
        self.__system_clock = system_clock

    def start_frame_transmission(self) -> Generator[bytes, None, None]:
        with open(self.__frames_path, "rb") as f:
            while True:
                header_bytes = f.read(FRAME_HEADER_SIZE)
                payload_bytes = f.read(FRAME_PAYLOAD_SIZE)
                if len(header_bytes) < FRAME_HEADER_SIZE or len(payload_bytes) < FRAME_PAYLOAD_SIZE:
                    logger.info(f"Finished transmitting frames from: {self.__frames_path}")
                    break

                try:
                    address, transmission_time = struct.unpack('<II', header_bytes)
                except struct.error as e:
                    logger.error(f"Failed to unpack header at position {f.tell() - FRAME_HEADER_SIZE}: {e}")
                    break

                header_bytes = struct.pack('<I', address)

                self.__system_clock.wait_until(transmission_time)

                yield header_bytes + payload_bytes
