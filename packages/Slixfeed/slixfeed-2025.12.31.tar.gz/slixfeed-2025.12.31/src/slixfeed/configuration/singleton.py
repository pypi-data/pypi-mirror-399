#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

import os
from slixfeed.config import Cache, Config, Data, Settings
from slixfeed.utility.toml import UtilityToml
from slixfeed.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

"""@dataclass"""
class ConfigurationSingleton:
    """
    alias: str = None
    sessions: dict = {}
    directory_cache: str = None
    directory_config: str = None
    directory_data: str = None
    directory_settings: str = None
    filename_settings: str = None
    defaults: dict = {}
    settings_selectors: dict
    settings_selectors_allow: int
    settings_selectors_deny: int
    data_selectors: dict
    selectors_allow: list
    selectors_deny: list
    settings_network
    trackers: list
    pathnames: list
    filters_keywords_allow: list
    filters_keywords_deny: list
    filters_hostname: list
    filters_tld: list
    """

    def __init__(self, alias=None):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{alias}	Start")

        # Handlers for directories.
        self.directory_cache = Cache.get_directory()
        self.directory_config = Config.get_directory()
        self.directory_data = Data.get_directory()
        self.directory_settings = Settings.get_directory()
        self.directory_focuscript = os.path.join(self.directory_data, "focuscript")
        self.alias = alias if alias else "Slixfeed"
        self.database_address_book = os.path.join(self.directory_data, "subscribers.sqlite")
        self.database_focuscript = os.path.join(self.directory_data, "focuscript.sqlite")

        # A handler for routine configuration.
        filename_settings = os.path.join(self.directory_config, "settings.toml")
        if os.path.exists(filename_settings):
            data_settings = UtilityToml.open_file(filename_settings)
            self.settings = data_settings
            self.defaults = data_settings["default"]
            self.interface = data_settings["configuration"]["interface"]
            # A handlers for selectors.
            self.settings_selectors = data_settings["selectors"]
            self.settings_selectors_allow = self.settings_selectors["allow"]
            self.settings_selectors_deny = self.settings_selectors["deny"]
            # A handler for network configurations.
            self.settings_network = data_settings["network"]
        else:
            logger.warning(f"{function_name}	{alias}	File settings.toml is missing.")

        # Handlers for whitelist and blacklist.
        filename_selectors = os.path.join(self.directory_config, "selectors.toml")
        if os.path.exists(filename_selectors):
            self.data_selectors = UtilityToml.open_file(filename_selectors)
            self.selectors_allow = self.data_selectors["allow"]
            self.selectors_deny = self.data_selectors["deny"]
        else:
            logger.warning(f"{function_name}	{alias}	File selectors.toml is missing.")

        # A handler for queries.
        filename_queries = os.path.join(self.directory_config, "queries.toml")
        if os.path.exists(filename_queries):
            data_queries = UtilityToml.open_file(filename_queries)
            self.trackers = data_queries["trackers"]
        else:
            logger.warning(f"{function_name}	{alias}	File queries.toml is missing.")

        # A handler for lists.
        filename_lists = os.path.join(self.directory_config, "lists.toml")
        if os.path.exists(filename_lists):
            data_lists = UtilityToml.open_file(filename_lists)
            self.pathnames = data_lists["pathnames"]
        else:
            logger.warning(f"{function_name}	{alias}	File lists.toml is missing.")

        # A handler for filters.
        filename_filters = os.path.join(self.directory_config, "filters.toml")
        if os.path.exists(filename_filters):
            data_filters = UtilityToml.open_file(filename_filters)
            self.filters_keywords_allow = data_filters["keywords-allow"]
            self.filters_keywords_deny = data_filters["keywords-deny"]
            self.filters_hostname = data_filters["hostname-deny"]
            self.filters_tld = data_filters["tld-deny"]
        else:
            logger.warning(f"{function_name}	{alias}	File filters.toml is missing.")

configurations = ConfigurationSingleton()
