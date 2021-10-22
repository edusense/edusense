"""
Author: Prasoon Patidar
Created: 2nd May 2021

Custom Datetime utils for analytics engine
"""

from datetime import datetime
# import numpy as np


def time_diff(t_start, t_end):
    """
    Get time diff in secs

    Parameters:
        t_start(datetime)               : Start time
        t_end(datetime)                 : End time

    Returns:
        t_diff(int)                     : time difference in secs
    """

    return (t_end - t_start).seconds + round((t_end - t_start).microseconds / 1000000, 3)


def extract_timestamp(session_keyword, logger):
    """
    Extract timestamp information from session keyword
    """
    session_datestring = session_keyword.split("_")[-1]

    datestring_format = "%Y%m%d%H%M"
    try:
        session_start_time = datetime.strptime(session_datestring, datestring_format)
        epoch_start_time = int(session_start_time.strftime("%s"))

        return epoch_start_time
    except:
        logger.error("Wrong format of datestring %s from session keyword, expected format %s", session_datestring,
                     datestring_format)

        return -1
