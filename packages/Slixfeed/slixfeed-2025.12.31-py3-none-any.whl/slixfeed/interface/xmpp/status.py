#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from slixfeed.interface.xmpp.presence import XmppPresence
from slixfeed.sqlite.general import SQLiteGeneral
from slixfeed.utility.account import accounts
from slixfeed.utility.logger import UtilityLogger
from slixfeed.utility.task import UtilityTask
import sys

logger = UtilityLogger(__name__)

class XmppStatus:

    def send_status_message(xmpp_instance, jid_bare):
        """
        Send status message.
    
        Parameters
        ----------
        jid : str
            Jabber ID.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        #if xmpp_instance.is_component:
        #    if last_update:
        #        presence_status = "chat"
        #        presence_body = f"📰 Last updated: {last_update}"
        #    else:
        #        presence_status = "xa"
        #        presence_body = f"️🗞️ No recorded updates."
        config_account = accounts.retrieve(jid_bare)
        #if not xmpp_instance.roster[xmpp_instance.boundjid.bare][jid_bare]["to"]:
        #    presence_status = "away"
        #    presence_body = "✒️ Please share your status to start service."
        if config_account.settings["enabled"]:
            jid_task = config_account.tasks_pending
            if jid_task and len(jid_task):
                presence_status = "dnd"
                presence_body = jid_task[list(jid_task.keys())[0]]
            else:
                db_file = config_account.database
                feeds = SQLiteGeneral.get_number_of_items(db_file, "feeds_properties")
                if not feeds:
                    presence_status = "available"
                    presence_body = "📪️ Send a link of a journal or torrent site."
                else:
                    unread = SQLiteGeneral.get_number_of_entries_unread(db_file)
                    if unread:
                        presence_status = "chat"
                        presence_body = f"📬️ {unread} news items."
                    else:
                        presence_status = "away"
                        presence_body = "📭️ No news."
        else:
            presence_status = "xa"
            presence_body = "📪️ Send \"service start\" to receive updates."
        XmppPresence.send(xmpp_instance, jid_bare, presence_body,
                          presence_show=presence_status)
        logger.debug(f"{function_name}	{jid_bare}	Finish")

class XmppStatusTask:

    async def looper(xmpp_instance, jid_bare):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        while True:
            XmppStatus.send_status_message(xmpp_instance, jid_bare)
            await asyncio.sleep(60 * 90)

    def restart_task(xmpp_instance, jid_bare):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        config_account = accounts.retrieve(jid_bare)
        UtilityTask.stop(config_account.tasks_manager, "status")
        config_account.tasks_manager["status"] = asyncio.create_task(
            XmppStatusTask.looper(xmpp_instance, jid_bare))
        logger.debug(f"{function_name}	{jid_bare}	Finish")
