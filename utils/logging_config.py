"""
Centralized logging configuration for the Mimicking Mindsets project.
Provides structured logging with appropriate levels for production deployment.
"""

import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Define log levels
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

def setup_logger(name: str, level: str = 'INFO', log_to_file: bool = True) -> logging.Logger:
    """
    Set up a logger with consistent formatting and handlers.
    
    Args:
        name: Logger name (usually __name__)
        level: Log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_to_file: Whether to log to file in addition to console
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(LOG_LEVELS.get(level.upper(), logging.INFO))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler with UTF-8 encoding for Windows compatibility
    # Fix Unicode encoding issues on Windows
    if os.name == 'nt':  # Windows
        # Use UTF-8 encoding for Windows console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.stream.reconfigure(encoding='utf-8', errors='replace')
    else:
        console_handler = logging.StreamHandler(sys.stdout)
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if requested) - always use UTF-8 encoding
    if log_to_file:
        log_file = LOGS_DIR / f"{name.replace('.', '_')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get or create a logger with default configuration."""
    return setup_logger(name)

# Application-specific loggers
def get_orchestrator_logger() -> logging.Logger:
    """Get logger for multi-agent orchestrator."""
    return setup_logger('orchestrator', level='INFO')

def get_agent_logger() -> logging.Logger:
    """Get logger for persona agents."""
    return setup_logger('agents', level='INFO')

def get_api_logger() -> logging.Logger:
    """Get logger for API server."""
    return setup_logger('api', level='INFO')

def get_evaluation_logger() -> logging.Logger:
    """Get logger for evaluation pipeline."""
    return setup_logger('evaluation', level='INFO') 