import logging

logger = logging.getLogger("infra_logger." + __name__)


class WritingPatternDetector:
    def __init__(self, threshold, delta):
        self.errors = []
        self.stats = {}

    def process_incoming_frame(self):
        pass

    def print_statistics(self):
        pass
