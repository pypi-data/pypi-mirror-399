#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

import hashlib
from slixfeed.utility.logger import UtilityLogger
from slixfeed.parser.uri import ParserUri
import sys

logger = UtilityLogger(__name__)

class UtilityText:

    def identifier(uri: str, counter: int) -> str:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{uri}	Start")
        hostname = ParserUri.hostname(uri)
        hostname = hostname.replace(".","-")
        identifier = hostname + "~" + str(counter)
        return identifier

    def md5sum(text: str) -> str:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{text}	Start")
        text_encoded = text.encode()
        text_hashed = hashlib.md5(text_encoded)
        text_digest = text_hashed.hexdigest()
        logger.debug(f"{function_name}		MD5 {text_digest}")
        logger.debug(f"{function_name}		Finish")
        return text_digest

    def message_starts_with_alias(message: str, alias: str) -> bool:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{message}	Start")
        for character in (" ", ",", ".", ":"):
            if message.startswith(alias + character):
                return True
