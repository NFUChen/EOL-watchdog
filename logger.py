from typing import Callable
import logging

class FileIsNotLogError(Exception):
    pass

class Logger:
    FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
    def __init__(self, file_name:str) -> None:

        if ".log" not in file_name:
            raise FileIsNotLogError(f"{file_name} is not a valid log file (.log)")

        self.logger = self.__get_logger(file_name)

    def __get_logger(self, file_name:str) -> logging.Logger:
        # create logger with 'file_name'
        logger = logging.getLogger(f"{file_name}")
        logger.setLevel(logging.DEBUG)
        # create file handler which logs even debug messages
        file_handler = logging.FileHandler(f"{file_name}")
        file_handler.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        formatter = logging.Formatter(self.FORMAT)
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)
        # add the handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        return logger

    def log(self, message: str) -> None:
        self.logger.info(message)

    def log_error(self, func:Callable) -> None:
        def wrapper(*args, **kwargs) -> Callable:
            try:
                return func(*args, **kwargs)
            except Exception as error:
                self.logger.error(error)

        return wrapper

