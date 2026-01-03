#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

import os
from slixfeed.configuration.directory import ConfigurationDirectory
from slixfeed.parser.focuscript import ParserFocuscript
from slixfeed.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

directory_scripts = os.path.join(ConfigurationDirectory.data(), "focuscript")
directory_setting = os.path.join(ConfigurationDirectory.config(), "focuscript")

class ConfigurationFocuscript:

    def charge(filename=None):
        """Charge Focuscript into memory."""
        for script in os.listdir(directory_scripts):
            if script.endswith(".focus"):
                filename = os.path.join(directory_scripts, script)
                data = open(filename, "r").read()
                metadata = ParserFocuscript.metadata(data)
                

    def discharge(identifier):
        """Discharge Focuscript from memory."""
        pass

    def recharge(identifier):
        """Recharge Focuscript into memory."""
        pass
