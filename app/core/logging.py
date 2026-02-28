"""
Logging configuration for RAG7 platform.
"""
import sys
from loguru import logger
from app.core.config import settings


def setup_logging():
    """Configure logging for the application."""
    logger.remove()  # Remove default handler
    
    # Configure format based on settings
    if settings.log_format == "json":
        log_format = (
            "{"
            '"time": "{time:YYYY-MM-DD HH:mm:ss}", '
            '"level": "{level}", '
            '"message": "{message}", '
            '"file": "{file}", '
            '"line": {line}'
            "}"
        )
    else:
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )
    
    # Add console handler
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.log_level,
        colorize=settings.log_format != "json"
    )
    
    # Add file handler
    logger.add(
        "logs/rag7_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="30 days",
        format=log_format,
        level=settings.log_level
    )
    
    return logger


app_logger = setup_logging()
