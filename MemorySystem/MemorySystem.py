import logging
from MemorySystem.WritingPatternDetector import FailureDetectedError

logger = logging.getLogger("infra_logger." + __name__)


class MemorySystem:

    def __init__(self, transmitter, detector, pattern_descriptor):
        self.__transmitter = transmitter
        self.__detector = detector
        self.__pattern_descriptor = pattern_descriptor

    def run(self) -> None:
        transmission_chanel = self.__transmitter.start_frame_transmission()

        logger.info(f"System starts frame transmission")
        for memory_write_len in self.__pattern_descriptor:
            try:
                for frame in range(memory_write_len):
                    transmission_time, frame = next(transmission_chanel)
                    self.__detector.process_incoming_frame(transmission_time, frame)
                self.__detector.notify_mw_tx_end()
            except StopIteration:
                logger.warning("Unexpected end of memory write transmission")
                break
            except FailureDetectedError as err:
                logger.error(f"Transmission aborted: {err}")
                break

            logger.info(f'finished transferring: {memory_write_len} frames')
        logger.info(f"Finished processing writing pattern")
        