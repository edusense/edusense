
import numpy as np
import os
import logging
from logging.handlers import WatchedFileHandler
import subprocess

def time_diff(t_start, t_end):
    """
    Get time diff in secs

    Parameters:
        t_start(datetime)               : Start time
        t_end(datetime)                 : End time

    Returns:
        t_diff(int)                     : time difference in secs
    """

    return (t_end - t_start).seconds + np.round((t_end - t_start).microseconds / 1000000, 3)


def get_logger(logname, logdir='cache/logs',console_log=True):
    # Initialize the logger

    logger_master = logging.getLogger(logname)
    logger_master.setLevel(logging.DEBUG)

    if not os.path.exists(logdir):
        os.makedirs(logdir)

    ## Add core logger handler

    core_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(filename)s:L%(lineno)d | %(process)d:%(processName)s | %(levelname)s | %(message)s')
    core_logging_handler = WatchedFileHandler(logdir + '/' + logname + '.log')
    core_logging_handler.setFormatter(core_formatter)
    logger_master.addHandler(core_logging_handler)

    ## Add stdout logger handler
    if console_log:
        console_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(filename)s:L%(lineno)d | %(process)d:%(processName)s | %(levelname)s | %(message)s')
        console_log = logging.StreamHandler()
        console_log.setLevel(logging.DEBUG)
        console_log.setFormatter(console_formatter)
        logger_master.addHandler(console_log)

    # initialize main logger
    logger = logging.LoggerAdapter(logger_master, {})

    return logger
