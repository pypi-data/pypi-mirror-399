#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from slixfeed.utility.account import accounts
from slixfeed.utility.logger import UtilityLogger
from slixfeed.sqlite.general import SQLiteGeneral
from slixfeed.utility.subscription import UtilitySubscriptionTask
from slixfeed.utility.task import UtilityTask
import sys

logger = UtilityLogger(__name__)

class UtilitySchedule:

    # Tasks are classes which are passed to this function
    # On an occasion in which they would have returned, variable "tasks" might be called "callback"
    async def start(xmpp_instance, jid_bare, callbacks):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        key = "enabled"
        await SQLiteGeneral.update_setting_value(db_file, key, 1)
        config_account = accounts.retrieve(jid_bare)
        config_account.settings[key] = 1
        for callback in callbacks:
            callback.restart_task(xmpp_instance, jid_bare)
        UtilitySubscriptionTask.restart_task(jid_bare)
        message = "Updates are enabled."
        return message

    async def stop(jid_bare):
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        key = "enabled"
        await SQLiteGeneral.update_setting_value(db_file, key, 0)
        config_account = accounts.retrieve(jid_bare)
        config_account.settings[key] = 0
        for task in ("interval", "status"):
            UtilityTask.stop(config_account.tasks_manager, task)
        message = "Updates are disabled."
        return message
