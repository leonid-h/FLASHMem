# Private function 1: Parses a YAML file in InputConfigs into a collection of frames
# Private function 2: Writes to a FRAMES.bin file (overwrites if exists) in Frames
# generate_frames() - public API that calls the private functions
import math
import yaml
import logging
import struct
from typing import TypeVar, Generator, Iterable, Iterator

from Utils.constants import FRAME_PAYLOAD_SIZE, FRAME_TOTAL_SIZE, DATA_PATTERN, FRAMES_BIN_FILENAME

logger = logging.getLogger(__name__)
T = TypeVar('T')


def safe_iterate_patterns(ptrn_generator: Iterable[T]) -> Generator[T, None, None]:
    it = iter(ptrn_generator)
    while True:
        try:
            yield next(it)
        except StopIteration:
            break
        except (OSError, ValueError) as e:
            logger.error(f"Pattern skipped due to error: {e}")
            continue


class BadConfigError(Exception):
    pass


class PatternGenerator:
    def __init__(self, config_file_path: str, frames_path: str) -> None:
        self.__config_file_path = config_file_path
        self.__frames_path = frames_path + "/" + FRAMES_BIN_FILENAME
        self.__patterns_iter = None

    def __iter__(self) -> Iterator[tuple[int, int, str]]:
        return self

    def __next__(self) -> tuple[int, int, str]:
        return self.__generate()

    def init(self) -> None:
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
    def _get_frames(memory_write: dict) -> Generator[bytes, None, None]:

        tx_times = set()

        def ensure_unique_tx_time(tx_time: int) -> int:
            while tx_time in tx_times:
                tx_time += 1
            tx_times.add(tx_time)
            return tx_time

        def check_overflow(value) -> None:
            if not (0 <= value <= 0xFFFFFFFF):
                raise ValueError("Value out of range")

        write_latency = memory_write["Duration"] / memory_write["N"]
        for frame_number in range(memory_write["N"]):
            address = memory_write["Start_address"] + frame_number * FRAME_TOTAL_SIZE
            transmission_time = math.floor(memory_write["Start_time"] + frame_number * write_latency)
            transmission_time = ensure_unique_tx_time(transmission_time)

            check_overflow(address)
            check_overflow(transmission_time)

            frame_header = struct.pack('<II', address, transmission_time)
            frame_data = DATA_PATTERN * (FRAME_PAYLOAD_SIZE // len(DATA_PATTERN))
            frame = frame_header + frame_data

            if __debug__:
                assert len(frame) == FRAME_TOTAL_SIZE

            yield frame

    def __generate(self) -> tuple[int, int, str]:
        current_pattern = next(self.__patterns_iter)

        try:
            with open(self.__frames_path, "wb") as f:
                for memory_write in current_pattern["memory_writes"]:
                    for frame in self._get_frames(memory_write):
                        f.write(frame)
        except OSError as err:
            logging.error(f"Failed to write to {self.__frames_path}: {err}")
            raise
        except ValueError as err:
            logging.error(f"Invalid frame header field value: {err}")
            raise

        logger.info(f"Successfully generated a writing pattern, bin file: {self.__frames_path}")

        return current_pattern["threshold"], current_pattern["delta"], self.__frames_path
