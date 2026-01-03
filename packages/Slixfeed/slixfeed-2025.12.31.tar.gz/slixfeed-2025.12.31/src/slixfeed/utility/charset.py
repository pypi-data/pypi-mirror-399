#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

import chardet
from slixfeed.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

class UtilityCharset:

    def decode(uri: str, data: bytes, encoding_decode: str, encoding_encode: str) -> str:
        """
        Decode bytes into string.
        The purpose of URI is to explore error.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{encoding_decode}	Start")
        try:
            return data.decode(encoding_decode).encode(encoding_encode)
        except Exception as e:
            logger.error(f"{function_name}	{uri}	{str(e)} ({encoding_decode})")
            return data

    def detect(data: bytes) -> str:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        """ Detect character encoding. """
        return chardet.detect(data)
