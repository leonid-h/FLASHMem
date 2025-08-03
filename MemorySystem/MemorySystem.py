import logging
from typing import Any, List

from MemorySystem.WritingPatternDetector import FailureDetectedError

logger = logging.getLogger("infra_logger." + __name__)


class MemorySystem:

    def __init__(self, transmitter: Any, detector: Any, pattern_descriptor: List[int]) -> None:
        self.__transmitter = transmitter
        self.__detector = detector
        self.__pattern_descriptor = pattern_descriptor

    def run(self) -> None:
        transmission_channel = self.__transmitter.start_frame_transmission()

        logger.info(f"System starts frame transmission")
        for memory_write_len in self.__pattern_descriptor:
            try:
                for frame in range(memory_write_len):
                    frame = next(transmission_channel)
                    self.__detector.process_incoming_frame(frame)
                self.__detector.notify_mw_tx_end()
            except StopIteration:
                logger.warning("Unexpected end of memory write transmission")
                break
            except FailureDetectedError as err:
                logger.error(f"Transmission aborted: {err}")
                break

            logger.info(f'finished transferring: {memory_write_len} frames')
        logger.info(f"Writing pattern processing complete, in case of failure, check log")
        