# Project: spot
# File   : utils.py
# Author : Michel Nowak <michel.nowak@thalesgroup.com>
# Date   : 16.10.2025

from datetime import datetime, timedelta
import orekit
orekit.initVM()

from org.orekit.time import AbsoluteDate, TimeScalesFactory, TimeOffset

MICROSECOND_MULTIPLIER = 1000000

def absolutedate_to_datetime(orekit_absolutedate: AbsoluteDate, tz_aware=False) -> datetime:
    """ Converts from orekit.AbsoluteDate objects
    to python datetime objects (utc).

    Args:
        orekit_absolutedate (AbsoluteDate): orekit AbsoluteDate object to convert
        tz_aware (bool): If True, the returned datetime will be timezone-aware (UTC). Default is False.
    Returns:
        datetime: time in python datetime format (UTC)
    """

    utc = TimeScalesFactory.getUTC()
    or_comp = orekit_absolutedate.getComponents(utc)
    or_date = or_comp.getDate()
    or_time = or_comp.getTime()
    us = or_time.getSplitSecond()
    dt = datetime(or_date.getYear(),
                    or_date.getMonth(),
                    or_date.getDay(),
                    or_time.getHour(),
                   or_time.getMinute())
    if tz_aware:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt

def datetime_to_absolutedate(dt_date: datetime) -> AbsoluteDate:
    """
    Converts from python datetime objects to orekit AbsoluteDate objects.

    Args:
        dt_date (datetime): datetime object to convert
    Returns:
        AbsoluteDate: time in orekit AbsoluteDate format
    """
    # if dt_date.tzinfo is not None and dt_date.tzinfo.utcoffset(dt_date) is not None:
        # If the datetime is timezone-aware, convert it to UTC
        # dt_date = dt_date.astimezone(timezone.utc)

    utc = TimeScalesFactory.getUTC()

    return AbsoluteDate(dt_date.year,
                        dt_date.month,
                        dt_date.day,
                        0,
                        0,
                        TimeOffset(0*MICROSECOND_MULTIPLIER+0, TimeOffset.MICROSECOND),
                        utc)

    
def compute_tmax(delta_angle, i):
    table = [[0., 3.0, 3.0, 3.0],
             [1., 5.9, 6.4, 6.4],
             [2., 6.9, 7.7, 7.6],
             [3., 7.7, 8.6, 8.5],
             [4., 8.3, 9.4, 9.3],
             [5., 8.9, 10.3, 10.1],
             [6., 9.4, 11.1, 11.0],
             [7., 10.0, 12.0, 11.8],
             [8., 10.6, 12.8, 12.6],
             [9., 11.1, 13.7, 13.4],
             [10., 11.7, 14.5, 14.2],
             [15., 14.5, 18.7, 18.3],
             [20., 17.3, 22.9, 22.4],
             [25., 20.1, 27.2, 26.4],
             [30., 22.9, 31.4, 30.5],
             [40., 28.6, 39.8, 38.6],
             [50., 34.2, 48.2, 46.8],
             [60., 39.8, 56.7, 54.9],
             [90., 56.7, 82.0, 79.4]]

    man_duration = 0.
    table_size = len(table)
    if delta_angle < table[0][0]:
        man_duration = table[0][i + 1]
    else:
        for j in range(table_size - 1):
            if table[j][0] <= delta_angle <= table[j + 1][0]:
                man_duration = table[j][i + 1] + (table[j + 1][i + 1] - table[j][i + 1]) / (
                        table[j + 1][0] - table[j][0]) * (delta_angle - table[j][0])
                break
        if delta_angle >= table[table_size - 1][0]:
            man_duration = table[table_size - 1][i + 1] + (
                    table[table_size - 1][i + 1] - table[table_size - 2][i + 1]) / (
                                   table[table_size - 1][0] - table[table_size - 2][0]) * (
                                   delta_angle - table[table_size - 1][0])

    return man_duration
