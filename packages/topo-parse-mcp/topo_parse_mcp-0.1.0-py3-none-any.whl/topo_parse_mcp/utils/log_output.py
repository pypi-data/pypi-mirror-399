"""
A small, practical logging utility module for Python.

Features:
- Named loggers via get_logger(name, ...)
- Console (stream) handler with readable formatter
- Rotating file handler (optional) with maxBytes/backups
- Optional JSON formatter for structured logs
- Optional colorized console output (uses colorama if available)

Usage example:
    from python_log_module import get_logger

    logger = get_logger('myapp', level='DEBUG', logfile='logs/app.log', rotate=True)
    logger.info('Hello world', extra={'request_id': 'abc123'})

This file is safe to copy as-is into your project.
"""
import logging
import logging.handlers
import json
import os
from datetime import datetime
from typing import Optional, Union

try:
    import colorama
    colorama.init(autoreset=True)
    _HAS_COLORAMA = True
except Exception:
    _HAS_COLORAMA = False


class JsonFormatter(logging.Formatter):
    """Simple JSON formatter for structured logs."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            'ts': datetime.utcfromtimestamp(record.created).isoformat() + 'Z',
            'name': record.name,
            'level': record.levelname,
            'msg': record.getMessage(),
        }
        # include basic extras if present
        if getattr(record, 'extra', None):
            payload['extra'] = record.extra
        # include exception info
        if record.exc_info:
            payload['exc_info'] = self.formatException(record.exc_info)
        # include stack info
        if record.stack_info:
            payload['stack_info'] = record.stack_info
        return json.dumps(payload, ensure_ascii=False)


class SimpleFormatter(logging.Formatter):
    """Human-friendly formatter with optional color."""

    FORMATS = {
        'DEBUG': '{asctime} [{levelname:^7}] {name}: {message}',
        'INFO': '{asctime} [{levelname:^7}] {name}: {message}',
        'WARNING': '{asctime} [{levelname:^7}] {name}: {message}',
        'ERROR': '{asctime} [{levelname:^7}] {name}: {message}',
        'CRITICAL': '{asctime} [{levelname:^7}] {name}: {message}',
    }

    LEVEL_COLORS = {
        'DEBUG': '\033[37m',    # light gray
        'INFO': '\033[36m',     # cyan
        'WARNING': '\033[33m',  # yellow
        'ERROR': '\033[31m',    # red
        'CRITICAL': '\033[41m', # red bg
    }

    def __init__(self, use_color: bool = True):
        super().__init__(style='{')
        self.use_color = use_color and _HAS_COLORAMA

    def format(self, record: logging.LogRecord) -> str:
        fmt = self.FORMATS.get(record.levelname, self.FORMATS['INFO'])
        record.message = record.getMessage()
        record.asctime = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        base = fmt.format(**record.__dict__)
        if self.use_color:
            color = self.LEVEL_COLORS.get(record.levelname, '')
            reset = '\033[0m'
            return f"{color}{base}{reset}"
        return base


def _ensure_dir(path: str) -> None:
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def get_logger(
    name: str = 'app',
    level: Union[int, str] = 'INFO',
    logfile: Optional[str] = None,
    rotate: bool = True,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    json_format: bool = False,
    console: bool = True,
    propagate: bool = False,
    use_color: bool = True,
) -> logging.Logger:
    """Create or return a configured logger.

    Args:
        name: logger name
        level: logging level (int or string)
        logfile: path to logfile. If None, file logging disabled.
        rotate: if True and logfile is set, use RotatingFileHandler
        max_bytes: rotation size in bytes
        backup_count: number of rotated files to keep
        json_format: if True, file handler (and console) will use JSON format
        console: enable console (stream) handler
        propagate: whether to propagate to ancestor loggers
        use_color: colorize console output when possible
    """
    logger = logging.getLogger(name)
    # Convert level
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(level)
    logger.propagate = propagate

    # Avoid adding duplicate handlers if logger already configured
    if getattr(logger, '_configured_by_get_logger', False):
        return logger

    formatter = JsonFormatter() if json_format else SimpleFormatter(use_color=use_color)

    if console:
        sh = logging.StreamHandler()
        sh.setLevel(level)
        sh.setFormatter(formatter)
        logger.addHandler(sh)

    if logfile:
        _ensure_dir(logfile)
        if rotate:
            fh = logging.handlers.RotatingFileHandler(logfile, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8')
        else:
            fh = logging.FileHandler(logfile, encoding='utf-8')
        fh.setLevel(level)
        # files are better as JSON for parsing, but respect json_format flag
        file_formatter = JsonFormatter() if json_format else SimpleFormatter(use_color=False)
        fh.setFormatter(file_formatter)
        logger.addHandler(fh)

    # mark configured so subsequent calls don't add handlers again
    logger._configured_by_get_logger = True
    return logger


# small convenience wrapper for structured logging
def log_json(logger: logging.Logger, level: Union[int, str], msg: str, **extras) -> None:
    """Log a message with a dict of extras under the 'extra' key so JsonFormatter captures it."""
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    logger.log(level, msg, extra={'extra': extras})

#定义log输出实例
log_output = get_logger('demo', level='INFO', logfile='agent/log_output.log', rotate=True, json_format=False)
log_output.debug('import logger module')

# Example: if run as script, demonstrate usage
if __name__ == '__main__':
    lg = get_logger('demo', level='DEBUG', logfile='logs/demo.log', rotate=True, json_format=False)
    lg.info('debug message', extra={'step': 1})
    lg.info('info message')
    log_json(lg, 'INFO', 'structured message', user='alice', action='login')
    try:
        1 / 0
    except Exception:
        lg.exception('caught exception')
