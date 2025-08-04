import os
from typing import Final

# memory system params
FRAME_HEADER_SIZE: Final = 8
FRAME_PAYLOAD_SIZE: Final = 4096
FRAME_TOTAL_SIZE: Final = FRAME_HEADER_SIZE + FRAME_PAYLOAD_SIZE
DATA_PATTERN: Final = b'\xDE\xAD\xBE\xEF'
UINT32_MAX: Final = 0xFFFFFFFF
FLOAT32_MAX: Final = 3.4028235e+38

# infrastructure constants
FRAMES_BIN_FILENAME: Final = os.path.join("PatternConfigs", "Frames", "FRAMES.bin")
FAILURE_LOGS_FOLDER: Final = "Logs"
