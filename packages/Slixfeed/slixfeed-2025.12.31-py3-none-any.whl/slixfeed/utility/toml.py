#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from slixfeed.utility.logger import UtilityLogger
import sys
import tomli_w

logger = UtilityLogger(__name__)

try:
    import tomllib
except:
    import tomli as tomllib

class UtilityToml:

    def open_file(filename: str) -> dict:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{filename}	Start")
        with open(filename, mode="rb") as fn:
            data = tomllib.load(fn)
            return data

    def save_file(filename: str, data: dict) -> None:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{filename}	Start")
        with open(filename, "w") as fn:
            data_as_string = tomli_w.dumps(data)
            fn.write(data_as_string)
