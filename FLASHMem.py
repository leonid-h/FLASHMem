import sys
import logging
from Utils import loggers

from Utils.PatternGenerator import safe_iterate_patterns, BadConfigError, PatternGenerator
from MemorySystem.MemorySystem import MemorySystem
from MemorySystem.FrameTransmitter import FrameTransmitter
from MemorySystem.WritingPatternDetector import WritingPatternDetector

loggers.setup_infra_logger()
logger = logging.getLogger("infra_logger." + __name__)

if __name__ == "__main__":

    config_file_path = "PatternConfigs/InputConfigs/SuccessFlows/successful_patterns_combined.yaml"  # TODO: make this dynamic
    frames_folder_path = "PatternConfigs/Frames"  # TODO: make this dynamic

    pattern_generator = PatternGenerator(config_file_path, frames_folder_path)

    try:
        pattern_generator.init()
    except BadConfigError as err:
        logger.error(f"Configuration Error: {err}")
        sys.exit(1)

    for threshold, delta, patter_descriptor, frames_bin_path in safe_iterate_patterns(pattern_generator):

        # Calls FrameTransmitter: takes FRAMES.bin file path, parses it and stores the frames
        frame_transmitter = FrameTransmitter(frames_bin_path)
        writing_pattern_detector = WritingPatternDetector(threshold, delta)

        memory_system = MemorySystem(frame_transmitter, writing_pattern_detector, patter_descriptor)

        # transmitter transmits the frames to wp_detector on by one
        # wp_detector detects failures or writes frames to the NAND
        try:
            memory_system.run()
        except (FileNotFoundError, PermissionError, OSError) as err:
            logger.error(f"Error opening/reading frames file: {err}")
            sys.exit(1)
        # memory reports statistics
        # memory_system.report()
