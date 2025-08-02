import logging

infra_logger = logging.getLogger("infra_logger")
infra_logger_handler = logging.StreamHandler()
infra_logger_formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')
infra_logger_handler.setFormatter(infra_logger_formatter)
infra_logger.addHandler(infra_logger_handler)
infra_logger.setLevel(logging.INFO)
infra_logger.propagate = False
