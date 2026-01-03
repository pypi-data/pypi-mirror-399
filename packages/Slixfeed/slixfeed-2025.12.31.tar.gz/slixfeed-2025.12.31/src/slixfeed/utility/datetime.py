#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.parser import parse
from email.utils import parsedate, parsedate_to_datetime
from slixfeed.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

class UtilityDateTime:

#https://feedparser.readthedocs.io/en/latest/date-parsing.html

    def now():
        """
        ISO 8601 Timestamp.

        Returns
        -------
        date : ???
            ISO 8601 Timestamp.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        date = datetime.now().isoformat()
        logger.debug(f"{function_name}		Finish")
        return date

    def convert_struct_time_to_iso8601(struct_time):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        date = datetime(*struct_time[:6])
        date = date.isoformat()
        logger.debug(f"{function_name}		Finish")
        return date

    def convert_seconds_to_yyyy_mm_dd(seconds_time):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        date_time = datetime.fromtimestamp(seconds_time)
        formatted_date = date_time.strftime("%Y-%m-%d")
        logger.debug(f"{function_name}		Finish")
        return formatted_date

    def current_date():
        """
        Print MM DD, YYYY (Weekday Time) timestamp.

        Returns
        -------
        date : str
            MM DD, YYYY (Weekday Time) timestamp.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        now = datetime.now()
        time = now.strftime("%B %d, %Y (%A %T)")
        logger.debug(f"{function_name}		Finish")
        return time

    def current_time():
        """
        Print HH:MM:SS timestamp.

        Returns
        -------
        date : str
            HH:MM:SS timestamp.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        now = datetime.now()
        time = now.strftime("%H:%M:%S")
        logger.debug(f"{function_name}		Finish")
        return time

    def timestamp():
        """
        Print time stamp to be used in filename.

        Returns
        -------
        formatted_time : str
            %Y%m%d-%H%M%S timestamp.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        now = datetime.now()
        formatted_time = now.strftime("%Y%m%d-%H%M%S")
        logger.debug(f"{function_name}		Finish")
        return formatted_time

    def validate(date):
        """
        Validate date format.

        Parameters
        ----------
        date : str
            Timestamp.

        Returns
        -------
        date : str
            Timestamp.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        try:
            parse(date)
        except:
            date = UtilityDateTime.now()
        logger.debug(f"{function_name}		Finish")
        return date

    def rfc2822_to_iso8601(date):
        """
        Convert RFC 2822 to ISO 8601.

        Parameters
        ----------
        date : str
            RFC 2822 Timestamp.

        Returns
        -------
        date : str
            ISO 8601 Timestamp.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        if parsedate(date):
            try:
                date = parsedate_to_datetime(date)
                date = date.isoformat()
            except:
                date = UtilityDateTime.now()
        logger.debug(f"{function_name}		Finish")
        return date
