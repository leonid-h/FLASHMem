import struct
import logging
import getpass
from datetime import date
from typing import Callable
from enum import Enum

from Utils import loggers
from Utils.constants import FLASH_FRAME_TOTAL_SIZE


infra_logger = logging.getLogger("infra_logger." + __name__)
detector_logger = logging.getLogger("detector_logger")


class Status(Enum):
    """
    An enum class used to indicate memory system run completion status
    """
    SUCCESS = 0
    FAILURE = 1


class FailureDetectedError(Exception):
    """
    Custom exception raised when a writing pattern failure is detected.
    """
    pass


def generate_failure_header(threshold: int, delta: int, start_addr: int) -> str:
    """
    Generates a header for the system failure report.

    Args:
        threshold (int): The max allowed number of writes in the pattern (THRESHOLD).
        delta (int): The allowed time window (DELTA) in seconds.
        start_addr (int): The start address of the failed writing pattern.

    Returns:
        str: The formatted report header as a string.
    """
    return (
        f"report type: system failure\n"
        f"user: {getpass.getuser()}\n"
        f"date: {date.today().strftime('%d/%m/%Y')}\n\n"
        f"SYSTEM_FAILURE_START_ADDRESS: 0x{start_addr:08X} # start address of the writing pattern\n"
        f"THRESHOLD: {threshold} # number of writes\n"
        f"DELTA: {delta} # sec\n\n"
        "system_failure_writing_pattern:\n\n"
    )


def generate_failure_body(memory_writes: list) -> str:
    """
    Generates the body of the system failure report, listing all the memory writes of the failed pattern.

    Args:
        memory_writes (list): List of dictionaries describing each memory write.

    Returns:
        str: The formatted report body as a string.
    """
    failure_body = []

    for i, mw in enumerate(memory_writes):
        failure_body.append(f"    # memory write {i + 1}\n"
                            f"    memory_write:\n"
                            f"      Start_time: {mw['Start_time']} # start time sec\n"
                            f"      Duration: {mw['Duration']} # duration sec\n"
                            f"      Start_address: 0x{mw['Start_address']:08X} # start_address\n"
                            f"      N: {mw['N']} # contiguous frames\n\n")

    return ''.join(failure_body)


def create_failure_logger(pattern_info) -> Callable[[], None]:
    """
    Creates a closure that logs a failure report using the detector logger.

    Args:
        pattern_info (dict): Dictionary that contains the pattern configuration
                             (threshold, delta, memory_writes).

    Returns:
        Callable[[], None]: A function that, when called, logs the pattern failure.
    """
    def log_failure():
        log_header = generate_failure_header(pattern_info["threshold"], pattern_info["delta"],
                                             pattern_info["memory_writes"][0]["Start_address"])
        log_body = generate_failure_body(pattern_info["memory_writes"])

        detector_logger.error(log_header + log_body)

    return log_failure


class WritingPatternDetector:
    """
    Detects and logs failures in writing patterns.

    Monitors the sequence of transmitted frames one by one and checks if the configured
    failure condition is met. If so, logs the failure and raises an error.
    """
    def __init__(self, system_clock, base_address: int, threshold: int, delta: int,
                 error_log_callback: Callable[[], None], log_path: str) -> None:
        """
        Initialize the WritingPatternDetector.

        Args:
            system_clock: The simulation clock object to track simulated time.
            threshold (int): The max allowed number of writes in the pattern.
            delta (int): The allowed time window for failure (in seconds).
            error_log_callback (Callable[[], None]): Callback to log a pattern failure.
            log_path (str): Path to the file where a pattern failure is logged.
        """
        self.__threshold_addr = (base_address + threshold - 1) * FLASH_FRAME_TOTAL_SIZE
        self.__delta = delta
        self.__previous_memory_write_end = False
        self.__error_log_callback = error_log_callback
        self.__system_clock = system_clock
        self.__log_path = log_path
        self.__status = Status.SUCCESS
        self.__frames_to_be_written = []
        self.__frames_written = 0

    def init_failure_logger(self) -> None:
        """
        Initializes the detector logger to log failures to the log file.
        """
        loggers.setup_detector_logger(self.__log_path)

    @staticmethod
    def close_failure_logger() -> None:
        """
        Closes all file handlers of the detector logger and clears the handlers.
        """
        for handler in detector_logger.handlers:
            handler.close()
        detector_logger.handlers.clear()

    def process_incoming_frame(self, frame: bytes) -> None:  # TODO: what to do with frame?
        """
        Processes an incoming frame and checks if the failure condition is met.

        Args:
            frame (bytes): The frame data.

        Raises:
            FailureDetectedError: If the failure condition is detected.
        """
        if self.__previous_memory_write_end:
            self.__write_frames_to_flash()
            self.__previous_memory_write_end = False

        frame_address = struct.unpack('<I', frame[:4])[0]

        if self.__system_clock.now <= self.__delta and frame_address >= self.__threshold_addr:
            self.__status = Status.FAILURE
            self.__report()
            raise FailureDetectedError("Writing pattern failure detected.")

        self.__frames_to_be_written.append(frame)

    def notify_mw_tx_end(self) -> None:
        """
        Notifies the detector of the memory write transmission end.

        Increments the internal memory write counter.
        """
        self.__previous_memory_write_end = True

    def notify_pattern_tx_end(self) -> None:
        if self.__status != Status.FAILURE:
            self.__write_frames_to_flash()

    def print_statistics(self) -> None:
        """
        Logs memory system run statistics using the infra logger.
        """
        infra_logger.info(f"LAST TRANSMISSION TIME: {self.__system_clock.now}")
        infra_logger.info(f"TOTAL FRAME COUNT IN FLASH: {self.__frames_written}")
        infra_logger.info(f"AVERAGE SPEED WITH HTATs: %.2f", self.__frames_written/self.__system_clock.now)
        if self.__status == Status.FAILURE:
            infra_logger.error(f"STATUS: {self.__status.name}")
        else:
            infra_logger.info(f"STATUS: {self.__status.name}")

    def __report(self) -> None:
        """
        Logs the failure using the error log callback.
        """
        self.__error_log_callback()

    def __write_frames_to_flash(self):
        self.__frames_written += len(self.__frames_to_be_written)
        self.__frames_to_be_written.clear()
