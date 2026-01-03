#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import os
import shutil
from slixfeed.config import Cache, Data, Settings
from slixfeed.configuration.singleton import configurations
from slixfeed.parser.focuscript import ParserFocuscript
from slixfeed.script.install import install_focuscript
from slixfeed.sqlite.focuscript import SQLiteFocuscript
from slixfeed.sqlite.subscribers import SQLiteSubscribers
#from slixfeed.utility.logger import UtilityLogger
from slixfeed.utility.toml import UtilityToml

#logger = UtilityLogger(__name__)

filename_settings = os.path.join(
    configurations.directory_settings, "settings.toml")
settings = UtilityToml.open_file(filename_settings)
settings_default = settings["default"]
settings_configuration = settings["configuration"]
settings_network = settings["network"]

filename_accounts = os.path.join(
    configurations.directory_settings, "accounts.toml")
accounts = UtilityToml.open_file(filename_accounts)


filename_selectors = os.path.join(
    configurations.directory_settings, "selectors.toml")
selectors = UtilityToml.open_file(filename_selectors)

accounts_list = []
for account in accounts: accounts_list.append(account)

db_file_focuscript = configurations.database_focuscript
directory_focuscript = configurations.directory_focuscript

def start():

    # Create directories
    directory_cache = Cache.get_directory()
    directory_data = Data.get_directory()
    directory_settings = Settings.get_directory()
    for directory in (directory_cache, directory_data, directory_settings):
        if not os.path.exists(directory):
            os.mkdir(directory)
            print(f"Creating directory {directory}")

    # Create cache subdirectories
    for directory in ("md", "enclosure", "markdown", "opml", "readability"):
        subdirectory_cache = os.path.join(directory_cache, directory)
        if not os.path.exists(subdirectory_cache):
            os.mkdir(subdirectory_cache)
            print(f"Creating cache subdirectory {subdirectory_cache}")

    # Create data subdirectories
    directory_sqlite = os.path.join(directory_data, "sqlite")
    if not os.path.exists(directory_sqlite):
        os.mkdir(directory_sqlite)
        print(f"Creating data subdirectory {directory_sqlite}")
    for directory in ("bitmessage", "component", "deltachat", "gemini",
                      "http", "irc", "lxmf", "pubsub", "xmpp"):
        subdirectory_sqlite = os.path.join(directory_sqlite, directory)
        if not os.path.exists(subdirectory_sqlite):
            os.mkdir(subdirectory_sqlite)
            print(f"Creating sqlite subdirectory {subdirectory_sqlite}")

    directory_self = os.path.dirname(__file__)
    # Change location reference of directory.
    directory_self_data = directory_self.replace("script", "data")

    # Copy or instantiate data files
    filename_database = os.path.join(directory_data, "subscribers.sqlite")
    SQLiteSubscribers.create_a_database_of_subscribers(filename_database)
    if (not os.path.exists(filename_database) or
        not os.path.getsize(filename_database)):
        print(f"Creating file {filename_database}")
    else:
        print(f"Reloading tables for database {filename_database}")

    # Copy configuration files
    for filename in ("accounts.toml", "filters.toml", "lists.toml",
                     "selectors.toml", "settings.toml", "queries.toml"):
        filename_settings = os.path.join(directory_settings, filename)
        if (not os.path.exists(filename_settings) or
            not os.path.getsize(filename_settings)):
            filename_original = os.path.join(directory_self_data, "configs", filename)
            shutil.copyfile(filename_original, filename_settings)
            print(f"Copying file {filename_settings}")

    # Example copying a single file.
    #filename_graphics = os.path.join(directory_settings, "image.svg")
    #if (not os.path.exists(filename_graphics) or
    #    not os.path.getsize(filename_graphics)):
    #    filename_original = os.path.join(directory_self_data, "graphics", "image.svg")
    #    shutil.copyfile(filename_original, filename_graphics)
    #    print(f"Copying file {filename_graphics}")

    # Copy data files
    for kind in ("css", "graphics", "info", "xslt"):
        directory_self_data_kind = os.path.join(directory_self_data, kind)
        directory_data_kind = os.path.join(directory_data, kind)
        if not os.path.exists(directory_data_kind):
            directory_data_kind_new = shutil.copytree(directory_self_data_kind,
                                                      directory_data_kind)
            print(f"Creating and populating directory {directory_data_kind_new}")

    # Create data subdirectories
    directory_focus = os.path.join(directory_data, "focuscript")
    if not os.path.exists(directory_focus):
        os.mkdir(directory_focus)
        print(f"Creating data subdirectory {directory_focus}")

    # Install Focuscripts
    directory_self_focuscript = os.path.join(directory_self_data, "focuscript")
    directory_data_focuscript = os.path.join(directory_data, "focuscript")
    for filename in os.listdir(directory_self_focuscript):
        pathname = os.path.join(directory_self_focuscript, filename)
        metadata = ParserFocuscript.metadata(pathname)
        identifier = metadata["identifier"]
        if not os.path.exists(db_file_focuscript):
            SQLiteFocuscript.create_database(db_file_focuscript)
        if not SQLiteFocuscript.select_id_by_identifier(db_file_focuscript, identifier):
            asyncio.run(install_focuscript(pathname))
