"""
Created on 2025-01-25

@author: wf
"""

import logging


class Logger:
    """Logger singleton for M-Bus reader"""
    _logger = None

    @classmethod
    def setup_logger(cls, debug: bool = False) -> logging.Logger:
        if cls._logger is None:
            cls._logger = logging.getLogger("MBusReader")
            if debug:
                cls._logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            cls._logger.addHandler(handler)
        return cls._logger