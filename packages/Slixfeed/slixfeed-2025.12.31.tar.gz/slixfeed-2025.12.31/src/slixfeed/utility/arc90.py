#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

from readability import Document
from slixfeed.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

class UtilityArc90:

    def process(data: str) -> str:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        """ Process data into a document. """
        return Document(data).summary()
