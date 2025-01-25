"""
Created on 2025-01-25

@author: wf
"""
import logging
class Logger:
    @staticmethod
    def setup_logger(debug:bool=False) -> logging.Logger:
        """Configure logging"""
        logger = logging.getLogger("MBusReader")
        if debug:
            logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
