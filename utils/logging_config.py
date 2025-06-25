"""
Optimized logging configuration for the Mimicking Mindsets project.
Minimal logging overhead with focus on errors and warnings only.
"""

import logging
import sys
import os
from pathlib import Path

# Create logs directory only if needed
LOGS_DIR = Path("logs")

# Define log levels
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

def setup_logger(name: str, level: str = 'WARNING', log_to_file: bool = False) -> logging.Logger:
    """
    Set up a logger with minimal overhead configuration.
    
    Args:
        name: Logger name (usually __name__)
        level: Log level ('WARNING', 'ERROR', 'CRITICAL' recommended for production)
        log_to_file: Whether to log to file (disabled by default for performance)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(LOG_LEVELS.get(level.upper(), logging.WARNING))
    
    # Simplified formatter for better performance
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    
    # Console handler with minimal configuration
    console_handler = logging.StreamHandler(sys.stdout)
    if os.name == 'nt':  # Windows
        console_handler.stream.reconfigure(encoding='utf-8', errors='replace')
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler only if explicitly requested
    if log_to_file:
        LOGS_DIR.mkdir(exist_ok=True)
        log_file = LOGS_DIR / f"{name.replace('.', '_')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get or create a logger with minimal configuration."""
    return setup_logger(name, level='WARNING')

# Application-specific loggers with production-optimized levels
def get_orchestrator_logger() -> logging.Logger:
    """Get logger for multi-agent orchestrator - errors only."""
    return setup_logger('orchestrator', level='ERROR')

def get_agent_logger() -> logging.Logger:
    """Get logger for persona agents - errors only."""
    return setup_logger('agents', level='ERROR')

def get_api_logger() -> logging.Logger:
    """Get logger for API server - warnings and errors."""
    return setup_logger('api', level='WARNING')

def get_evaluation_logger() -> logging.Logger:
    """Get logger for evaluation pipeline - warnings and errors."""
    return setup_logger('evaluation', level='WARNING') 