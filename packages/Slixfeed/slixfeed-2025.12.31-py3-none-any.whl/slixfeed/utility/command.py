#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

import asyncio
import os
from pathlib import Path
from random import randrange # pending_tasks: Use a list and read the first index (i.e. index 0).
from slixfeed.configuration.singleton import configurations
from slixfeed.interface.xmpp.message import XmppMessage
from slixfeed.interface.xmpp.muc import XmppMuc
from slixfeed.interface.xmpp.presence import XmppPresence
from slixfeed.interface.xmpp.status import XmppStatus, XmppStatusTask
from slixfeed.interface.xmpp.upload import XmppUpload
from slixfeed.interface.xmpp.utilities import XmppUtilities
from slixfeed.parser.uri import ParserUri
from slixfeed.retriever.http import RetrieverHttp
from slixfeed.sqlite.general import SQLiteGeneral
from slixfeed.utility.account import accounts
from slixfeed.utility.arc90 import UtilityArc90
#from slixfeed.utility.content import UtilityContent
from slixfeed.utility.database import UtilityDatabase
from slixfeed.utility.html import UtilityHtml
from slixfeed.utility.information import UtilityInformation
from slixfeed.utility.logger import UtilityLogger
from slixfeed.utility.option import UtilityOption
from slixfeed.utility.schedule import UtilitySchedule
from slixfeed.utility.subscription import UtilitySubscription
from slixfeed.utility.task import UtilityTask
from slixfeed.utility.text import UtilityText
from slixfeed.utility.uri import UtilityUri
from slixfeed.utility.xmpp import UtilityXmpp
from slixmpp.jid import JID
from slixmpp.stanza import Message
#from slixmpp.types import JidStr
import sys
import time
from typing import Optional

logger = UtilityLogger(__name__)

class UtilityCommand:

        def message(command):
            function_name = sys._getframe().f_code.co_name
            logger.debug(f"{function_name}	{command}	Start")
            command_lowercase = command.lower()
            match command_lowercase:
                case _ if command_lowercase.startswith("export"):
                    status = "dnd"
                    message = "📤️ Procesing request to export subscriptions..."
                case "service start":
                    status = "available"
                    message = "📫️ Welcome back."
                case "service stop":
                    status = "xa"
                    message = "📪️ Send \"service start\" to receive updates"
                case _ if command_lowercase.startswith("subscribe"):
                    url = command[10:]
                    status = "dnd"
                    message = f"📫️ Retrieving data from {url}"
                case _ if (command_lowercase.endswith(".opml") and
                           ParserUri.scheme(command)):
                    status = "dnd"
                    message = "📥️ Procesing request to import subscriptions..."
                case _ if command_lowercase.startswith("subscription remove"):
                    ix_url = command[20:]
                    ix_url = ix_url.split(" ")
                    status = "dnd"
                    message = "📫️ Removing subscription and entries..."
                case _ if command_lowercase.startswith("subscription reset"):
                    status = "dnd"
                    message = "📫️ Marking entries as read..."
                case "subscriptions reset":
                    status = "dnd"
                    message = "📫️ Marking all entries as read..."
                case _ :
                    status = message = None
            return status, message

        async def action(account, command):
            function_name = sys._getframe().f_code.co_name
            logger.debug(f"{function_name}	{account}	Start")
            logger.debug(f"{function_name}	{account}	{command}")
            command_lowercase = command.lower()
            match command_lowercase:
                case "help":
                    command_list = UtilityInformation.print_help()
                    response = ("Available command keys:\n"
                                f"```\n{command_list}\n```\n"
                                "Usage: `help <key>`")
                case "help all":
                    command_list = UtilityInformation.print_help_list()
                    response = ("Complete list of commands:\n"
                                f"```\n{command_list}\n```")
                case _ if command_lowercase.startswith("help"):
                    command = command[5:].lower()
                    command = command.split(" ")
                    if len(command) == 2:
                        command_root = command[0]
                        command_name = command[1]
                        command_list = UtilityInformation.print_help_specific(
                            command_root, command_name)
                        if command_list:
                            response = (command_list)
                        else:
                            response = f"KeyError for {command_root} {command_name}"
                    elif len(command) == 1:
                        command = command[0]
                        command_list = UtilityInformation.print_help_key(command)
                        if command_list:
                            response = (f"Available command `{command}` keys:\n"
                                        f"```\n{command_list}\n```\n"
                                        f"Usage: `help {command} <command>`")
                        else:
                            response = f"KeyError for {command}"
                    else:
                        response = ("Invalid. Enter command key "
                                    "or command key & name")
                case "info":
                    entries = UtilityInformation.print_info_list()
                    response = ("Available command options:\n"
                                f"```\n{entries}\n```\n"
                                "Usage: `info <option>`")
                case _ if command_lowercase.startswith("info"):
                    entry = command[5:].lower()
                    response = UtilityInformation.print_info_specific(entry)
                case _ if command_lowercase.startswith("subscribe"):
                    url = command[10:]
                    blocked = False
                    hostname = ParserUri.hostname(url)
                    blocked = UtilityUri.is_host(url,
                                                 configurations.filters_hostname)
                    if not blocked:
                        blocked = UtilityUri.is_tld(url,
                                                    configurations.filters_tld)
                    if blocked:
                        response = f"URL {url} is blocked by this service."
                    else:
                        information = await UtilitySubscription.subscribe(url, account)
                        response = information["message"]
                case "get amount":
                    response = UtilityOption.get_amount(account)
                case "get archive":
                    response = UtilityOption.get_archive(account)
                case "get interval":
                    response = UtilityOption.get_interval(account)
                case "get length":
                    response = UtilityOption.get_length(account)
                case _ if (command_lowercase.endswith(".opml") and
                           ParserUri.scheme(command)):
                    uri = command
                    response = await UtilitySubscription.import_opml(account, uri)
                #case _ if command_lowercase.startswith("keyword"):
                case "print options":
                    response = UtilityInformation.print_options(account)
                case "print statistics":
                    response = UtilityInformation.print_statistics(account)
                case "print subscriptions":
                    result, number = UtilityInformation.list_feeds(account)
                    if number:
                        response = f"{number} subscriptions.\n\n" + result
                    else:
                        response = f"No subscriptions were found."
                case "print version":
                    response = UtilityInformation.print_version()
                case _ if command_lowercase.startswith("search entries"):
                    query = command[15:]
                    response = UtilityDatabase.search(account, query)
                case _ if command_lowercase.startswith("search subscriptions"):
                    query = command[21:]
                    if query:
                        result, number = UtilityInformation.list_feeds(account, query)
                        if number:
                            response = (f"{number} subscriptions containing "
                                        f"\"{query}\".\n\n" + result)
                        else:
                            response = ("No subscriptions containing "
                                        f"\"{query}\" were found.")
                    else:
                        response = "Please enter a query."
                case _ if command_lowercase.startswith("set amount"):
                    value = command[11:]
                    if value:
                        response = await UtilityOption.set_amount(account, value)
                    else:
                        response = "Value is missing."
                case _ if command_lowercase.startswith("set archive"):
                    value = command[12:]
                    if value:
                        response = await UtilityOption.set_archive(account, value)
                    else:
                        response = "Value is missing."
                case "set encryption off":
                    response = await UtilityOption.set_omemo_off(account)
                case "set encryption on":
                    response = await UtilityOption.set_omemo_on(account)
                case _ if command_lowercase.startswith("set interval"):
                    value = command[13:]
                    if value:
                        response = await UtilityOption.set_interval(account, value)
                    else:
                        response = "Value is missing."
                case _ if command_lowercase.startswith("set length"):
                    value = command[11:]
                    if value:
                        response = await UtilityOption.set_length(account, value)
                    else:
                        response = "Value is missing."
                case "set media off":
                    response = await UtilityOption.set_media_off(account)
                case "set media on":
                    response = await UtilityOption.set_media_on(account)
                case _ if command_lowercase.startswith("set order"):
                    order = command[10:]
                    if order == "normal":
                        response = UtilityOption.set_order_random(account)
                    elif order == "random":
                        response = UtilityOption.set_order_normal(account)
                    else:
                        response = "Please enter order \"normal\" or \"random\"."
                case _ if command_lowercase.startswith("set routine"):
                    key = command[12:]
                    if key:
                        response = await UtilityOption.restore_default(account, key)
                    else:
                        response = "Enter a key or \"all\"."
                case "set send all":
                    response = await UtilityOption.set_old_on(account)
                case "set send new":
                    response = await UtilityOption.set_old_off(account)
                case _ if command_lowercase.startswith("set status off"):
                    key = command[15:]
                    if key in ("online", "away", "chat", "dnd", "offline", "xa"):
                        response = await UtilityOption.set_status(account, key, "0")
                    else:
                        response = ("Valid presences: online, away, chat, dnd, "
                                    "offline, xa")
                case _ if command_lowercase.startswith("set status on"):
                    key = command[14:]
                    if key in ("online", "away", "chat", "dnd", "offline", "xa"):
                        response = await UtilityOption.set_status(account, key, "1")
                    else:
                        response = ("Valid presences: online, away, chat, dnd, "
                                    "offline, xa")
                case _ if command_lowercase.startswith("subscription remove"):
                    ix_url = command[20:]
                    ix_url = ix_url.split(" ")
                    response = await UtilitySubscription.unsubscribe(account, ix_url)
                case _ if command_lowercase.startswith("subscription rename"):
                    response = await UtilitySubscription.rename(account, command)
                case _ if command_lowercase.startswith("subscription reset"):
                    ix_url = command[19:]
                    if ix_url:
                        ix_url = ix_url.split(" ")
                        response = await UtilityDatabase.mark(account, ix_url)
                    else:
                        response = "Subscription index or URI is required."
                case "subscriptions reset":
                    response = await UtilityDatabase.mark(account)
                case _ if command_lowercase.startswith("subscription status disable"):
                    feed_id = command[28:]
                    response = await UtilityOption.feed_disable(account, feed_id)
                    #XmppStatusTask.restart_task(xmpp_instance, account)
                case _ if command_lowercase.startswith("subscription status enable"):
                    feed_id = command[27:]
                    response = await UtilityOption.feed_enable(account, feed_id)
                case _:
                    response = UtilityInformation.print_unknown()
            return response
