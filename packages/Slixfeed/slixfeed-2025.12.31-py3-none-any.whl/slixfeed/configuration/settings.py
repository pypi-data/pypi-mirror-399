#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

import os
from slixfeed.config import Cache, Config, Data, Settings
from slixfeed.utility.logger import UtilityLogger
from slixfeed.utility.toml import UtilityToml
from slixfeed.sqlite.general import SQLiteGeneral
import sys

logger = UtilityLogger(__name__)

class ConfigurationDirectory:

    def get_setting_value(db_file, key):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        value = SQLiteGeneral.get_setting_value(db_file, key)
        if value:
            value = value[0]
        else:
            value = UtilityConfiguration.get_value("settings", "Settings", key)
        return value

    def get_values(filename, key=None):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{filename}	Start")
        config_dir = UtilityConfiguration.get_default_config_directory()
        if not os.path.isdir(config_dir):
            config_dir = "/usr/share/slixfeed/"
        if not os.path.isdir(config_dir):
            config_dir = os.path.dirname(__file__) + "/assets"
        config_file = os.path.join(config_dir, filename)
        result = UtilityToml.open_file(config_file)
        values = result[key] if key else result
        return values
