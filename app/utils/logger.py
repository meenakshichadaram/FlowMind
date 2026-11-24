import logging
import sys
from typing import Optional

def setup_logger(name: str = "flowmind", log_level: str = "INFO") -> logging.Logger:
    """Configures and returns a standardized logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        level = getattr(logging, log_level.upper(), logging.INFO)
        logger.setLevel(level)
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

logger = setup_logger()
