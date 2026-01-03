#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from slixfeed.configuration.singleton import configurations
from slixfeed.utility.account import accounts
from slixfeed.utility.documentation import UtilityDocumentation
from slixfeed.utility.logger import UtilityLogger
from slixfeed.utility.toml import UtilityToml
from slixfeed.sqlite.general import SQLiteGeneral
from slixfeed.version import __version__
import sys

logger = UtilityLogger(__name__)

    # for task in main_task:
    #     task.cancel()

    # Deprecated in favour of event "presence_available"
    # if not main_task:
    #     await select_file()

class UtilityInformation:

    def print_help():
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        file_info = os.path.join(configurations.directory_data,
                                 "info", "commands.toml")
        result = UtilityDocumentation.manual(file_info)
        message = "\n".join(result)
        return message

    def print_help_list():
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        file_info = os.path.join(configurations.directory_data,
                                 "info", "commands.toml")
        command_list = UtilityDocumentation.manual(file_info, section="all")
        message = ("Complete list of commands:\n"
                   f"```\n{command_list}\n```")
        return message

    def print_help_specific(command_root, command_name):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{command_name}	Start")
        file_info = os.path.join(configurations.directory_data,
                                 "info", "commands.toml")
        command_list = UtilityDocumentation.manual(file_info,
                                                   section=command_root,
                                                   command=command_name)
        if command_list:
            command_list = "".join(command_list)
            message = (command_list)
        else:
            message = f"KeyError for {command_root} {command_name}"
        return message

    def print_help_key(command):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{command}	Start")
        file_info = os.path.join(configurations.directory_data,
                                 "info", "commands.toml")
        command_list = UtilityDocumentation.manual(file_info, command)
        if command_list:
            command_list = " ".join(command_list)
            message = (f"Available command `{command}` keys:\n"
                       f"```\n{command_list}\n```\n"
                       f"Usage: `help {command} <command>`")
        else:
            message = f"KeyError for {command}"
        return message

    def print_info_list():
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        file_info = os.path.join(configurations.directory_data,
                                 "info", "information.toml")
        result = UtilityToml.open_file(file_info)
        message = "\n".join(result)
        return message

    def print_info_specific(entry):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{entry}	Start")
        file_info = os.path.join(configurations.directory_data,
                                 "info", "information.toml")
        entries = UtilityToml.open_file(file_info)
        if entry in entries:
            # command_list = "\n".join(command_list)
            message = (entries[entry]["info"])
        else:
            message = f"KeyError for {entry}"
        return message

    def list_feeds(jid_bare, query=None):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        if query:
            feeds = SQLiteGeneral.search_feeds(db_file, query)
        else:
            feeds = SQLiteGeneral.get_feeds(db_file)
        number = len(feeds)
        message = ""
        if number:
            for id, title, url in feeds:
                message += f"\n{str(url)}\n{str(title)} [{str(id)}]\n"
        elif query:
            message = f"No subscriptions were found for \"{query}\"."
        return message, number

    def print_options(jid_bare):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        message = ""
        config_account = accounts.retrieve(jid_bare)
        for key in config_account.settings:
            value = config_account.settings[key]
            steps = 11 - len(key)
            pulse = ""
            for step in range(steps):
                pulse += " "
            message += "\n" + key + pulse + ": " + str(value)
        return message

    # """You have {} unread news items out of {} from {} subscriptions.
    # """.format(unread_entries, entries, feeds)
    def print_statistics(jid_bare):
        """
        Print statistics.
    
        Parameters
        ----------
        jid_bare : str
            Account address.
    
        Returns
        -------
        msg : str
            Statistics as message.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        entries_unread = SQLiteGeneral.get_number_of_entries_unread(db_file)
        entries_all = SQLiteGeneral.get_number_of_items(db_file, "entries_properties")
        feeds_active = SQLiteGeneral.get_number_of_feeds_active(db_file)
        feeds_all = SQLiteGeneral.get_number_of_items(db_file, "feeds_properties")
        message = (f"Subscriptions: {feeds_active} (active) {feeds_all} (all) "
                   f"Items: {entries_unread} (unread) {entries_all} (all).")
        return message

    def print_selector(list_type):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        jids = " ".join(list_type) if list_type else "(empty)."
        message = f"Jabber IDs: {jids}"
        return message

    def print_version():
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        message = __version__
        return message

    def print_unknown():
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        message = "An unknown command.  Type \"help\" for a list of commands."
        return message
