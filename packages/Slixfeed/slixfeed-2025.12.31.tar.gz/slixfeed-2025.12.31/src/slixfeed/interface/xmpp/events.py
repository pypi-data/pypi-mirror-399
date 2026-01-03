#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# TODO
# Send message that database will be deleted within 30 days
# Check whether JID is in bookmarks or roster
# If roster, remove contact JID into file 
# If bookmarks, remove groupchat JID into file 

import asyncio
from random import randrange
from slixfeed.configuration.profile import profile
from slixfeed.configuration.singleton import configurations
from slixfeed.interface.xmpp.activity import XmppActivity
from slixfeed.interface.xmpp.adhoc import XmppAdHoc
from slixfeed.interface.xmpp.avatar import XmppAvatar
from slixfeed.interface.xmpp.block import XmppBlock
from slixfeed.interface.xmpp.capabilities import XmppEntityCapabilities
from slixfeed.interface.xmpp.chat import XmppChat, XmppChatTask
from slixfeed.interface.xmpp.disco import XmppServiceDiscovery
from slixfeed.interface.xmpp.message import XmppMessage
from slixfeed.interface.xmpp.mood import XmppMood
from slixfeed.interface.xmpp.muc import XmppMuc
from slixfeed.interface.xmpp.presence import XmppPresence
from slixfeed.interface.xmpp.publish import XmppPubsub, XmppPubsubTask
from slixfeed.interface.xmpp.roster import XmppRoster
from slixfeed.interface.xmpp.status import XmppStatus, XmppStatusTask
from slixfeed.interface.xmpp.utilities import XmppUtilities
from slixfeed.interface.xmpp.vcard import XmppVCard
#from slixfeed.main import interface_instance as xmpp_instance
from slixfeed.sqlite.general import SQLiteGeneral
from slixfeed.sqlite.subscribers import SQLiteSubscribers
from slixfeed.utility.account import accounts
from slixfeed.utility.logger import UtilityLogger
from slixfeed.utility.miscellaneous import UtilityMiscellaneous
from slixfeed.utility.selectors import UtilitySelectors
from slixfeed.utility.subscription import UtilitySubscriptionTask
from slixfeed.utility.task import UtilityTask
from slixfeed.version import __version__
from slixmpp import JID
#from slixmpp.stanza.iq import Iq
import sys
#import time

# time_now = datetime.now()
# time_now = time_now.strftime("%H:%M:%S")

# def print_time():
#     # return datetime.now().strftime("%H:%M:%S")
#     now = datetime.now()
#     current_time = now.strftime("%H:%M:%S")
#     return current_time

logger = UtilityLogger(__name__)

class XmppEvents:

    async def calibrate_status_message(xmpp_instance, message):
        function_name = sys._getframe().f_code.co_name
        jid_bare = message["from"].bare
        if jid_bare == xmpp_instance.boundjid.bare: return
        jid_type = await XmppUtilities.get_chat_type(xmpp_instance, jid_bare)
        if jid_type in ("gateway", "groupchat"): return
        logger.debug(f"{function_name}	{jid_bare}	Start")
        #await asyncio.sleep(1)
        if message["type"] in ("chat", "normal"):
            XmppStatusTask.restart_task(xmpp_instance, jid_bare)

    async def on_presence_error(xmpp_instance, presence):
        function_name = sys._getframe().f_code.co_name
        jid_bare = presence["from"].bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        presence_error_condition = presence["error"]["condition"]
        logger.warning(f"{function_name}	{jid_bare}	{presence_error_condition}")

    async def on_got_offline(xmpp_instance, presence):
        function_name = sys._getframe().f_code.co_name
        jid_bare = presence["from"].bare
        if jid_bare == xmpp_instance.boundjid.bare: return
        jid_type = await XmppUtilities.get_chat_type(xmpp_instance, jid_bare)
        if jid_type in ("gateway", "groupchat"): return
        logger.debug(f"{function_name}	{jid_bare}	Start")
        config_account = accounts.retrieve(jid_bare)
        print(f"X on_got_offline {jid_bare}")
        for task in ("check", "interval", "status"):
            UtilityTask.stop(config_account.tasks_manager, task)

    async def on_changed_status(xmpp_instance, presence):
        jid = presence["from"]
        function_name = sys._getframe().f_code.co_name
        jid_bare = jid.bare
        jid_host = jid.host
        jid_resource = jid.resource
        if jid_bare == xmpp_instance.boundjid.bare: return
        if not jid_resource: return
        jid_type = await XmppUtilities.get_chat_type(xmpp_instance, jid_bare)
        if jid_type in ("gateway", "groupchat"): return
        logger.debug(f"{function_name}	{jid_bare}	Start")
        # await task.check_readiness(xmpp_instance, presence)
        presence_show = presence["show"]
        config_account = accounts.retrieve(jid_bare)
        #db_file = config_account.database
        approved = UtilitySelectors.is_approved(jid_bare, jid_host)
        status_type = f"status_{presence_show}" if presence_show else "status_online"
        if not approved:
            print(f"X on_changed_status_1 {jid_bare}")
            for task in ("check", "interval", "status"):
                UtilityTask.stop(config_account.tasks_manager, task)
            for presence_type in ("unsubscribe", "unsubscribed"):
                XmppPresence.subscription(xmpp_instance, jid_bare, presence_type)
            if jid_bare in xmpp_instance.client_roster:
                iq = await XmppRoster.remove_contact(xmpp_instance, jid)
            presence_status = "xa"
            presence_body = "⛔ Service denied."
            XmppPresence.send(
                xmpp_instance,
                jid_bare,
                presence_body,
                presence_show=presence_status)
        elif (config_account.settings[status_type] and
              config_account.settings["enabled"]):
            XmppChatTask.restart_task(xmpp_instance, jid_bare)
            #UtilitySubscriptionTask.restart_task(jid_bare)
        else:
            print(f"X on_changed_status_2 {jid_bare}")
            UtilityTask.stop(config_account.tasks_manager, "interval")

    async def on_presence_available(xmpp_instance, presence):
        jid = presence["from"]
        function_name = sys._getframe().f_code.co_name
        jid_bare = jid.bare
        jid_host = jid.host
        jid_resource = jid.resource
        if jid_bare == xmpp_instance.boundjid.bare: return
        if not jid_resource: return
        jid_type = await XmppUtilities.get_chat_type(xmpp_instance, jid_bare)
        if jid_type in ("gateway", "groupchat"): return
        logger.debug(f"{function_name}	{jid_bare}	Start")
        # await task.check_readiness(xmpp_instance, presence)
        #presence_show = presence["show"]
        config_account = accounts.retrieve(jid_bare)
        #db_file = config_account.database
        approved = UtilitySelectors.is_approved(jid_bare, jid_host)
        #status_type = f"status_{presence_show}" if presence_show else "status_online"
        if not approved:
            print(f"X on_presence_available_1 {jid_bare}")
            for task in ("check", "interval", "status"):
                UtilityTask.stop(config_account.tasks_manager, task)
            for presence_type in ("unsubscribe", "unsubscribed"):
                XmppPresence.subscription(xmpp_instance, jid_bare, presence_type)
            if jid_bare in xmpp_instance.client_roster:
                iq = await XmppRoster.remove_contact(xmpp_instance, jid)
            presence_status = "xa"
            presence_body = "⛔ Service denied."
            XmppPresence.send(
                xmpp_instance,
                jid_bare,
                presence_body,
                presence_show=presence_status)
        elif (config_account.settings["status_online"] and
              config_account.settings["enabled"]):
            XmppChatTask.restart_task(xmpp_instance, jid_bare)
            #UtilitySubscriptionTask.restart_task(jid_bare)
        else:
            print(f"X on_presence_available_2 {jid_bare}")
            UtilityTask.stop(config_account.tasks_manager, "interval")

    def on_command(xmpp_instance, iq):
        function_name = sys._getframe().f_code.co_name
        jid_bare = iq["from"].bare
        action = iq["command"]["action"]
        node = iq["command"]["node"]
        presence_status = "dnd"
        presence_body = f"🎛 {action.capitalize()} Ad-Hoc Command: {node.capitalize()}."
        XmppPresence.send(
            xmpp_instance,
            jid_bare,
            presence_body,
            presence_show=presence_status)

    async def on_chatstate_active(xmpp_instance, message):
        function_name = sys._getframe().f_code.co_name
        jid = message["from"]
        jid_bare = jid.bare
        jid_host = jid.host
        if jid_bare == xmpp_instance.boundjid.bare: return
        jid_type = await XmppUtilities.get_chat_type(xmpp_instance, jid_bare)
        if jid_type == "gateway": return
        logger.debug(f"{function_name}	{jid_bare}	Start")
        approved = UtilitySelectors.is_approved(jid_bare, jid_host)
        config_account = accounts.retrieve(jid_bare)
        if not approved:
            print(f"X on_chatstate_active {jid_bare}")
            for task in ("check", "interval", "status"):
                UtilityTask.stop(config_account.tasks_manager, task)
            for presence_type in ("unsubscribe", "unsubscribed"):
                XmppPresence.subscription(xmpp_instance, jid_bare, presence_type)
            if jid_bare in xmpp_instance.client_roster:
                iq = await XmppRoster.remove_contact(xmpp_instance, jid)
            presence_status = "xa"
            presence_body = "⛔ Service denied."
            XmppPresence.send(
                xmpp_instance,
                jid_bare,
                presence_body,
                presence_show=presence_status)
        else:
            if message["type"] in ("chat", "normal"):
                await asyncio.sleep(1)
                XmppStatus.send_status_message(xmpp_instance, jid_bare)

    async def on_chatstate_composing(xmpp_instance, message):
        function_name = sys._getframe().f_code.co_name
        jid = message["from"]
        jid_bare = jid.bare
        jid_host = jid.host
        if jid_bare == xmpp_instance.boundjid.bare: return
        jid_type = await XmppUtilities.get_chat_type(xmpp_instance, jid_bare)
        if jid_type == "gateway": return
        logger.debug(f"{function_name}	{jid_bare}	Start")
        approved = UtilitySelectors.is_approved(jid_bare, jid_host)
        config_account = accounts.retrieve(jid_bare)
        if not approved:
            print(f"X on_chatstate_composing {jid_bare}")
            for task in ("check", "interval", "status"):
                UtilityTask.stop(config_account.tasks_manager, task)
            for presence_type in ("unsubscribe", "unsubscribed"):
                XmppPresence.subscription(xmpp_instance, jid_bare, presence_type)
            if jid_bare in xmpp_instance.client_roster:
                iq = await XmppRoster.remove_contact(xmpp_instance, jid)
            presence_status = "xa"
            presence_body = "⛔ Service denied."
            XmppPresence.send(
                xmpp_instance,
                jid_bare,
                presence_body,
                presence_show=presence_status)
        elif message["type"] in ("chat", "normal"):
            presence_status = "chat"
            message_body = [
                "🛟 Send command \"help\" for manual.",
                "💡 Send command \"info\" for information."]
            presence_body = message_body[randrange(2)]
            XmppPresence.send(
                xmpp_instance,
                jid_bare,
                presence_body,
                presence_show=presence_status)
            await asyncio.sleep(5)

    async def on_connection_failed(xmpp_instance, event):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        message = f"Connection has failed.  Reason: {event}"
        logger.warning(f"{function_name}		{message}")

    # NOTE Disco event disrupts status message.
    #      Tested with Gajim. It might be different with Psi.
    async def on_disco_info(xmpp_instance, DiscoInfo):
        function_name = sys._getframe().f_code.co_name
        jid = DiscoInfo["from"]
        jid_bare = jid.bare
        jid_host = jid.host
        if jid_bare == xmpp_instance.boundjid.bare: return
        # NOTE Querying JID type would result in constant negotiations.
        #jid_type = await XmppUtilities.get_chat_type(xmpp_instance, jid_bare)
        #if jid_type == "gateway": return
        logger.debug(f"{function_name}	{jid_bare}	Start")
        approved = UtilitySelectors.is_approved(jid_bare, jid_host)
        if (approved and
            xmpp_instance.roster[xmpp_instance.boundjid.bare][jid_bare]["to"]):
            await XmppEntityCapabilities.update_capabilities(xmpp_instance,
                                                             jid.full)

    async def join_to_groupchat(xmpp_instance, message):
        function_name = sys._getframe().f_code.co_name
        jid = message["from"]
        jid_bare = jid.bare
        jid_host = jid.host
        logger.debug(f"{function_name}	{jid_bare}	Start")
        room = message["groupchat_invite"]["jid"]
        jid_type = await XmppUtilities.get_chat_type(xmpp_instance, room)
        if jid_type == "groupchat":
            room_split = room.split("@")
            room_host = room_split[1] if room_split else room
            approved_account = UtilitySelectors.is_approved(jid_bare, jid_host)
            approved_group = UtilitySelectors.is_approved(room, room_host)
            if not approved_account:
                for presence_type in ("unsubscribe", "unsubscribed"):
                    XmppPresence.subscription(xmpp_instance, jid_bare, presence_type)
                presence_status = "xa"
                presence_body = "⛔ Service denied."
                XmppPresence.send(
                    xmpp_instance,
                    jid_bare,
                    presence_body,
                    presence_show=presence_status)
            elif not approved_group:
                message_body = f"Group chat {room} is not approved."
                XmppMessage.send(xmpp_instance, jid_bare, message_body, "chat")
                logger.warning(f"{function_name}	{jid_bare}	{message_body}")
            else:
                result = await XmppMuc.enter(xmpp_instance, room)
                if result == "ban":
                    message_body = f"Slixfeed is banned from {room}"
                    XmppMessage.send(xmpp_instance, jid_bare, message_body, "chat")
                    logger.warning(f"{function_name}	{jid_bare}	{message_body}")
                else:
                    db_file = configurations.database_address_book
                    address_id = SQLiteSubscribers.get_index_of_an_address(
                        db_file, room)
                    if not address_id:
                        await SQLiteSubscribers.insert_an_address(db_file, room)
                        address_id = SQLiteSubscribers.get_index_of_an_address(
                            db_file, room)
                        kind_id = SQLiteSubscribers.get_index_of_a_kind(db_file, "muc")
                        protocol_id = SQLiteSubscribers.get_index_of_a_protocol(
                            db_file, "xmpp")
                        await SQLiteSubscribers.associate_kind_and_protocol_with_an_address(
                            db_file, address_id, kind_id, protocol_id)
                    else:
                       pass # TODO Update address type to MUC or remove and insert.
                    XmppStatusTask.restart_task(xmpp_instance, room)
                    XmppChatTask.restart_task(xmpp_instance, room)
                    UtilitySubscriptionTask.restart_task(room)
        else:
            message_body = (f"Jabber ID {room} does not appear to be a "
                            "supported group chat.")
            XmppMessage.send(xmpp_instance, jid_bare, message_body, "chat")

    # NOTE Change activity to reading for a few seconds.
    async def on_message(xmpp_instance, message):
        function_name = sys._getframe().f_code.co_name
        jid = message["from"]
        jid_bare = jid.bare
        jid_host = jid.host
        jid_type = await XmppUtilities.get_chat_type(xmpp_instance, jid_bare)
        if jid_type == "gateway": return
        #if jid_bare == xmpp_instance.boundjid.bare: return
        logger.debug(f"{function_name}	{jid_bare}	Start")
        approved = UtilitySelectors.is_approved(jid_bare, jid_host)
        config_account = accounts.retrieve(jid_bare)
        if jid_bare == xmpp_instance.boundjid.bare:
            presence_status = "dnd"
            presence_body = "⚠ Slixfeed does not interact with itself."
            XmppPresence.send(
                xmpp_instance,
                jid_bare,
                presence_body,
                presence_show=presence_status)
        elif not approved:
            print(f"X on_message_1 {jid_bare}")
            for task in ("check", "interval", "status"):
                UtilityTask.stop(config_account.tasks_manager, task)
            for presence_type in ("unsubscribe", "unsubscribed"):
                XmppPresence.subscription(xmpp_instance, jid_bare, presence_type)
            if jid_bare in xmpp_instance.client_roster:
                iq = await XmppRoster.remove_contact(xmpp_instance, jid)
            message_body = "Service denied. Please contact an operator."
            presence_status = "xa"
            presence_body = "⛔ Service denied."
            XmppMessage.send(xmpp_instance, jid_bare, message_body, "chat")
            XmppPresence.send(
                xmpp_instance,
                jid_bare,
                presence_body,
                presence_show=presence_status)
            await XmppBlock.block(xmpp_instance, jid_bare)
        elif (configurations.interface == "xmpp-client" and
              not message.get_plugin("muc", check=True) and
              message["type"] in ("chat", "normal") and
              not xmpp_instance.roster[xmpp_instance.boundjid.bare][jid_bare]["to"]):
            print(f"X on_message_2 {jid_bare}")
            for task in ("check", "interval", "status"):
                UtilityTask.stop(config_account.tasks_manager, task)
            message_body = "Please share your status to start service."
            presence_status = "away"
            presence_body = "✒️ Please share your status to start service."
            XmppMessage.send(xmpp_instance, jid_bare, message_body, "chat")
            XmppPresence.send(
                xmpp_instance,
                jid_bare,
                presence_body,
                presence_show=presence_status)
        else:
            #jid_type = await XmppUtilities.get_chat_type(xmpp_instance, jid_bare)
            #if jid_type not in ("error", "chat"): breakpoint()
            #if (not message.get_plugin("muc", check=True) and
            #    message["type"] in ("chat", "normal") and
            #    not xmpp_instance.roster[xmpp_instance.boundjid.bare][jid_bare]["from"]):
            #    for presence_type in ("subscribe", "subscribed"):
            #        XmppPresence.subscription(xmpp_instance, jid_bare, presence_type)
            await XmppChat.process_message(xmpp_instance, message)
        # chat_type = message["type"]
        # message_body = message["body"]
        # message_reply = message.reply

#    def on_reactions(xmpp_instance, message):
#        logger.info(message["from"])
#        logger.info(message["reactions"]["values"])

    def on_session_end(xmpp_instance, event):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        message = "Session has ended."
        logger.warning(f"{function_name}		{message}")

    async def unblock_accounts(xmpp_instance, event):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        iq = await XmppBlock.get_blocked(xmpp_instance)
        if iq:
            items = iq["blocklist"]["items"]
            for item in items:
                jid = JID(item["jid"])
                jid_bare = jid.bare
                jid_host = jid.host
                approved = UtilitySelectors.is_approved(jid_bare, jid_host)
                if approved: await XmppBlock.unblock(xmpp_instance, jid_bare)

    def set_commands(xmpp_instance, event):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        
        # TODO Iterate xmpp_instance.blacklist and add JIDs to Privacy List

        # NOTE Advertise a different set of commands to operators.
        # https://codeberg.org/poezio/slixmpp/issues/3515
        # if XmppUtilities.is_operator(jid_bare):
        XmppAdHoc.commands(xmpp_instance)

    def status_message(xmpp_instance, event):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        xmpp_instance.send_presence(pstatus="📜️ Slixfeed news service.")
        presence_body = f"💿 Slixfeed version {__version__}"
        for operator in profile.operators["xmpp"]:
            XmppPresence.send(xmpp_instance, operator["address"], presence_body)

    async def set_identity(xmpp_instance, event):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        photo = UtilityMiscellaneous.get_photo(configurations.directory_config)
        if photo:
            await XmppAvatar.set_photo(xmpp_instance, photo)
        else:
            logger.warning(f"{function_name}		No photo detected.")
        vcard = profile.vcard
        await XmppVCard.set_vcard(xmpp_instance, vcard)
        await XmppServiceDiscovery.set_identity(xmpp_instance, "client", "bot",
                                                xmpp_instance.boundjid.full,
                                                "en", "slixfeed")
        await XmppServiceDiscovery.set_identity(xmpp_instance, "headline", "rss",
                                                xmpp_instance.boundjid.full,
                                                "en", "slixfeed")
        await XmppActivity.publish(xmpp_instance, "working", "writing",
                                   "Distributing and publishing news")
        await XmppMood.publish(xmpp_instance, "creative")
        await XmppEntityCapabilities.update_capabilities(xmpp_instance)

    async def calibrate_roster(xmpp_instance, event):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        await xmpp_instance.get_roster()
        for jid_bare in xmpp_instance.roster[xmpp_instance.boundjid.bare]:
            #jid_type = await XmppUtilities.get_chat_type(xmpp_instance, jid_bare)
            subscription_from = xmpp_instance.roster[xmpp_instance.boundjid.bare][jid_bare]["from"]
            subscription_to = xmpp_instance.roster[xmpp_instance.boundjid.bare][jid_bare]["to"]
            if subscription_from and subscription_to:
                XmppStatusTask.restart_task(xmpp_instance, jid_bare)
                UtilitySubscriptionTask.restart_task(jid_bare)
            elif not subscription_from and not subscription_to:
                for presence_type in ("subscribe", "subscribed"):
                    XmppPresence.subscription(xmpp_instance, jid_bare, presence_type)
            elif not subscription_from:
                XmppPresence.subscription(xmpp_instance, jid_bare, "subscribe")
            elif not subscription_to:
                XmppPresence.subscription(xmpp_instance, jid_bare, "subscribed")
                #XmppStatusTask.restart_task(xmpp_instance, jid_bare)
                #UtilitySubscriptionTask.restart_task(jid_bare)

    async def join_to_groupchats(xmpp_instance, event):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        # Join to group chats
        await asyncio.sleep(5)
        db_file = configurations.database_address_book
        for address in SQLiteSubscribers.get_addresses_of_kind_and_protocol(
            db_file, "muc", "xmpp"):
            jid_bare = address[0]
            result = await XmppMuc.enter(xmpp_instance, jid_bare)
            match result:
                case "ban":
                    logger.warning(f"{function_name}	{jid_bare}	Banned from group.")
                case "error":
                    logger.warning(f"{function_name}	{jid_bare}	An error occured.")
                case "timeout":
                    logger.warning(f"{function_name}	{jid_bare}	Timeout reached.")
                case _:
                    logger.info(f"{function_name}	{jid_bare}	Joined to group chat.")
                    XmppStatusTask.restart_task(xmpp_instance, jid_bare)
                    XmppChatTask.restart_task(xmpp_instance, jid_bare)
                    UtilitySubscriptionTask.restart_task(jid_bare)

    async def start_pubsub_service(xmpp_instance, event):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        await xmpp_instance.get_roster()
        for operator in profile.operators["pubsub"]:
            jid_bare = operator["address"]
            presence_body = f"📰 Slixfeed PubSub Mode."
            XmppPresence.send(xmpp_instance, jid_bare, presence_body)
            if not xmpp_instance.roster[xmpp_instance.boundjid.bare][jid_bare]["to"]:
                XmppPresence.subscription(xmpp_instance, jid_bare, "subscribed")

        # Iterate PubSub services
#        db_file = configurations.database_address_book
#        for address in SQLiteGeneral.get_addresses_of_kind_and_protocol(db_file,
#                                                                        "pubsub",
#                                                                        "xmpp"):
#            jid_bare = address[0]

        # Publish items to PubSub nodes
        for result in await XmppPubsub.get_pubsub_services(xmpp_instance):
            jid_bare = result["jid"]
            UtilitySubscriptionTask.restart_task(jid_bare)
            await asyncio.sleep(60 * 5)
            XmppPubsubTask.restart_task(xmpp_instance, jid_bare)

    async def service_close(xmpp_instance, presence):
        function_name = sys._getframe().f_code.co_name
        jid = presence["from"]
        jid_bare = jid.bare
        jid_host = jid.host
        if jid_bare == xmpp_instance.boundjid.bare: return
        logger.debug(f"{function_name}	{jid_bare}	Start")
        for presence_type in ("unsubscribe", "unsubscribed"):
            XmppPresence.subscription(xmpp_instance, jid_bare, presence_type)
        if jid_bare in xmpp_instance.client_roster:
            iq = await XmppRoster.remove_contact(xmpp_instance, jid)
        approved = UtilitySelectors.is_approved(jid_bare, jid_host)
        presence_status = "xa"
        if approved:
            config_account = accounts.retrieve(jid_bare)
            print(f"X service_close {jid_bare}")
            for task in ("check", "interval", "status"):
                UtilityTask.stop(config_account.tasks_manager, task)
            message_body = "News service has been deactivated."
            XmppMessage.send(xmpp_instance, jid_bare, message_body, "chat")
            presence_body = "🖋️ You have been unsubscribed."
            XmppPresence.send(
                xmpp_instance,
                jid_bare,
                presence_body,
                presence_show=presence_status)
            await asyncio.sleep(5)
        presence_body = "📜️ Schapps Slixfeed news service."
        XmppPresence.send(
            xmpp_instance,
            jid_bare,
            presence_body,
            presence_show=presence_status)

    async def service_open(xmpp_instance, presence):
        function_name = sys._getframe().f_code.co_name
        jid = presence["from"]
        jid_bare = jid.bare
        jid_host = jid.host
        if jid_bare == xmpp_instance.boundjid.bare: return
        jid_type = await XmppUtilities.get_chat_type(xmpp_instance, jid_bare)
        if jid_type == "gateway": return
        logger.debug(f"{function_name}	{jid_bare}	Start")
        approved = UtilitySelectors.is_approved(jid_bare, jid_host)
        if approved:
            if jid_bare not in xmpp_instance.client_roster:
                await XmppRoster.add_contact(xmpp_instance, jid_bare)
            #jid_type = await XmppUtilities.get_chat_type(xmpp_instance, jid_bare)
            if not xmpp_instance.roster[xmpp_instance.boundjid.bare][jid_bare]["from"]:
                for presence_type in ("subscribe", "subscribed"):
                    XmppPresence.subscription(xmpp_instance, jid_bare, presence_type)
            iq = await xmpp_instance.get_roster()
            if xmpp_instance.roster[xmpp_instance.boundjid.bare][jid_bare]["to"]:
                message_body = "Slixfeed has been activated."
                presence_body = "📫️ Slixfeed has been activated."
            else:
                config_account = accounts.retrieve(jid_bare)
                print(f"X service_open {jid_bare}")
                for task in ("check", "interval", "status"):
                    UtilityTask.stop(config_account.tasks_manager, task)
                message_body = "Please share your status to start service."
                presence_body = "✒️ Please share your status to start service."
            presence_status = "chat"
            XmppPresence.send(
                xmpp_instance,
                jid_bare,
                presence_body,
                presence_show=presence_status)
            XmppMessage.send(xmpp_instance, jid_bare, message_body, "chat")
            await asyncio.sleep(5)
        else:
            for presence_type in ("unsubscribe", "unsubscribed"):
                XmppPresence.subscription(xmpp_instance, jid_bare, presence_type)
            if jid_bare in xmpp_instance.client_roster:
                iq = await XmppRoster.remove_contact(xmpp_instance, jid)
            presence_status = "xa"
            presence_body = "⛔ Service denied."
            XmppPresence.send(
                xmpp_instance,
                jid_bare,
                presence_body,
                presence_show=presence_status)
            message_subject_alert = "Subscription request"
            message_body_alert = (f"Subscription for Jabber ID xmpp:{jid_bare} "
                                  "was denied.")
            for operator in profile.operators["xmpp"]:
                XmppMessage.send_headline(
                    xmpp_instance,
                    operator["address"],
                    message_subject_alert,
                    message_body_alert,
                    "chat")
