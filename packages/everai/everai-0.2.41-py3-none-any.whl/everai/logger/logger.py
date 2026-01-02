import logging
import os.path
import sys
import typing


class ShortFilenameFormatter(logging.Formatter):
    def format(self, record):
        filename = record.filename
        fields = os.path.split(filename)
        start_index = 0
        for idx, field in enumerate(fields):
            if field == 'src':
                start_index = idx
                break
        filename = os.path.join(*(fields[start_index:-1]))
        record.project_filename = filename
        return super(ShortFilenameFormatter, self).format(record)


default_log_format = '[%(asctime)s][%(levelname)s][%(project_filename)s:%(lineno)d] %(message)s'
default_date_format = '%Y-%m-%d %H:%M:%S'

default_formatter = ShortFilenameFormatter(default_log_format, datefmt=default_date_format)

Level = typing.Literal[
    'CRITICAL',
    'FATAL',
    'ERROR',
    'WARNING',
    'WARN',
    'INFO',
    'DEBUG',
]


def getLogger(name: typing.Optional[str] = None, level: typing.Optional[Level] = None) -> logging.Logger:
    ret = logging.getLogger(name)
    logger_handler = logging.StreamHandler(sys.stdout)
    ret.addHandler(logger_handler)
    logger_handler.setFormatter(default_formatter)

    if level is not None:
        logger_handler.setLevel(level)
    return ret


default_logger = getLogger(level='WARN')


def debug(msg, *args, **kwargs):
    default_logger.debug(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    default_logger.info(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    default_logger.warning(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    default_logger.error(msg, *args, **kwargs)


def fatal(msg, *args, **kwargs):
    default_logger.fatal(msg, *args, **kwargs)


def critical(msg, *args, **kwargs):
    default_logger.critical(msg, *args, **kwargs)
