#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

"""

Consider utilizing a dict as a handler that would match task keyword to functions.

tasks_xmpp_chat =  {"check" : check_updates,
                    "status" : task_status_message,
                    "interval" : task_message}

tasks_xmpp_pubsub =  {"check" : check_updates,
                      "pubsub" : task_pubsub}

scan = {"database" : db_file,
        "task_manager" : xmpp_instance.task_manager[jid_bare]["check"],
        "proxy" : xmpp_instance.settings_network,
        "settings" : xmpp_instance.settings[jid_bare],}

pubsub = {"database" : db_file,
          "instance" : xmpp_instance,
          "task_manager" : xmpp_instance.task_manager[jid_bare]["status"]}

status = {"database" : db_file,
          "instance" : xmpp_instance,
          "task_manager" : xmpp_instance.task_manager[jid_bare]["status"],
          "pending_tasks" : xmpp_instance.pending_tasks[jid_bare],
          "settings" : xmpp_instance.settings[jid_bare]}

chat = {"database" : db_file,
        "instance" : xmpp_instance,
        "task_manager" : xmpp_instance.task_manager[jid_bare]["interval"],
        "pending_tasks" : xmpp_instance.pending_tasks[jid_bare],
        "settings" : xmpp_instance.settings[jid_bare],
        "proxy" : xmpp_instance.settings_network,
        "pathname" : pathname,
        "omemo" : xmpp_instance.omemo_present}

"""

from slixfeed.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

class UtilityTask:

    def restart(task_manager: dict, properties: dict, account: str, task: str, callback):
        UtilityTask.stop(task_manager, account, task)
        UtilityTask.start(properties, account, callback)

    def _start(properties: dict, account: str, callback):
        callback(properties, account)

    def start(self, jid_bare, callback):
        callback(self, jid_bare)

    def stop(task_manager: dict, task: str) -> bool:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{task}	Start")
        task_cancelled = False
        if task in task_manager:
            task_cancelled = task_manager[task].cancel()
        return task_cancelled
