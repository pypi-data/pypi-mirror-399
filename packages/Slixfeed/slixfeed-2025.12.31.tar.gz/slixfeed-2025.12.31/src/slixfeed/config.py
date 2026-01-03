#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

TODO

1) Site-specific filter (i.e. audiobookbay).

2) Exclude sites from being subjected to filtering (e.g. metapedia).

3) Filter phrases:
    Refer to sqlitehandler.search_entries for implementation.
    It is expected to be more complex than function search_entries.

4) Copy file from /etc/slixfeed/ or /usr/share/slixfeed/

"""

from slixfeed.utility.logger import UtilityLogger
from slixfeed.sqlite.general import SQLiteGeneral
import os
# from random import randrange
import sys

logger = UtilityLogger(__name__)

class Settings:

    def get_directory():
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

class Share:

    def get_directory():
        """
        Determine the directory path where data files be stored.
    
        * If $XDG_DATA_HOME is defined, use it;
        * else if $HOME exists, use it;
        * else if the platform is Windows, use %APPDATA%;
        * else use the current directory.
    
        Returns
        -------
        str
            Path to database file.
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

class Cache:

    def get_directory():
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

class Config:

    def get_directory():
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

    async def set_setting_value(self, jid_bare, db_file, key, val):
        key = key.lower()
        self.settings[jid_bare][key] = val
        if not SQLiteGeneral.is_setting_key(db_file, key):
            await SQLiteGeneral.set_setting_value(db_file, key, val)

class Data:

    def get_directory():
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

def get_values(filename, key=None):
    config_dir = get_default_config_directory()
    if not os.path.isdir(config_dir):
        config_dir = "/usr/share/slixfeed/"
    if not os.path.isdir(config_dir):
        config_dir = os.path.dirname(__file__) + "/assets"
    config_file = os.path.join(config_dir, filename)
    with open(config_file, mode="rb") as defaults:
        result = tomllib.load(defaults)
    values = result[key] if key else result
    return values

def get_setting_value(db_file, key):
    value = SQLiteGeneral.get_setting_value(db_file, key)
    if value:
        value = value[0]
    else:
        value = get_value("settings", "Settings", key)
    # try:
    #     value = int(value)
    # except ValueError as e:
    #     print("ValueError for value {} (key {}):\n{}".format(value, key, e))
    #     if isinstance(value, bool):
    #         if value:
    #             value = 1
    #         else:
    #             value = 0
    return value

def clear_values(input):
    if isinstance(input, dict):
        return {k: clear_values(v) for k, v in input.items()}
    elif isinstance(input, list):
        return [""]
    else:
        return ""

def add_to_list(newwords, keywords):
    """
    Append new keywords to list.

    Parameters
    ----------
    newwords : str
        List of new keywords.
    keywords : str
        List of current keywords.

    Returns
    -------
    val : str
        List of current keywords and new keywords.
    """
    if isinstance(keywords, str) or keywords is None:
        try:
            keywords = keywords.split(",")
        except:
            keywords = []
    newwords = newwords.lower().split(",")
    for word in newwords:
        word = word.strip()
        if len(word) and word not in keywords:
            keywords.extend([word])
    keywords.sort()
    val = ",".join(keywords)
    return val

def remove_from_list(newwords, keywords):
    """
    Remove given keywords from list.

    Parameters
    ----------
    newwords : str
        List of new keywords.
    keywords : str
        List of current keywords.

    Returns
    -------
    val : str
        List of new keywords.
    """
    if isinstance(keywords, str) or keywords is None:
        try:
            keywords = keywords.split(",")
        except:
            keywords = []
    newwords = newwords.lower().split(",")
    for word in newwords:
        word = word.strip()
        if len(word) and word in keywords:
            keywords.remove(word)
    keywords.sort()
    val = ",".join(keywords)
    return val

def is_include_keyword(db_file, key, string):
    """
    Check keyword match.

    Parameters
    ----------
    db_file : str
        Path to database file.
    type : str
        "allow" or "deny".
    string : str
        String.

    Returns
    -------
    Matched keyword or None.

    """
# async def reject(db_file, string):
# async def is_blacklisted(db_file, string):
    keywords = SQLiteGeneral.get_filter_value(db_file, key)
    keywords = keywords[0] if keywords else ""
    keywords = keywords.split(",")
    keywords = keywords + (open_config_file("lists.toml")[key])
    for keyword in keywords:
        if not keyword or len(keyword) < 2:
            continue
        if keyword in string.lower():
            # print(">>> ACTIVATE", i)
            # return 1
            return keyword

"""

This code was tested at module datahandler

reject = 0
blacklist = SQLiteGeneral.get_setting_value(
    db_file,
    "deny"
    )
# print(">>> blacklist:")
# print(blacklist)
# breakpoint()
if blacklist:
    blacklist = blacklist.split(",")
    # print(">>> blacklist.split")
    # print(blacklist)
    # breakpoint()
    for i in blacklist:
        # print(">>> length", len(i))
        # breakpoint()
        # if len(i):
        if not i or len(i) < 2:
            print(">>> continue due to length", len(i))
            # breakpoint()
            continue
        # print(title)
        # print(">>> blacklisted word:", i)
        # breakpoint()
        test = (title + " " + summary + " " + link)
        if i in test.lower():
            reject = 1
            break
        
if reject:
    print("rejected:",title)
    entry = (title, "", link, source, date, 1);

"""
