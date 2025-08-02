import logging

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
                    logger.info(f"transferred_frame at tx time: {transmission_time}")
                # notify detector - end of memory write transmission
                # self.__detector.recive_frame(transmission_time, frame)
            except StopIteration:
                logger.warning("Unexpected end of memory write transmission")
                break

            logger.info(f'finished transferring: {memory_write_len} frames')
