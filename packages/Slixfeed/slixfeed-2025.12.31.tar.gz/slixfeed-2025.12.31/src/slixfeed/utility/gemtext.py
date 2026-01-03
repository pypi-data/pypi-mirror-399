#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

from slixfeed.utility.datetime import UtilityDateTime
from slixfeed.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

class UtilityGemText:

    def generate(jid_bare: str, filename: str, subscriptions: list) -> None:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        logger.debug(f"{function_name}	{jid_bare}	Filename: {filename}")
        with open(filename, "w") as file:
            file.write(f"# Subscriptions of {jid_bare}\n\n")
            for subscription in subscriptions:
                file.write(f"=> {subscription[2]} {subscription[1]}\n")
            file.write("\n## Slixfeed\n\n"
                       f"Created at {UtilityDateTime.current_date()}\n\n"
                       "=> https://schapps.woodpeckersnest.space")
