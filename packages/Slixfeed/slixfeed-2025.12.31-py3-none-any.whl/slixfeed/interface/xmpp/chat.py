#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

TODO

2) Set timeout for moderator interaction.
   If moderator interaction has been made, and moderator approves the bot, then
   the bot will add the given groupchat to bookmarks; otherwise, the bot will
   send a message that it was not approved and therefore leaves the groupchat.

3) If subscription is inadequate (see XmppPresence.request), send a message that says so.

"""

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
from slixfeed.utility.command import UtilityCommand
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

try:
    from slixfeed.interface.xmpp.encryption import XmppOmemo
except Exception as e:
    logger.critical("		Encryption of type OMEMO could not be enabled.  Reason: " + str(e))

    # for task in main_task:
    #     task.cancel()

    # Deprecated in favour of event "presence_available"
    # if not main_task:
    #     await select_file()

class XmppChat:

    async def process_message(
        xmpp_instance, message: Message, allow_untrusted: bool = False) -> None:
        """
        Process incoming message stanzas. Be aware that this also
        includes MUC messages and error messages. It is usually
        a good practice to check the messages"s type before
        processing or sending replies.

        Parameters
        ----------
        message : str
            The received message stanza. See the documentation
            for stanza objects and the Message stanza to see
            how it may be used.
        """
        function_name = sys._getframe().f_code.co_name
        jid = message["from"]
        jid_bare = jid.bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        jid_full = jid.full
        message_type = message["type"]
        if message_type in ("chat", "groupchat", "normal"):
            function_name = sys._getframe().f_code.co_name
            logger.debug(f"{function_name}	{jid_bare}	Start")
            message_body = message["body"]
            command = " ".join(message_body.split())
            if (xmpp_instance.omemo_present and
                xmpp_instance["xep_0384"].is_encrypted(message)):
                command, omemo_decrypted = await XmppOmemo.decrypt(
                    xmpp_instance, message)
            else:
                omemo_decrypted = None
            # Check whether message is of MUC.
            if message.get_plugin("muc", check=True) or message["mucroom"]:
            #if message["mucnick"] and message["mucroom"]:
                if message["muc"]["invite"]["from"].jid: return
                alias = message["muc"]["nick"]
                self_alias = XmppMuc.get_self_alias(xmpp_instance, jid_bare)
                if (alias != self_alias and
                    # Serve occupants who are moderators.
                    XmppUtilities.is_moderator(xmpp_instance, jid_bare, alias)):
                    permitted = True
                    if message_type == "groupchat":
                        if UtilityText.message_starts_with_alias(
                            message_body, self_alias):
                            # NOTE Adding one to the length because a character
                            #      (colon, comma, dot, or white-space) was added.
                            self_alias_length = len(self_alias) + 1
                            command = command[self_alias_length:].lstrip()
                        else:
                            permitted = False
                            return
                else:
                    permitted = False
                    return

            presence_status, presence_body = UtilityCommand.message(command)

            if message:
                config_account = accounts.retrieve(jid_bare)
                UtilityTask.stop(config_account.tasks_manager, "status")
                pending_tasks_num = randrange(10000, 99999)
                config_account.tasks_pending[pending_tasks_num] = presence_body

            response = None
            command_lowercase = command.lower()
            match command_lowercase:
                case "support":
                    response = UtilityXmpp.print_support_jid()
                    # NOTE Invitation does not seem to work.
                    #await UtilityXmpp.invite_jid_to_muc(xmpp_instance, jid_bare)
                case _ if command_lowercase.startswith("set interval"):
                    XmppChatTask.restart_task(xmpp_instance, jid_bare)
                    response = await UtilityCommand.action(jid_bare, command)
                case _ if command_lowercase.startswith("export"):
                    ext = command[7:]
                    if not ext: ext = "opml"
                    if ext in ("gmi", "md", "opml"): # html xbel
                        pathname, response = UtilitySubscription.export(jid_bare, ext)
                        encrypt_omemo = config_account.settings["omemo"]
                        encrypted = True if encrypt_omemo else False
                        url = await XmppUpload.start(
                            xmpp_instance, jid_bare, Path(pathname), encrypted=encrypted)
                        # response = (
                        #     f"Feeds exported successfully to {ex}.\n{url}"
                        #     )
                        # XmppMessage.send_oob_reply_message(message, url, response)
                        if url:
                            chat_type = await XmppUtilities.get_chat_type(
                                xmpp_instance, jid_bare)
                            if xmpp_instance.omemo_present and encrypted:
                                url_encrypted, omemo_encrypted = await XmppOmemo.encrypt(
                                    xmpp_instance, jid, "chat", url)
                                XmppMessage.send_omemo_oob(
                                    xmpp_instance, jid, url_encrypted, chat_type)
                            else:
                                XmppMessage.send_oob(
                                    xmpp_instance, jid_bare, url, chat_type)
                        else:
                            response = "OPML file export has been failed."
                        XmppStatusTask.restart_task(xmpp_instance, jid_bare)
                    else:
                        response = "Supported filetypes are gmi, md, and opml."
                case _ if command_lowercase.startswith("next"):
                    num = command[5:]
                    if num:
                        try:
                            num = int(num)
                            if num > 3: num = 3
                        except:
                            num = config_account.settings["amount"]
                            response = "Value must be a digit."
                    await XmppChatAction.send_unread_items(
                        xmpp_instance, jid_bare, chat_type=message_type, num=num)
                    XmppStatus.send_status_message(xmpp_instance, jid_bare)
                case "service close":
                    if XmppUtilities.is_operator(jid_bare):
                        #for account in available_accounts:
                        #    for task in ("check", "interval", "status"):
                        #        UtilityTask.stop(config_account.tasks_manager,
                        #                         task)
                        #from slixfeed.interface.xmpp.events import XmppEvents
                        #xmpp_instance.del_event_handler("session_end", XmppEvents.on_session_end)
                        xmpp_instance.task_ping_instance.cancel()
                        xmpp_instance.disconnect()
                        #await asyncio.get_event_loop().shutdown_asyncgens()
                        #asyncio.get_event_loop().run_until_complete(xmpp_instance.disconnected)
                        sys.exit()
                case "service start":
                    await asyncio.sleep(5)
                    callbacks = (XmppChatTask, XmppStatusTask)
                    response = await UtilitySchedule.start(
                        xmpp_instance, jid_bare, callbacks)
                case "service stop":
                    response = await UtilitySchedule.stop(jid_bare)
                case "service subscribe":
                    XmppPresence.subscription(
                        xmpp_instance, jid_bare, "subscribe")
                    XmppPresence.subscription(
                        xmpp_instance, jid_bare, "subscribed")
                case "service unsubscribe":
                    if message_type == "groupchat":
                        await UtilityXmpp.muc_leave(xmpp_instance, jid_bare)
                    else:
                        XmppPresence.subscription(
                            xmpp_instance, jid_bare, "unsubscribe")
                        XmppPresence.subscription(
                            xmpp_instance, jid_bare, "unsubscribed")
                case _ :
                    response = await UtilityCommand.action(jid_bare, command)

            if message:
                XmppPresence.send(xmpp_instance, jid_bare, presence_body,
                                  presence_show=presence_status)
                del config_account.tasks_pending[pending_tasks_num]
                XmppStatusTask.restart_task(xmpp_instance, jid_bare)

            # if response: message.reply(response).send()
            if response:
                encrypt_omemo = config_account.settings["omemo"]
                encrypted = True if encrypt_omemo else False
                if (xmpp_instance.omemo_present and encrypted and
                    xmpp_instance["xep_0384"].is_encrypted(message)):
                    response_encrypted, omemo_encrypted = await XmppOmemo.encrypt(
                        xmpp_instance, jid, "chat", response)
                    if omemo_decrypted and omemo_encrypted:
                        XmppMessage.send_omemo(xmpp_instance, jid,
                                               response_encrypted, message_type)
                        # XmppMessage.send_omemo_reply(xmpp_instance, message, response_encrypted)
                else:
                    XmppMessage.send_reply(message, response)

# TODO Move to module message.py
class XmppChatAction:

    # TODO Change this function to handle a single message.
    # Create another function to gather results, iterate and call to this function.
    async def send_unread_items(xmpp_instance, jid_bare: str,
                                chat_type: Optional[str] = None,
                                num: Optional[int] = None):
        """
        Send news items as messages.

        Parameters
        ----------
        jid_bare : str
            Jabber ID.
        num : str, optional
            Number. The default is None.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        logger.debug(f"{function_name}	{jid_bare}	Num: {num}")
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        encrypted = True if config_account.settings["omemo"] else False
        jid = JID(jid_bare)
        setting_document = config_account.settings["document"]
        setting_media = config_account.settings["media"]
        if not chat_type: chat_type = await XmppUtilities.get_chat_type(
            xmpp_instance, jid_bare)
        if not num: num = config_account.settings["amount"]
        results = SQLiteGeneral.retrieve_entries_properties_unread(db_file, num)
        for result in results:
            (entry_id, entry_identifier, entry_title,
             entry_link, entry_summary, feed_id) = result
            feed_title = SQLiteGeneral.get_feed_title(db_file, feed_id)
            message_content = XmppChatAction.list_unread_entries(
                xmpp_instance, entry_title, entry_summary, entry_link,
                feed_id, feed_title, jid_bare, entry_id)
            await XmppChatAction.send_content(
                xmpp_instance, jid_bare, message_content, chat_type, encrypted)
            if setting_document: await XmppChatAction.send_document(
                xmpp_instance, jid_bare, entry_identifier, entry_title,
                entry_link, chat_type, encrypted)
            if setting_media: await XmppChatAction.send_media(
                xmpp_instance, jid_bare, db_file, entry_id, chat_type, encrypted)
            await SQLiteGeneral.mark_as_read(db_file, entry_id)

    async def send_media(xmpp_instance, jid_bare: str, db_file: str,
                         entry_id: str, chat_type: str, encrypted: bool):
        # Find media
        # if entry_link.startswith("magnet:"):
        #     media = action.get_magnet(entry_link)
        # elif enclosure.startswith("magnet:"):
        #     media = action.get_magnet(enclosure)
        # elif enclosure:

        media_uri = None
        enclosure = SQLiteGeneral.get_enclosure_by_entry_id(db_file, entry_id)
        if enclosure:
            media_uri = enclosure
            # The purpose of this is to disqualify files larger than 10MB?
            # Perhaps it would be preferable to read from file system,
            # because the file is already stored on the system.
            # See OMEMO (line 722)
            if media_uri:
                """
                try:
                    http_headers = await RetrieverHttp.headers(media_uri)
                    if ("Content-Length" in http_headers and
                        int(http_headers["Content-Length"]) > 100000):
                        media_uri = None
                except Exception as e:
                    logger.error(f"{function_name}    {jid_bare}    {str(e)}")
                    media_uri = None
                """
                # Send media
                if xmpp_instance.omemo_present and encrypt_omemo:
                    filename = os.path.basename(media_uri)
                    pathname = os.path.join(configurations.directory_cache,
                                            filename)
                    # if not media_uri.startswith("data:"):
                    #filename = media_uri.split("/").pop().split("?")[0]
                    #if not filename: breakpoint()
                    # http_response = await Http.response(media_uri)
                    http_headers = await RetrieverHttp.headers(media_uri)
                    if ("Content-Length" in http_headers and
                        int(http_headers["Content-Length"]) < 3000000):
                        status = await RetrieverHttp.data(
                            media_uri, pathname=pathname, binary=True)
                        if status:
                            filesize = os.path.getsize(pathname)
                            media_uri_new = await XmppUpload.start(
                                xmpp_instance, jid_bare, Path(pathname),
                                filesize, encrypted=encrypted)
                        else:
                            media_uri_new = media_uri
                    else:
                        media_uri_new = media_uri
                    # else:
                    #     import io, base64
                    #     from PIL import Image
                    #     file_content = media_uri.split(",").pop()
                    #     file_extension = media_uri.split(";")[0].split(":").pop().split("/").pop()
                    #     img = Image.open(io.BytesIO(base64.decodebytes(bytes(file_content, "utf-8"))))
                    #     filename = "image." + file_extension
                    #     pathname = os.path.join(cache_dir, filename)
                    #     img.save(pathname)
                    #     filesize = os.path.getsize(pathname)
                    #     media_uri_new = await XmppUpload.start(
                    #         xmpp_instance, jid_bare, Path(pathname), filesize, encrypted=encrypted)
                    media_uri_new_encrypted, omemo_encrypted = await XmppOmemo.encrypt(
                        xmpp_instance, JID(jid_bare), "chat", media_uri_new)
                    if media_uri_new_encrypted and omemo_encrypted:
                        # NOTE Tested against Gajim.
                        # FIXME This only works with aesgcm URLs, and it does
                        # not work with http URLs.
                        # entry_link = saxutils.escape(entry_link)
                        # AttributeError: "Encrypted" object has no attribute "replace"
                        XmppMessage.send_omemo_oob(xmpp_instance, JID(jid_bare),
                                                  media_uri_new_encrypted,
                                                  chat_type)
                elif media_uri:
                    # NOTE Tested against Gajim.
                    # FIXME Handle data: URIs.
                    if media_uri.startswith("data:"):
                        http_headers = await RetrieverHttp.headers(media_uri)
                        if ("Content-Length" in http_headers and
                            int(http_headers["Content-Length"]) > 100000):
                            breakpoint()
                            XmppMessage.send_oob(xmpp_instance, jid_bare, media_uri,
                                                 chat_type)
                    else:
                        XmppMessage.send_oob(xmpp_instance, jid_bare, media_uri,
                                             chat_type)
        # See XEP-0367
        # if media:
        #     # message = xmpp.Slixfeed.make_message(
        #     #     xmpp_instance, mto=jid, mbody=new, mtype=chat_type)
        #     message = xmpp.Slixfeed.make_message(
        #         xmpp_instance, mto=jid, mbody=media, mtype=chat_type)
        #     message["oob"]["url"] = media
        #     message.send()

    async def send_document(
        xmpp_instance, jid_bare: str, entry_identifier: str, entry_title: str,
        entry_link: str, chat_type: str, encrypted: bool):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        #http_response = await RetrieverHttp.response(entry_link)
        #http_headers = await RetrieverHttp.headers(entry_link)
        #if ("Content-Length" in http_headers and
        #    int(http_headers["Content-Length"]) < 3000000):
        filename = entry_identifier + ".html"
        pathname_html = os.path.join(configurations.directory_cache,
                                filename)
        result = await RetrieverHttp.data(
            entry_link, pathname=pathname_html, binary=True)
        # TODO Cancel if binary (e.g. ODS, ODT, et cetera.)
        if not result["error"] and os.path.exists(pathname_html):
            try:
                content = open(pathname_html, "r").read()
                content_processed = UtilityArc90.process(content)
                # NOTE More filetypes.
                # b1cb9f77778d47a01811386d9d2808d789416e99/slixfeed/xmpp/process.py
                pathname_html_processed =  os.path.join(configurations.directory_cache,
                                                        filename + "-arc90.html")
                pathname_txt_processed =  os.path.join(configurations.directory_cache,
                                                      filename + "-arc90.txt")
                with open(pathname_html_processed, "w") as f: f.write(content_processed)
                #content_processed_parsed = UtilityHtml.parse(content_processed)
                #content_processed_mod = entry_title + "\n\n: " + entry_link + "\n\n" + content_processed_parsed
                #with open(pathname_txt_processed, "w") as f: f.write(content_processed_mod)
                #pathname_pdf_processed = UtilityContent.produce_pdf(content_processed_mod, pathname_txt_processed)
                pathname_file_to_send = pathname_html_processed
                filesize = os.path.getsize(pathname_file_to_send)
                entry_link_new = await XmppUpload.start(
                    xmpp_instance, jid_bare, Path(pathname_file_to_send),
                    filesize, encrypted=encrypted)
                if xmpp_instance.omemo_present and encrypt_omemo:
                    (entry_link_new_encrypted,
                      omemo_encrypted) = await XmppOmemo.encrypt(
                        xmpp_instance, JID(jid_bare), "chat", entry_link_new)
                    if entry_link_new_encrypted and omemo_encrypted:
                        XmppMessage.send_omemo_oob(
                            xmpp_instance, JID(jid_bare),
                            entry_link_new_encrypted, chat_type)
                    else:
                        logger.warning(f"{function_name}	{pathname_file_to_send}	File is not encrypted")
                        XmppMessage.send_oob(
                            xmpp_instance, jid_bare, entry_link_new, chat_type)
                else:
                    XmppMessage.send_oob(
                        xmpp_instance, jid_bare, entry_link_new, chat_type)
            except UnicodeDecodeError as e:
                logger.error(f"{function_name}	{entry_identifier}	{str(e)}")

    async def send_content(xmpp_instance, jid_bare: str, message_content: str,
                           chat_type: str, encrypted: bool):
            # TODO Conclude check "omemo_present" at singleton.
            if xmpp_instance.omemo_present and encrypt_omemo:
                message_content_encrypted, omemo_encrypted = await XmppOmemo.encrypt(
                    xmpp_instance, JID(jid_bare), "chat", message_content)
            if xmpp_instance.omemo_present and encrypt_omemo and omemo_encrypted:
                XmppMessage.send_omemo(xmpp_instance, JID(jid_bare),
                                       message_content_encrypted, chat_type)
            else:
                XmppMessage.send(xmpp_instance, jid_bare, message_content,
                                 chat_type)
                    
            # TODO Do not refresh task before
            # verifying that it was completed.

            # XmppStatusTask.restart_task(xmpp_instance, jid_bare)
            # UtilityGeneral.task_start(xmpp_instance, jid_bare, "interval")

    def list_unread_entries(
        xmpp_instance, title, summary, link, feed_id, feed_title, jid_bare, ix):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        logger.debug(f"{function_name}	{jid_bare}	Feed: {feed_title}")
        # TODO Add filtering
        # TODO Do this when entry is added to list and mark it as read
        # DONE!
        # results = []
        # if SQLiteGeneral.is_setting_key(db_file, "deny"):
        #     while len(results) < num:
        #         result = cur.execute(sql).fetchone()
        #         blacklist = SQLiteGeneral.get_setting_value(db_file, "deny").split(",")
        #         for i in blacklist:
        #             if i in result[1]:
        #                 continue
        #                 print("rejected:", result[1])
        #         print("accepted:", result[1])
        #         results.extend([result])
        title = UtilityHtml.remove_html_tags(title) if title else "Untitled"
        if summary:
            summary = UtilityHtml.remove_html_tags(summary)
            # TODO Limit text length
            # summary = summary.replace("\n\n\n", "\n\n")
            summary = summary.replace("\n", " ")
            summary = summary.replace("    ", " ")
            # summary = summary.replace("  ", " ")
            summary = " ".join(summary.split())
            config_account = accounts.retrieve(jid_bare)
            length = config_account.settings["length"]
            length = int(length)
            summary = summary[:length] + " […]"
            # summary = summary.strip().split("\n")
            # summary = ["> " + line for line in summary]
            # summary = "\n".join(summary)
        link = UtilityUri.remove_tracking_parameters(link)
        # news_item = (f"\n{str(title)}\n{str(link)}\n{str(feed_title)} [{str(ix)}]\n")
        formatting = configurations.defaults["formatting"]
        #formatting = config_account.settings["formatting"]
        news_item = formatting.format(feed_title=feed_title, title=title,
                                      summary=summary, link=link, ix=ix,
                                      feed_id=feed_id)
        # news_item = news_item.replace("\\n", "\n")
        return news_item

# TODO Move to module message.py
class XmppChatTask:

    async def looper(xmpp_instance, jid_bare):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        update_interval = config_account.settings["interval"]
        update_interval = 60 * int(update_interval)
        while True:
            last_update_time = SQLiteGeneral.get_last_update_time(db_file)
            if last_update_time:
                last_update_time = float(last_update_time)
                diff = time.time() - last_update_time
                if diff < update_interval:
                    next_update_time = update_interval - diff
                    await asyncio.sleep(next_update_time)
                await SQLiteGeneral.update_last_update_time(db_file)
            else:
                await SQLiteGeneral.set_last_update_time(db_file)
            await XmppChatAction.send_unread_items(xmpp_instance, jid_bare)
            XmppStatus.send_status_message(xmpp_instance, jid_bare)
            await asyncio.sleep(50)

    def restart_task(xmpp_instance, jid_bare):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        config_account = accounts.retrieve(jid_bare)
        UtilityTask.stop(config_account.tasks_manager, "interval")
        config_account.tasks_manager["interval"] = asyncio.create_task(
            XmppChatTask.looper(xmpp_instance, jid_bare))
        logger.debug(f"{function_name}	{jid_bare}	Finish")
