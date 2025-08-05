import os
from typing import Final

# memory system params
FRAME_ADDRESS_SIZE: Final = 4
FRAME_TX_TIME_SIZE: Final = 4
FRAME_PAYLOAD_SIZE: Final = 4096
FRAME_HEADER_SIZE: Final = FRAME_ADDRESS_SIZE + FRAME_TX_TIME_SIZE
FRAME_TOTAL_SIZE: Final = FRAME_HEADER_SIZE + FRAME_PAYLOAD_SIZE

# flash frame constants
FLASH_FRAME_TOTAL_SIZE: Final = FRAME_ADDRESS_SIZE + FRAME_PAYLOAD_SIZE

DATA_PATTERN: Final = b'\xDE\xAD\xBE\xEF'
UINT32_MAX: Final = 0xFFFFFFFF
FLOAT32_MAX: Final = 3.4028235e+38

# infrastructure constants
FRAMES_BIN_FILENAME: Final = os.path.join("PatternConfigs", "Frames", "FRAMES.bin")
FAILURE_LOGS_FOLDER: Final = "Logs"
