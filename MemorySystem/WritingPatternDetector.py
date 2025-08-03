import logging
import getpass
from datetime import date
from typing import Callable

from Utils import loggers


logger = logging.getLogger("infra_logger." + __name__)
detector_logger = logging.getLogger("detector_logger")


class FailureDetectedError(Exception):
    pass


def generate_failure_header(threshold: int, delta: int, start_addr: int) -> str:
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
    failure_body = ""

    for i, mw in enumerate(memory_writes):
        failure_body = (failure_body +
                        f"    # memory write {i + 1}\n"
                        f"    memory_write:\n"
                        f"      Start_time: {mw['Start_time']} # start time sec\n"
                        f"      Duration: {mw['Duration']} # duration sec\n"
                        f"      Start_address: 0x{mw['Start_address']:08X} # start_address\n"
                        f"      N: {mw['N']} # contiguous frames\n\n")

    return failure_body


def create_failure_logger(pattern_info) -> Callable[[], None]:
    def log_failure():
        log_header = generate_failure_header(pattern_info["threshold"], pattern_info["delta"],
                                             pattern_info["memory_writes"][0]["Start_address"])
        log_body = generate_failure_body(pattern_info["memory_writes"])

        detector_logger.error(log_header + log_body)

    return log_failure


class WritingPatternDetector:
    def __init__(self, system_clock, threshold: int, delta: int,
                 error_log_callback: Callable[[], None], log_path: str) -> None:
        self.__threshold = threshold
        self.__delta = delta
        self.__current_memory_write = 0
        self.__error_log_callback = error_log_callback
        self.__system_clock = system_clock
        loggers.setup_detector_logger(log_path)

    def process_incoming_frame(self, frame) -> None:  # TODO: what to do with frame?
        if self.__system_clock.now <= self.__delta and self.__current_memory_write + 1 >= self.__threshold:
            self.__report()
            raise FailureDetectedError("Writing pattern failure detected.")

    def notify_mw_tx_end(self) -> None:
        self.__current_memory_write += 1

    def __report(self) -> None:
        self.__error_log_callback()
