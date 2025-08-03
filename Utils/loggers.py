import logging
import colorlog


def setup_infra_logger() -> None:
    """
    Configures and initializes the global infrastructure logger for the application.

    Sets up a colorized stream handler with timestamped and leveled output for logging
    to the console. Ensures that the logger does not propagate messages to the root logger.

    Side Effects:
        Modifies the handlers and configuration of the logger named "infra_logger".
    """
    infra_logger = logging.getLogger("infra_logger")
    infra_logger.handlers.clear()
    infra_logger_handler = colorlog.StreamHandler()
    infra_logger_formatter = colorlog.ColoredFormatter(
        '%(log_color)s %(asctime)s %(name)s %(levelname)s: %(message)s',
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'bold_red',
        }
    )
    infra_logger_handler.setFormatter(infra_logger_formatter)
    infra_logger.addHandler(infra_logger_handler)
    infra_logger.setLevel(logging.INFO)
    infra_logger.propagate = False


def setup_detector_logger(logfile_path: str) -> None:
    """
    Configures and initializes the detector logger for writing failure logs to a file.

    Sets up a file handler that logs failures to the specified log file.
    Ensures that the logger does not propagate messages to the root logger.

    Args:
        logfile_path (str): Path to the log file where failure logs will be written.

    Side Effects:
        Modifies the handlers and configuration of the logger named "detector_logger".
    """
    detector_logger = logging.getLogger("detector_logger")
    detector_logger.handlers.clear()
    detector_logger_handler = logging.FileHandler(logfile_path)
    detector_logger_formatter = logging.Formatter('%(message)s')
    detector_logger_handler.setFormatter(detector_logger_formatter)
    detector_logger.addHandler(detector_logger_handler)
    detector_logger.setLevel(logging.ERROR)
    detector_logger.propagate = False
