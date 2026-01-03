#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from slixfeed.configuration.singleton import configurations
from slixfeed.interface.xmpp.muc import XmppMuc
from slixfeed.interface.xmpp.publish import XmppPubsub
from slixfeed.interface.xmpp.utilities import XmppUtilities
from slixfeed.utility.logger import UtilityLogger
from slixfeed.sqlite.general import SQLiteGeneral
import sys

logger = UtilityLogger(__name__)

class UtilityXmpp:

    async def pubsub_list(xmpp_instance, jid):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid}	Start")
        iq = await XmppPubsub.get_nodes(xmpp_instance, jid)
        message = ""
        for item in iq["disco_items"]:
            item_id = item["node"]
            item_name = item["name"]
            message += f"Name: {item_name}\nNode: {item_id}\n\n"
        return message

    async def muc_leave(xmpp_instance, jid_bare):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        db_file = configurations.address_book
        await SQLiteGeneral.delete_an_address(db_file, jid_bare)
        XmppMuc.leave(xmpp_instance, jid_bare)

    def node_delete(xmpp_instance, info):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        info = info.split(" ")
        if len(info) > 2:
            jid = info[0]
            nid = info[1]
            if jid:
                XmppPubsub.delete_node(xmpp_instance, jid, nid)
                message = f"Deleted node: {nid}"
            else:
                message = "PubSub JID is missing. Enter PubSub JID."
        else:
            message = "Missing argument. Enter JID and Node name."
        return message

    def node_purge(xmpp_instance, info):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        info = info.split(" ")
        if len(info) > 1:
            jid = info[0]
            nid = info[1]
            if jid:
                XmppPubsub.purge_node(xmpp_instance, jid, nid)
                message = f"Purged node: {nid}"
            else:
                message = "PubSub JID is missing. Enter PubSub JID."
        else:
            message = "Missing argument. Enter JID and Node name."
        return message

    def print_support_jid():
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        muc_jid = "slixfeed@chat.woodpeckersnest.space"
        message = f"Join xmpp:{muc_jid}?join"
        return message

    # TODO Atomize xep_0045
    async def invite_jid_to_muc(xmpp_instance, jid_bare):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        muc_jid = "slixfeed@chat.woodpeckersnest.space"
        if await XmppUtilities.get_chat_type(xmpp_instance, jid_bare) == "chat":
            # TODO Move this instruction to module XmppMuc
            xmpp_instance.plugin["xep_0045"].invite(muc_jid, jid_bare)
