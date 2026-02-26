"""Structured logging with PII redaction."""
import logging
import re
from typing import Any, Dict

import structlog


# PII patterns to redact
PII_PATTERNS = [
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '[EMAIL]'),
    (re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), '[SSN]'),
    (re.compile(r'\b\d{16}\b'), '[CARD]'),
    (re.compile(r'\b(?:\d{3}-){2}\d{4}\b'), '[PHONE]'),
    (re.compile(r'api[_-]?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]+)["\']?', re.IGNORECASE), 'api_key=[REDACTED]'),
    (re.compile(r'token["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]+)["\']?', re.IGNORECASE), 'token=[REDACTED]'),
    (re.compile(r'password["\']?\s*[:=]\s*["\']?([^\s"\']+)["\']?', re.IGNORECASE), 'password=[REDACTED]'),
]


def redact_pii(text: str) -> str:
    """Redact PII from text.
    
    Args:
        text: Input text
        
    Returns:
        Text with PII redacted
    """
    if not isinstance(text, str):
        return text
    
    result = text
    for pattern, replacement in PII_PATTERNS:
        result = pattern.sub(replacement, result)
    return result


def redact_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively redact PII from dictionary.
    
    Args:
        data: Input dictionary
        
    Returns:
        Dictionary with PII redacted
    """
    if not isinstance(data, dict):
        return data
    
    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = redact_pii(value)
        elif isinstance(value, dict):
            result[key] = redact_dict(value)
        elif isinstance(value, list):
            result[key] = [
                redact_dict(item) if isinstance(item, dict) else redact_pii(str(item))
                for item in value
            ]
        else:
            result[key] = value
    return result


class PIIRedactionProcessor:
    """Structlog processor for PII redaction."""
    
    def __call__(self, logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Process log event and redact PII.
        
        Args:
            logger: Logger instance
            method_name: Method name
            event_dict: Event dictionary
            
        Returns:
            Processed event dictionary
        """
        # Redact event message
        if 'event' in event_dict:
            event_dict['event'] = redact_pii(str(event_dict['event']))
        
        # Redact other fields
        return redact_dict(event_dict)


def configure_logging(log_level: str = "INFO", json_logs: bool = True) -> None:
    """Configure structured logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Whether to output JSON logs (True) or console logs (False)
    """
    # Configure Python logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper()),
    )

    # Configure structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        PIIRedactionProcessor(),
        structlog.processors.UnicodeDecoder(),
    ]

    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a configured logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger
    """
    return structlog.get_logger(name)
