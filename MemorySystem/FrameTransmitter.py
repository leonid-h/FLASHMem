import logging

logger = logging.getLogger("infra_logger." + __name__)


class FrameTransmitter:
    def __init__(self, frames_path: str):
        self.frames_path = frames_path

    def transmit(self):
        pass

    def has_frames(self):
        pass

    def transmit_frame(self):
        pass
