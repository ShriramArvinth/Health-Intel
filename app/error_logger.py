from dataclasses import dataclass
import logging
from enum import Enum
import traceback

logging.basicConfig(level=logging.WARNING)

@dataclass
class Error:
    module: str
    code: int
    description: str
    excpetion: Exception

class Severity(Enum):
    INFO = 'INFO'
    WARN = 'WARN'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'

def log_error(error: Error, severity: Severity):
    logger = logging.getLogger(error.module)
    if severity == Severity.INFO:
        logger.setLevel(logging.INFO)
    elif severity == Severity.WARN:
        logger.setLevel(logging.WARNING)
    elif severity == Severity.ERROR:
        logger.setLevel(logging.ERROR)
    elif severity == Severity.CRITICAL:
        logger.setLevel(logging.CRITICAL)
    
    stack_trace = ''.join(traceback.format_exception(None, error.excpetion, error.excpetion.__traceback__))
    log_message = f"module={error.module} code={error.code} description=\"{error.description}\" stack_trace=\"{stack_trace}\""

    if severity == Severity.INFO:
        logger.info(log_message)
    elif severity == Severity.WARN:
        logger.warning(log_message)
    elif severity == Severity.ERROR:
        logger.error(log_message)
    elif severity == Severity.CRITICAL:
        logger.critical(log_message)
                