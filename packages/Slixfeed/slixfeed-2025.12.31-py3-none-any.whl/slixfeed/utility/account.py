#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-FileCopyrightText: 2025 Luna <https://l4.pm>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

from dataclasses import dataclass
import os
from slixfeed.config import Data
from slixfeed.configuration.singleton import configurations
from slixfeed.sqlite.general import SQLiteGeneral
from slixfeed.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

@dataclass
class Account:
    identifier: str
    database: str = None
    settings: dict = None
    tasks_manager: dict = None
    tasks_pending: dict = None

    def create(self) -> None:
        self.database = os.path.join(
            Data.get_directory(), "sqlite",
            configurations.interface, f"{self.identifier}.db")
        if (not os.path.exists(self.database) or
            not os.path.getsize(self.database)):
            SQLiteGeneral.create_a_database_for_an_account(self.database)
        self.settings = {}
        for key in ("amount", "archive", "document", "enabled", "filter",
                    "interval", "length", "media", "old", "omemo", "random",
                    "status_online", "status_away", "status_chat",
                    "status_dnd", "status_xa", "status_offline"):
            self.settings[key] = SQLiteGeneral.get_setting_value(self.database, key)
            if self.settings[key] is None:
                value = configurations.defaults[key]
                SQLiteGeneral.set_initial_setting_value(self.database, key, value)
                self.settings[key] = value
        self.tasks_manager = {}
        self.tasks_pending = {}

@dataclass
class AccountStore:
    accounts: dict[str, Account]

    def retrieve(self, identifier: str) -> Account:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{identifier}	Start")
        if not identifier in self.accounts:
            account = Account(identifier)
            account.create()
            self.accounts[identifier] = account
        return self.accounts[identifier]

accounts = AccountStore({})
