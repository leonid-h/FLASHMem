import sys
import logging
from Utils import loggers

from Utils.PatternGenerator import safe_iterate_patterns, BadConfigError, PatternGenerator
from MemorySystem.SystemClock import SystemClock
from MemorySystem.MemorySystem import MemorySystem
from MemorySystem.FrameTransmitter import FrameTransmitter
from MemorySystem.WritingPatternDetector import WritingPatternDetector, create_failure_logger

loggers.setup_infra_logger()
logger = logging.getLogger("infra_logger." + __name__)

if __name__ == "__main__":

    config_file_path = "PatternConfigs/InputConfigs/SystemFailureFlows/failure_pattern_after_successful.yaml"  # TODO: make this dynamic
    frames_folder_path = "PatternConfigs/Frames"  # TODO: make this dynamic
    failure_log_path = "Logs/log.txt" # TODO: make separate logs for each system failure

    pattern_generator = PatternGenerator(config_file_path, frames_folder_path)

    try:
        pattern_generator.init()
    except BadConfigError as err:
        logger.critical(f"Configuration Error: {err}")
        sys.exit(1)

    for threshold, delta, patter_descriptor, frames_bin_path in safe_iterate_patterns(pattern_generator):

        system_clock = SystemClock()
        failure_logger = create_failure_logger(pattern_generator.current_pattern)

        frame_transmitter = FrameTransmitter(system_clock, frames_bin_path)
        writing_pattern_detector = WritingPatternDetector(system_clock, threshold, delta,
                                                          failure_logger, failure_log_path)

        memory_system = MemorySystem(frame_transmitter, writing_pattern_detector, patter_descriptor)

        try:
            memory_system.run()
        except (FileNotFoundError, PermissionError, OSError) as err:
            logger.critical(f"Error opening/reading frames file: {err}")
            sys.exit(1)

        # memory reports statistics
        # memory_system.report()
