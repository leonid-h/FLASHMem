import logging


def setup_infra_logger() -> None:
    infra_logger = logging.getLogger("infra_logger")
    infra_logger.handlers.clear()
    infra_logger_handler = logging.StreamHandler()
    infra_logger_formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')
    infra_logger_handler.setFormatter(infra_logger_formatter)
    infra_logger.addHandler(infra_logger_handler)
    infra_logger.setLevel(logging.INFO)
    infra_logger.propagate = False


def setup_detector_logger(logfile_path: str) -> None:
    detector_logger = logging.getLogger("detector_logger")
    detector_logger.handlers.clear()
    detector_logger_handler = logging.FileHandler(logfile_path)
    detector_logger_formatter = logging.Formatter('%(message)s')
    detector_logger_handler.setFormatter(detector_logger_formatter)
    detector_logger.addHandler(detector_logger_handler)
    detector_logger.setLevel(logging.ERROR)
    detector_logger.propagate = False
