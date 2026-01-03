#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

import os
from slixfeed.config import Config
from slixfeed.utility.logger import UtilityLogger
from slixfeed.utility.toml import UtilityToml
import sys

logger = UtilityLogger(__name__)

class UtilityHandlerGroups:

    def __init__(self, account: str):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{account}	Start")
        # A handler for bookmarks.
        directory_config = Config.get_directory()
        self.filename_bookmarks = os.path.join(directory_config, "bookmarks.toml")
        if (os.path.exists(self.filename_bookmarks) and 
            os.path.getsize(self.filename_bookmarks)):
            self.data_bookmarks = UtilityToml.open_file(self.filename_bookmarks)
        else:
            self.data_bookmarks = {"bookmarks" : {account : {}}}
            UtilityToml.save_file(self.filename_bookmarks, self.data_bookmarks)
        self.bookmarks = self.data_bookmarks["bookmarks"][account]
