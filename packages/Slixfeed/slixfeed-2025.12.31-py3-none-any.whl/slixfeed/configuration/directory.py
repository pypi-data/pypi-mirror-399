#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

import os
from slixfeed.config import Cache, Config, Data, Settings
from slixfeed.utility.logger import UtilityLogger
from slixfeed.utility.toml import UtilityToml
import sys

logger = UtilityLogger(__name__)

class ConfigurationDirectory:

    def cache():
        """
        Determine the directory path where cache files be stored.
    
        * If $XDG_CACHE_HOME is defined, use it;
        * else if $HOME exists, use it;
        * else if the platform is Windows, use %APPDATA%;
        * else use the current directory.
    
        Returns
        -------
        str
            Path to cache directory.
        """
    #    cache_home = xdg.BaseDirectory.xdg_cache_home
        cache_home = os.environ.get("XDG_CACHE_HOME")
        if cache_home is None:
            if os.environ.get("HOME") is None:
                if sys.platform == "win32":
                    cache_home = os.environ.get("APPDATA")
                    if cache_home is None:
                        return os.path.abspath(".slixfeed/cache")
                else:
                    return os.path.abspath(".slixfeed/cache")
            else:
                cache_home = os.path.join(
                    os.environ.get("HOME"), ".cache"
                    )
        return os.path.join(cache_home, "slixfeed")

    def config():
        """
        Determine the directory path where setting files be stored.
    
        * If $XDG_CONFIG_HOME is defined, use it;
        * else if $HOME exists, use it;
        * else if the platform is Windows, use %APPDATA%;
        * else use the current directory.
    
        Returns
        -------
        str
            Path to configuration directory.
        """
    #    config_home = xdg.BaseDirectory.xdg_config_home
        config_home = os.environ.get("XDG_CONFIG_HOME")
        if config_home is None:
            if os.environ.get("HOME") is None:
                if sys.platform == "win32":
                    config_home = os.environ.get("APPDATA")
                    if config_home is None:
                        return os.path.abspath(".")
                else:
                    return os.path.abspath(".")
            else:
                config_home = os.path.join(
                    os.environ.get("HOME"), ".config"
                    )
        return os.path.join(config_home, "slixfeed")

    def data():
        """
        Determine the directory path where dbfile will be stored.
    
        * If $XDG_DATA_HOME is defined, use it;
        * else if $HOME exists, use it;
        * else if the platform is Windows, use %APPDATA%;
        * else use the current directory.
    
        Returns
        -------
        str
            Path to database file.
    
        Note
        ----
        This function was taken from project buku.
        
        See https://github.com/jarun/buku
    
        * Arun Prakash Jana (jarun)
        * Dmitry Marakasov (AMDmi3)
        """
    #    data_home = xdg.BaseDirectory.xdg_data_home
        data_home = os.environ.get("XDG_DATA_HOME")
        if data_home is None:
            if os.environ.get("HOME") is None:
                if sys.platform == "win32":
                    data_home = os.environ.get("APPDATA")
                    if data_home is None:
                        return os.path.abspath(".slixfeed/data")
                else:
                    return os.path.abspath(".slixfeed/data")
            else:
                data_home = os.path.join(
                    os.environ.get("HOME"), ".local", "share"
                    )
        return os.path.join(data_home, "slixfeed")

"""
    def get_default_data_directory():
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	,Start")
        if os.environ.get("HOME"):
            data_home = os.path.join(os.environ.get("HOME"), ".local", "share")
            return os.path.join(data_home, "slixfeed")
        elif sys.platform == "win32":
            data_home = os.environ.get("APPDATA")
            if data_home is None:
                return os.path.join(
                    os.path.dirname(__file__) + "/slixfeed_data")
        else:
            return os.path.join(os.path.dirname(__file__) + "/slixfeed_data")

    def get_default_config_directory():
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	,Start")
    #    config_home = xdg.BaseDirectory.xdg_config_home
        config_home = os.environ.get("XDG_CONFIG_HOME")
        if config_home is None:
            if os.environ.get("HOME") is None:
                if sys.platform == "win32":
                    config_home = os.environ.get("APPDATA")
                    if config_home is None:
                        return os.path.abspath(".")
                else:
                    return os.path.abspath(".")
            else:
                config_home = os.path.join(
                    os.environ.get("HOME"), ".config"
                    )
        return os.path.join(config_home, "slixfeed")
"""
