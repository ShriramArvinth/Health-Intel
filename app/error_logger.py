from dataclasses import dataclass
import logging
from enum import Enum
import traceback
from google.cloud import logging as cloud_logging
import os

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


    if is_running_in_gcp():
        print("Running in GCP")
        # Google Cloud Logging
        # client = cloud_logging.Client()
        # cloud_logger = client.logger(error.module)

        # if severity == Severity.INFO:
        #     cloud_logger.log_text(log_message, severity='INFO')
        # elif severity == Severity.WARN:
        #     cloud_logger.log_text(log_message, severity='WARNING')
        # elif severity == Severity.ERROR:
        #     cloud_logger.log_text(log_message, severity='ERROR')
        # elif severity == Severity.CRITICAL:
        #     cloud_logger.log_text(log_message, severity='CRITICAL')
        if severity == Severity.INFO:
            logger.info(log_message)
        elif severity == Severity.WARN:
            logger.warning(log_message)
        elif severity == Severity.ERROR:
            logger.error(log_message)
        elif severity == Severity.CRITICAL:
            logger.critical(log_message)
    else:
        print("Running in Non-GCP")
        # Console Logging
        if severity == Severity.INFO:
            logger.info(log_message)
        elif severity == Severity.WARN:
            logger.warning(log_message)
        elif severity == Severity.ERROR:
            logger.error(log_message)
        elif severity == Severity.CRITICAL:
            logger.critical(log_message)

def is_running_in_gcp():
    return os.getenv('GAE_ENV', '').startswith('standard') or os.getenv('K_SERVICE') is not None