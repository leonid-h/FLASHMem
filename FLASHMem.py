import os
import sys
import logging
from Utils import loggers
from datetime import datetime

from Utils.constants import FAILURE_LOGS_FOLDER
from Utils.PatternGenerator import safe_iterate_patterns, BadConfigError, PatternGenerator
from MemorySystem.SystemClock import SystemClock
from MemorySystem.MemorySystem import MemorySystem
from MemorySystem.FrameTransmitter import FrameTransmitter
from MemorySystem.WritingPatternDetector import WritingPatternDetector, create_failure_logger

loggers.setup_infra_logger()
logger = logging.getLogger("infra_logger." + __name__)


def remove_failure_log_file_if_empty(file_path: str) -> None:
    if os.path.exists(file_path) and os.path.getsize(file_path) == 0:
        os.remove(file_path)


def run_simulation(writing_pattern_generator: PatternGenerator) -> None:
    for threshold, delta, patter_descriptor, frames_bin_path in safe_iterate_patterns(writing_pattern_generator):
        current_pattern = writing_pattern_generator.current_pattern
        now = datetime.now()
        execution_time = now.strftime("__%d_%m_%Y__%H_%M_%S.txt")
        failure_log_path = FAILURE_LOGS_FOLDER + "/" + current_pattern["name"] + execution_time

        system_clock = SystemClock()
        failure_logger = create_failure_logger(current_pattern)

        frame_transmitter = FrameTransmitter(system_clock, frames_bin_path)
        writing_pattern_detector = WritingPatternDetector(system_clock, threshold, delta,
                                                          failure_logger, failure_log_path)
        try:
            writing_pattern_detector.init_failure_logger()
        except (FileNotFoundError, PermissionError, OSError) as er:
            logger.critical(f"Initializing failure logger: {er}")
            raise

        memory_system = MemorySystem(frame_transmitter, writing_pattern_detector, patter_descriptor)

        try:
            memory_system.run()
        except (FileNotFoundError, PermissionError, OSError) as er:
            logger.critical(f"Error opening/reading frames file: {er}")
            raise

        writing_pattern_detector.close_failure_logger()

        try:
            remove_failure_log_file_if_empty(failure_log_path)
        except (FileNotFoundError, PermissionError, OSError) as er:
            logger.critical(f"Error removing an empty failure log file: {er}")
            raise
        # memory reports statistics
        # memory_system.report()


if __name__ == "__main__":

    config_file_path = "PatternConfigs/InputConfigs/SystemFailureFlows/failure_pattern_after_successful.yaml"
    # TODO: make this dynamic

    pattern_generator = PatternGenerator(config_file_path)

    try:
        pattern_generator.init()
    except BadConfigError as err:
        logger.critical(f"Configuration Error: {err}")
        sys.exit(1)

    try:
        run_simulation(pattern_generator)
    except (FileNotFoundError, PermissionError, OSError) as e:
        logger.critical(f"FS error occurred: {e}")
        sys.exit(1)
