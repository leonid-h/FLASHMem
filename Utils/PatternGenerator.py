import yaml
import logging
import struct
from typing import TypeVar, Generator, Iterable, Iterator

from Utils.constants import (FRAME_PAYLOAD_SIZE, FRAME_TOTAL_SIZE,
                             DATA_PATTERN, FRAMES_BIN_FILENAME, UINT32_MAX, FLOAT32_MAX)

logger = logging.getLogger("infra_logger." + __name__)
T = TypeVar('T')


def safe_iterate_patterns(pattern_generator_iter: Iterable[T]) -> Generator[T, None, None]:
    """
    Safely iterates over a pattern generator, yielding valid patterns and skipping erroneous patterns.

    Args:
        pattern_generator_iter (Iterable[T]): An iterable that yields patterns.

    Yields:
        T: The next pattern from the generator.

    Logs:
        Errors encountered during iteration (OSError, ValueError).
    """
    it = iter(pattern_generator_iter)
    while True:
        try:
            yield next(it)
        except StopIteration:
            break
        except (OSError, ValueError) as e:
            logger.error(f"Pattern skipped due to error: {e}")
            continue


class BadConfigError(Exception):
    """
    Custom exception raised in case there is a problem loading the configuration file.
    """
    pass


class PatternGenerator(Iterator[tuple[int, int, list, str]]):
    """
    Iterator that generates writing pattern and writes a bin frame file for each pattern.

    Attributes:
        __config_file_path (str): Path to the YAML configuration file.
        __patterns_iter (Iterator): Internal iterator that iterates patterns.
        __current_pattern (dict): The current pattern being processed.
    """

    def __init__(self, config_file_path: str) -> None:
        """
        Initializes the PatternGenerator with the specified config file.

        Args:
            config_file_path (str): Path to the YAML configuration file.
        """
        self.__config_file_path = config_file_path
        self.__patterns_iter = None
        self.__current_pattern = None

    def __iter__(self) -> 'PatternGenerator':  # returns self
        """
        Returns the iterator instance (self).

        Returns:
            PatternGenerator: The iterator instance.
        """
        return self

    def __next__(self) -> tuple[int, int, list, str]:
        """
        Calls self.__generate()

        Returns:
            tuple: (threshold, delta, pattern_descriptor, frames_bin_filename)
                - threshold (int): Pattern threshold parameter.
                - delta (int): Pattern delta parameter.
                - pattern_descriptor (list): Frame count per memory write.
                - frames_bin_filename (str): Output file path for generated frames.

        Raises:
              Errors raised by self._generate().
        """
        return self.__generate()

    @property
    def current_pattern(self) -> dict:
        """
        The current pattern being processed by the memory system.

        Returns:
            dict: The current pattern's configuration dictionary.
        """
        return self.__current_pattern

    def init(self) -> None:
        """
        Initializes the generator by loading and parsing the YAML config file.

        Raises:
            BadConfigError: If the config file is missing, empty, or invalid.
        """
        try:
            with open(self.__config_file_path, "r") as f:
                patterns = yaml.safe_load(f)
                if not patterns:
                    raise BadConfigError("Config file is empty.")
                self.__patterns_iter = iter(patterns["writing_patterns"])
                logger.info(f"Successfully loaded config file: {self.__config_file_path}")
        except FileNotFoundError:
            raise BadConfigError(f"Config file '{self.__config_file_path}' not found.")
        except yaml.YAMLError as err:
            raise BadConfigError(f"Error parsing YAML: {err}")

    @staticmethod
    def __get_frames(memory_write: dict) -> Generator[bytes, None, None]:
        """
        Generates all frames for a single memory write.

        Args:
            memory_write (dict): Dictionary that has the following keys:
             start time, duration, start address, and frame count.

        Yields:
            bytes: Serialized frame data (header(contains address and transmission time) + payload).

        Raises:
            ValueError: If frame header fields are out of range (4 byte unsigned integer).
        """

        def check_addr_overflow(value: int) -> None:
            if not (0 <= value <= UINT32_MAX):
                raise ValueError("Address out of range")

        def check_time_overflow(value: float) -> None:
            if not (0 <= value <= FLOAT32_MAX):
                raise ValueError("Transmission time out of range")

        write_latency = memory_write["Duration"] / memory_write["N"]
        for frame_index in range(memory_write["N"]):
            address = (memory_write["Start_address"] + frame_index) * FRAME_TOTAL_SIZE

            transmission_time = memory_write["Start_time"] + frame_index * write_latency

            check_addr_overflow(address)
            check_time_overflow(transmission_time)

            frame_header = struct.pack('<If', address, transmission_time)
            frame_data = DATA_PATTERN * (FRAME_PAYLOAD_SIZE // len(DATA_PATTERN))
            frame = frame_header + frame_data

            if __debug__:
                assert len(frame) == FRAME_TOTAL_SIZE

            yield frame

    def __generate(self) -> tuple[int, int, list, str]:
        """
        Generates the next writing pattern and writes corresponding frames to the FRAMES.bin file.

        Returns:
            tuple: (threshold, delta, pattern_descriptor, frames_bin_filename)
                - threshold (int): Pattern threshold parameter.
                - delta (int): Pattern delta parameter.
                - pattern_descriptor (list): Frame count per memory write.
                - frames_bin_filename (str): Output file path for generated frames.

        Raises:
            OSError: If writing to the frames file fails.
            ValueError: If frame header fields are invalid.
        """
        self.__current_pattern = next(self.__patterns_iter)
        pattern_descriptor = []

        try:
            with open(FRAMES_BIN_FILENAME, "wb") as f:
                for mw_index, memory_write in enumerate(self.__current_pattern["memory_writes"]):
                    pattern_descriptor.append(0)
                    for frame_index, frame in enumerate(self.__get_frames(memory_write)):
                        f.write(frame)
                        pattern_descriptor[mw_index] += 1
        except OSError as err:
            logger.error(f"Failed to write to {FRAMES_BIN_FILENAME}: {err}")
            raise
        except ValueError as err:
            logger.error(f"Invalid frame header field value: {err}")
            raise

        logger.info(f"Successfully generated a writing pattern, bin file: {FRAMES_BIN_FILENAME}")

        return (self.__current_pattern["threshold"], self.__current_pattern["delta"],
                pattern_descriptor, FRAMES_BIN_FILENAME)
