import logging
from typing import Any, List

from MemorySystem.WritingPatternDetector import FailureDetectedError

logger = logging.getLogger("infra_logger." + __name__)


class MemorySystem:
    """
    Simulates a memory system by coordinating the FrameTransmitter and the WritingPatternDetector

    This class is responsible for orchestrating the transfer of frames (via the transmitter)
    and the detection of failures in writing patterns (via the detector), according to the
    provided pattern descriptor.
    Acts as an interface between the FrameTransmitter and the WritingPatternDetector
    """
    def __init__(self, transmitter: Any, detector: Any, pattern_descriptor: List[int]) -> None:
        """
        Initializes the MemorySystem with the transmitter and the detector.

        Args:
            transmitter (Any): An object responsible for providing frames
            (should implement `start_frame_transmission()`).
            detector (Any): An object responsible for detecting failures
            (should implement `process_incoming_frame()` and `notify_mw_tx_end()`).
            pattern_descriptor (List[int]):
            List indicating the number of frames in each memory write of the current pattern.
        """
        self.__transmitter = transmitter
        self.__detector = detector
        self.__pattern_descriptor = pattern_descriptor

    def run(self) -> None:
        """
        Runs the memory system simulation for the current writing pattern.

        Transmits frames one by one to the detector.
        Notifies the detector on completion of a memory write.
        Handles unexpected end-of-transmission and writing pattern failures raised by the WritingPatternDetector.

        Logs:
            Information about transmission stages,
            unexpected end-of-transmission, and writing pattern failures
        """
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
        