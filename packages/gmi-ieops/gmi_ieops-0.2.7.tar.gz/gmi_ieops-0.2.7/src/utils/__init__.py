"""
Utils Module - Provides common utility functions
"""

# Environment variable manager (import first)
from .config import env

# Logging
from .log import log, uvicorn_logger

# Random utilities
from .util import randstr, arandstr, randint, arandint, APP_ID

# File operations
from .file import load_json, save_json, save, save_jfs

# Subprocess management
from .subprocess_manager import SubprocessManager, create_http_health_check

# LLM sampling params (import as module)
from . import llm_sampling_params

# Initialize logger with environment variables
log.set_logger(
    log_path=env.log.path,
    app_name=env.app.name,
    log_level=env.log.level,
    file_enabled=env.log.file_enabled,
)

__all__ = [
    # Environment variable manager
    'env',
    
    # Logging
    'log',
    'uvicorn_logger',
    
    # Random utilities
    'randstr',
    'arandstr',
    'randint',
    'arandint',
    'APP_ID',
    
    # File operations
    'load_json',
    'save_json',
    'save',
    'save_jfs',
    
    # Subprocess management
    'SubprocessManager',
    'create_http_health_check',
    
    # LLM sampling params
    'llm_sampling_params',
]
