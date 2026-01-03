#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

TODO

1) XHTML-IM
    case _ if message_lowercase.startswith("html"):
        message["html"]="
Parse me!
"
        xmpp_instance.send_message(
            mto=jid,
            mfrom=xmpp_instance.boundjid.bare,
            mhtml=message
            )

NOTE

1) Extracting attribute using xmltodict.
    import xmltodict
    message = xmltodict.parse(str(message))
    jid = message["message"]["x"]["@jid"]

############################################################
#                                                          #
#                     INSTRUCTIONS                         #
#                                                          #
############################################################

1) Best practice: One form per functionality.
2) Use match/case only when it is intended to provide
   several actions of functionality of similar context.
   This will usually occur from first form which receives
   the parameters (xmpp_instance, iq, session) to second form which
   is yielded from a function with match/case.
3) Do not use same function for two different actions
   (i.e. match/case), because it makes context and future
   management difficult.

TODO

Add intermediate form to separate several forms from a function..
The intermediate form will have technical explanation about the next form.

e.g when list-multi is engaged
 options.addOption("Bookmarks", "bookmarks")
 options.addOption("Contacts", "roster")
 options.addOption("Nodes", "nodes")
 options.addOption("PubSub", "pubsub")
 options.addOption("Subscribers", "subscribers")

NOTE

1) Utilize code session["notes"] to keep last form:

 text_note = "Done."
 session["next"] = None
 session["notes"] = [["info", text_note]]
 session["payload"] = None

 see _handle_subscription_toggle

 instead of

 form = payload
 form["title"] = "Done"
 form["instructions"] = None
 session["payload"] = form

2) Set session["next"] = None to make form to disappear (Cheogram and monocles chat)

"""

# from slixmpp.plugins.xep_0363.http_upload import FileTooBig, HTTPError, UploadServiceNotFound
# from slixmpp.plugins.xep_0402 import BookmarkStorage, Conference
# from slixmpp.plugins.xep_0048.stanza import Bookmarks

# import xmltodict
# import xml.etree.ElementTree as ET
# from lxml import etree

import asyncio
from datetime import datetime
import functools
import os
from pathlib import Path
from slixfeed.configuration.singleton import configurations
from slixfeed.interface.xmpp.message import XmppMessage
#from slixfeed.interface.xmpp.encryption import XmppOmemo
from slixfeed.interface.xmpp.presence import XmppPresence
from slixfeed.interface.xmpp.status import XmppStatusTask
from slixfeed.interface.xmpp.upload import XmppUpload
from slixfeed.interface.xmpp.utilities import XmppUtilities
from slixfeed.sqlite.general import SQLiteGeneral
from slixfeed.utility.account import accounts
from slixfeed.utility.datetime import UtilityDateTime
from slixfeed.utility.download import UtilityDownload
from slixfeed.utility.html import UtilityHtml
from slixfeed.utility.logger import UtilityLogger
from slixfeed.utility.miscellaneous import UtilityMiscellaneous
from slixfeed.utility.opml import UtilityOpml
from slixfeed.utility.subscription import UtilitySubscription, UtilitySubscriptionTask
from slixfeed.utility.task import UtilityTask
from slixfeed.utility.toml import UtilityToml
from slixfeed.utility.uri import UtilityUri
from slixmpp.jid import JID
#from slixmpp.types import JidStr
import sys

# time_now = datetime.now()
# time_now = time_now.strftime("%H:%M:%S")

# def print_time():
#     # return datetime.now().strftime("%H:%M:%S")
#     now = datetime.now()
#     current_time = now.strftime("%H:%M:%S")
#     return current_time

logger = UtilityLogger(__name__)

class XmppForms:

    def profile(xmpp_instance, iq, session):
        function_name = sys._getframe().f_code.co_name
        jid_bare = session["from"].bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        form = xmpp_instance["xep_0004"].make_form("form", "Profile")
        form["instructions"] = f"Displaying information\nJabber ID {jid_bare}"
        form.add_field(
            ftype="fixed", value="News", label="News")
        feeds_all = str(
            SQLiteGeneral.get_number_of_items(db_file, "feeds_properties"))
        form.add_field(
            label="Subscriptions", ftype="text-single", value=feeds_all)
        feeds_act = str(SQLiteGeneral.get_number_of_feeds_active(db_file))
        form.add_field(
            label="Active", ftype="text-single", value=feeds_act)
        entries = str(SQLiteGeneral.get_number_of_items(db_file, "entries_properties"))
        form.add_field(
            label="Items", ftype="text-single", value=entries)
        unread = str(SQLiteGeneral.get_number_of_entries_unread(db_file))
        form.add_field(
            label="Unread", ftype="text-single", value=unread)
        form.add_field(
            ftype="fixed", value="Options", label="Options")
        key_archive = str(config_account.settings["archive"])
        form.add_field(
            label="Archive", ftype="text-single", value=key_archive)
        key_enabled = str(config_account.settings["enabled"])
        form.add_field(
            label="Enabled", ftype="text-single", value=key_enabled)
        key_interval = str(config_account.settings["interval"])
        form.add_field(
            label="Interval", ftype="text-single", value=key_interval)
        key_length = str(config_account.settings["length"])
        form.add_field(
            label="Length", ftype="text-single", value=key_length)
        key_media = str(config_account.settings["media"])
        form.add_field(
            label="Media", ftype="text-single", value=key_media)
        key_old = str(config_account.settings["old"])
        form.add_field(
            label="Old", ftype="text-single", value=key_old)
        key_amount = str(config_account.settings["amount"])
        form.add_field(
            label="Quantum", ftype="text-single", value=key_amount)
        update_interval = 60 * config_account.settings["interval"]
        last_update_time = SQLiteGeneral.get_last_update_time(db_file)
        if last_update_time:
            last_update_time = float(last_update_time)
            dt_object = datetime.fromtimestamp(last_update_time)
            last_update = dt_object.strftime("%H:%M:%S")
            if int(key_enabled):
                next_update_time = last_update_time + update_interval
                dt_object = datetime.fromtimestamp(next_update_time)
                next_update = dt_object.strftime("%H:%M:%S")
            else:
                next_update = "n/a"
        else:
            last_update = next_update = "n/a"
        form.add_field(ftype="fixed", value="Schedule", label="Schedule")
        form.add_field(label="Last update", ftype="text-single",
                       value=last_update)
        form.add_field(label="Next update", ftype="text-single",
                       value=next_update)
        session["payload"] = form
        # text_note = ("Jabber ID: {jid}"
        #              "\n"
        #              "Last update: {last_update}"
        #              "\n"
        #              "Next update: {next_update}")
        # session["notes"] = [["info", text_note]]
        return session

    async def filters(xmpp_instance, iq, session):
        function_name = sys._getframe().f_code.co_name
        jid = session["from"]
        jid_bare = jid.bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        chat_type = await XmppUtilities.get_chat_type(xmpp_instance, jid_bare)
        if XmppUtilities.is_access(xmpp_instance, jid, chat_type):
            config_account = accounts.retrieve(jid_bare)
            db_file = config_account.database
            form = xmpp_instance["xep_0004"].make_form("form", "Filters")
            form["instructions"] = ("Filters allow you to skip news items that "
                                    "you may not be interested at. Use the "
                                    "\"Allow list\" as an \"Exception list\" "
                                    "to exceptionally enforce items that "
                                    "contain keywords that are included in the "
                                    "\"Deny list\". If only the \"Allow list\" "
                                    "is enabled, then Slixfeed would skip any "
                                    "item that does not include the chosen "
                                    "keywords")
            value = SQLiteGeneral.get_filter_value(db_file, "allow")
            if value: value = str(value)
            # TODO Add check box for allow and also for deny (See Greasemonkey extension Newspaper).
            form.add_field(desc="Keywords to allow (comma-separated keywords).",
                           ftype="text-single",
                           label="Allow list",
                           value=value,
                           var="allow")
            value = SQLiteGeneral.get_filter_value(db_file, "deny")
            if value: value = str(value)
            form.add_field(desc="Keywords to deny (comma-separated keywords).",
                           ftype="text-single",
                           label="Deny list",
                           value=value,
                           var="deny")
            session["allow_complete"] = True
            session["has_next"] = False
            session["next"] = functools.partial(XmppForms.filters_complete,
                                                xmpp_instance)
            session["payload"] = form
        else:
            if chat_type == "error":
                text_warn = (f"Could not determine chat type of {jid_bare}.")
            elif chat_type == "groupchat":
                text_warn = ("This resource is restricted to moderators of "
                             f"{jid_bare}.")
            else:
                text_warn = "This resource is restricted."
            session["notes"] = [["warn", text_warn]]
        return session

    async def filters_complete(xmpp_instance, payload, session):
        """
        Process a command result from the user.

        Arguments:
            payload -- Either a single item, such as a form, or a list
                       of items or forms if more than one form was
                       provided to the user. The payload may be any
                       stanza, such as jabber:x:oob for out of band
                       data, or jabber:x:data for typical data forms.
            session -- A dictionary of data relevant to the command
                       session. Additional, custom data may be saved
                       here to persist across handler callbacks.
        """
        function_name = sys._getframe().f_code.co_name
        jid_bare = session["from"].bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        # Text is not displayed; only labels
        form = payload
        # form = xmpp_instance["xep_0004"].make_form("result", "Done")
        # form["instructions"] = ("✅️ Filters have been updated")
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        # In this case (as is typical), the payload is a form
        values = payload["values"]
        for key in values:
            val = values[key]
            # NOTE We might want to add new keywords from
            #      an empty form instead of editing a form.
            # keywords = SQLiteGeneral.get_filter_value(db_file, key)
            keywords = ""
            val = config.add_to_list(val, keywords) if val else ""
            if SQLiteGeneral.is_filter_key(db_file, key):
                await SQLiteGeneral.update_filter_value(db_file, [key, val])
            elif val:
                await SQLiteGeneral.set_filter_value(db_file, [key, val])
            # form.add_field(var=key.capitalize() + " list",
            #                ftype="text-single",
            #                value=val)
        form["title"] = "Done"
        # session["has_next"] = False
        session["next"] = None
        session["payload"] = form
        return session

    async def subscription_add(xmpp_instance, iq, session):
        function_name = sys._getframe().f_code.co_name
        jid = session["from"]
        jid_bare = jid.bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        chat_type = await XmppUtilities.get_chat_type(xmpp_instance, jid_bare)
        if XmppUtilities.is_access(xmpp_instance, jid, chat_type):
            form = xmpp_instance["xep_0004"].make_form("form", "Add Subscription")
            form["instructions"] = "Add a URI or URL to subscribe to."
            form.add_field(ftype="fixed",
                           label="Subscription",
                           value="Subscription",
                           desc="Enter a URI or URL. A scheme (e.g. gemini:// "
                                "or ipfs://) is required.")
            form.add_field(desc="Enter a URI or URL. A scheme (e.g. gemini:// "
                                "or ipfs://) is required.",
                           # TODO Make it possible to add several subscriptions at once;
                           #      Similarly to BitTorrent trackers list
                           # ftype="text-multi",
                           # label="Subscription URLs",
                           # desc="Add subscriptions one time per "
                           #       "subscription.",
                           ftype="text-single",
                           label="URI",
                           required=True,
                           var="uri")
            # form.add_field(desc="Scan URL for validity (recommended).",
            #                ftype="boolean",
            #                label="Scan",
            #                value=True,
            #                var="scan")
            session["allow_prev"] = False
            session["has_next"] = True
            session["next"] = functools.partial(XmppForms.subscription_new,
                                                xmpp_instance)
            session["prev"] = None
            session["payload"] = form
        else:
            if chat_type == "error":
                text_warn = "Could not determine chat type of {jid_bare}."
            elif chat_type == "groupchat":
                text_warn = ("This resource is restricted to moderators of "
                             f"{jid_bare}.")
            else:
                text_warn = "This resource is restricted."
            session["notes"] = [["warn", text_warn]]
        return session

    async def recent(xmpp_instance, iq, session):
        function_name = sys._getframe().f_code.co_name
        jid_bare = session["from"].bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        form = xmpp_instance["xep_0004"].make_form("form", "Updates")
        # form["instructions"] = "Browse and read news items."
        options = form.add_field(desc="What would you want to read?",
                                 ftype="list-single",
                                 label="News",
                                 required=True,
                                 var="action")
        options.addOption("All", "all")
        # options.addOption("News by subscription", "feed")
        # options.addOption("News by tag", "tag")
        options.addOption("Rejected", "reject")
        options.addOption("Unread", "unread")
        # Cheogram changes style if button "allow_prev" - which should not be on this form - is present
        session["allow_prev"] = False
        session["has_next"] = True
        session["next"] = functools.partial(XmppForms.recent_result,
                                            xmpp_instance)
        session["payload"] = form
        # Cheogram works as expected with "allow_prev" set to False Just in case
        session["prev"] = None
        return session

    def recent_result(xmpp_instance, payload, session):
        function_name = sys._getframe().f_code.co_name
        jid_bare = session["from"].bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        values = payload["values"]
        form = xmpp_instance["xep_0004"].make_form("form", "Updates")
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        num = 100
        match values["action"]:
            case "all":
                results = SQLiteGeneral.get_entries(db_file, num)
                subtitle = f"Recent {num} updates"
                message = "There are no news"
            case "reject":
                results = SQLiteGeneral.get_entries_rejected(db_file, num)
                subtitle = f"Recent {num} updates (rejected)"
                message = "There are no rejected news"
            case "unread":
                results = SQLiteGeneral.get_unread_entries(db_file, num)
                subtitle = f"Recent {num} updates (unread)"
                message = "There are no unread news."
        if results:
            form["instructions"] = subtitle
            options = form.add_field(desc="Select a news item to read.",
                                     ftype="list-single",
                                     label="News",
                                     required=True,
                                     var="update")
            for result in results:
                title = result[1] # TODO Decide what title to display upon empty title
                if not title: title = SQLiteGeneral.get_feed_title(db_file, result[4])
                ix = str(result[0])
                options.addOption(title, ix)
            session["allow_prev"] = False # Cheogram changes style if that button - which should not be on this form - is present
            session["has_next"] = True
            session["next"] = functools.partial(XmppForms.recent_select,
                                                xmpp_instance)
            session["payload"] = form
            session["prev"] = None # Cheogram works as expected with "allow_prev" set to False Just in case
        else:
            text_info = message
            session["allow_prev"] = True
            session["has_next"] = False
            session["next"] = None
            session["notes"] = [["info", text_info]]
            session["payload"] = None
            session["prev"] = functools.partial(XmppForms.recent, xmpp_instance)
        return session

    # TODO FIXME Do not declare jid_bare twice
    # TODO Restore document export. Copy code from Slixprint.
    def recent_select(xmpp_instance, payload, session):
        function_name = sys._getframe().f_code.co_name
        jid_bare = session["from"].bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        values = payload["values"]
        ix = values["update"]
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        title = SQLiteGeneral.get_entry_title(db_file, ix)
        form = xmpp_instance["xep_0004"].make_form("form", title)
        #form["instructions"] = SQLiteGeneral.get_entry_title(db_file, ix) or "Untitled"
        # TODO Handle a situation when index is no longer exist
        url = SQLiteGeneral.get_entry_url(db_file, ix)
        logger.debug(f"{function_name}	{jid_bare}	Original URL: {url}")
        url = UtilityUri.remove_tracking_parameters(url)
        logger.debug(f"{function_name}	{jid_bare}	Processed URL (tracker removal): {url}")
        logger.debug(f"{function_name}	{jid_bare}	Processed URL (replace hostname): {url}")
        # result = await UtilityDownload.uri(url)
        # if "content" in result:
        #     data = result["content"]
        #     summary = action.get_document_content_as_text(data)
        summary = SQLiteGeneral.get_entry_summary(db_file, ix)
        if summary:
            form["instructions"] = UtilityHtml.remove_html_tags(summary)
        content = SQLiteGeneral.get_entry_content(db_file, ix)
        if content:
            content_clean = UtilityHtml.remove_html_tags(content)
            form.add_field(ftype="text-multi",
                           label="Content",
                           value=content_clean)
        #field_url = form.add_field(ftype="hidden",
        #                           value=url,
        #                           var="url")
        field_url = form.add_field(ftype="text-single",
                                   label="Link",
                                   value=url,
                                   var="url_link")
        field_url["validate"]["datatype"] = "xs:anyURI"
        feed_id = SQLiteGeneral.get_feed_id_by_entry_index(db_file, ix)
        feed_url = SQLiteGeneral.get_feed_url(db_file, feed_id)
        field_feed = form.add_field(ftype="text-single",
                                    label="Source",
                                    value=feed_url,
                                    var="url_feed")
        field_feed["validate"]["datatype"] = "xs:anyURI"
        # options = form.add_field(desc="Select file type.",
        #                          ftype="list-single",
        #                          label="Save as",
        #                          required=True,
        #                          value="pdf",
        #                          var="filetype")
        # options.addOption("ePUB", "epub")
        # options.addOption("HTML", "html")
        # options.addOption("Markdown", "md")
        # options.addOption("PDF", "pdf")
        # options.addOption("Plain Text", "txt")
        session["payload"] = form
        #session["allow_complete"] = False
        session["allow_prev"] = True
        #session["has_next"] = True
        session["has_next"] = False
        # session["next"] = functools.partial(XmppForms.recent_action, xmpp_instance)
        session["next"] = None
        session["prev"] = functools.partial(XmppForms.recent, xmpp_instance)
        return session

    async def subscription_new(xmpp_instance, payload, session):
        function_name = sys._getframe().f_code.co_name
        jid_bare = session["from"].bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        form = xmpp_instance["xep_0004"].make_form("form", "Subscription")
        # scan = values["scan"]
        values = payload["values"]
        identifier = values["identifier"] if "identifier" in values else None
        if isinstance(values["uri"], str):
            uri = values["uri"]
            uris = None
        elif isinstance(values["uri"], list):
            # TODO Test
            #breakpoint()
            uri = None
            uris = values["uri"]
        custom_jid = values["jid"] if "jid" in values else None
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        if identifier and SQLiteGeneral.check_identifier_exist(db_file, identifier):
            form["title"] = "Identifier conflict"
            form["instructions"] = f"Identifier \"{identifier}\" already exists."
            form.add_field(ftype="fixed",
                           label="Identifier",
                           value="Identifier",
                           desc="An identifier is meant to distinct JIDs and "
                                "PubSub nodes.")
            form.add_field(desc="Enter a unique identifier.",
                           ftype="text-single",
                           label="Identifier",
                           value=identifier,
                           var="identifier")
            form.add_field(ftype="hidden", value=uri, var="subscription")
            form.add_field(ftype="hidden", value=identifier, var="identifier")
            session["allow_prev"] = False
            session["next"] = functools.partial(XmppForms.subscription_new,
                                                xmpp_instance)
            # session["payload"] = None
            session["prev"] = None
        # Several URLs to subscribe
        if uris:
            urls = uris
            agree_count = error_count = exist_count = 0
            for uri in uris:
                information = await UtilityDownload.uri(uri)
                if information["error"]:
                    error_count += 1
                elif information["index"]:
                    exist_count += 1
                else:
                    agree_count += 1
            if agree_count:
                response = (f"Added {agree_count} subscription(s) out of "
                            "{len(uris)}")
                session["notes"] = [["info", response]]
            else:
                response = ("No new subscription was added. "
                            f"Exist: {exist_count} Error: {error_count}.")
                session["notes"] = [["error", response]]
            session["allow_prev"] = True
            session["next"] = None
            session["payload"] = None
            session["prev"] = functools.partial(XmppForms.subscription_add,
                                                xmpp_instance)
        elif uri:
            information = await UtilityDownload.uri(uri)
            # URL is not a feed and URL has returned to feeds
            if "subscriptions" in information and len(information["subscriptions"]) > 1:
                subscriptions = information["subscriptions"]
                form["instructions"] = (f"Discovered {len(subscriptions)} "
                                        f"subscriptions for {uri}")
                options = form.add_field(desc="Select subscriptions to add.",
                                         ftype="list-multi",
                                         label="Subscribe",
                                         required=True,
                                         var="subscription")
                for subscription in subscriptions:
                    options.addOption(subscription["name"],
                                      subscription["link"])
                # NOTE Disabling "allow_prev" until Cheogram would allow to display
                # items of list-single as buttons when button "back" is enabled.
                # session["allow_prev"] = True
                session["has_next"] = True
                session["next"] = functools.partial(XmppForms.subscription_new,
                                                    xmpp_instance)
                session["payload"] = form
                # session["prev"] = functools.partial(XmppForms.subscription_add, xmpp_instance)
            elif information["error"]:
                response = information["message"]
                session["allow_prev"] = True
                session["next"] = None
                session["notes"] = [["error", response]]
                session["payload"] = None
                session["prev"] = functools.partial(XmppForms.subscription_add,
                                                    xmpp_instance)
            elif "index" in information and information["index"]:
                subscription = information["subscriptions"]
                name = subscription[0]["name"]
                form["instructions"] = (f"Subscription \"{name}\" already exist. "
                                        "Proceed to edit this subscription.")
                uri = subscription[0]["link"]
                feed_id = information["index"]
                entries = SQLiteGeneral.get_entries_of_feed(db_file, feed_id)
                renewed, scanned = SQLiteGeneral.get_last_update_time_of_feed(
                    db_file, feed_id)
                last_updated_string = renewed or scanned
                last_updated = UtilityDateTime.convert_seconds_to_yyyy_mm_dd(
                    float(last_updated_string)) if last_updated_string else "N/A"
                form.add_field(desc="Recent titles from subscription",
                               ftype="fixed",
                               value="Recent updates")
                recent_updates = ""
                for entry in entries: recent_updates += "* " + entry[1] + "\n\n"
                if not recent_updates: recent_updates = "N/A"
                form.add_field(ftype="text-multi",
                               value=recent_updates)
                form.add_field(ftype="fixed",
                               value="Information",
                               label="Information")
                form.add_field(ftype="text-single",
                               label="Renewed",
                               value=last_updated)
                form.add_field(ftype="text-single",
                               label="ID #",
                               value=feed_id)
                form.add_field(var="subscription",
                               ftype="hidden",
                               value=uri)
                # NOTE Should we allow "Complete"?
                # Do all clients provide button "Cancel".
                session["allow_complete"] = False
                session["has_next"] = True
                session["next"] = functools.partial(XmppForms.subscription_edit,
                                                    xmpp_instance)
                session["payload"] = form
                # session["has_next"] = False
            # Single URL to subscribe
            else:
                #form["instructions"] = (f"Subscription \"{title}\" has been added. "
                form["instructions"] = (f"Subscription \"{uri}\" has been added. "
                                        "Proceed to edit this subscription.")
                feed_id = SQLiteGeneral.get_feed_id(db_file, uri)
                entries = SQLiteGeneral.get_entries_of_feed(db_file, feed_id)
                #renewed, scanned = SQLiteGeneral.get_last_update_time_of_feed(
                #    db_file, feed_id)
                #last_updated = UtilityDateTime.convert_seconds_to_yyyy_mm_dd(
                #    float(renewed or scanned))
                options = form.add_field(ftype="fixed",
                                         value="Recent updates")
                recent_updates = ""
                for entry in entries: recent_updates += "* " + entry[1] + "\n\n"
                form.add_field(ftype="text-multi",
                               value=recent_updates)
                form.add_field(ftype="fixed",
                               value="Information",
                               label="Information")
                #form.add_field(ftype="text-single",
                #               label="Updated",
                #               value=last_updated)
                form.add_field(ftype="text-single",
                               label="ID #",
                               value=str(feed_id))
                form.add_field(var="subscription",
                               ftype="hidden",
                               value=uri)
                session["allow_complete"] = False
                session["has_next"] = True
                # session["allow_prev"] = False
                # Gajim: Will offer next dialog but as a result, not as form.
                # session["has_next"] = False
                session["next"] = functools.partial(XmppForms.subscription_edit,
                                                    xmpp_instance)
                session["payload"] = form
                # session["prev"] = None
        return session

    async def subscription_toggle(xmpp_instance, payload, session):
        function_name = sys._getframe().f_code.co_name
        jid_bare = session["from"].bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        values = payload["values"]
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        for key in values:
            value = 1 if values[key] else 0
            await SQLiteGeneral.set_enabled_status(db_file, key, value)
        # text_note = "Done."
        # session["next"] = None
        # session["notes"] = [["info", text_note]]
        # session["payload"] = None
        form = payload
        form["title"] = "Done"
        form["instructions"] = "has been successful"
        session["payload"] = form
        return session

    async def subscription_del_complete(xmpp_instance, payload, session):
        function_name = sys._getframe().f_code.co_name
        jid_bare = session["from"].bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        values = payload["values"]
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        subscriptions = ""
        ixs = values["subscriptions"]
        for ix in ixs:
            name = SQLiteGeneral.get_feed_title(db_file, ix)
            url = SQLiteGeneral.get_feed_url(db_file, ix)
            if not name: name = f"Subscription #{ix}"
            await SQLiteGeneral.remove_feed_by_index(db_file, ix)
            subscriptions += f"{ix}. {name}\n{url}\n\n"
        text_note = ("The following subscriptions have been deleted:\n\n"
                     f"{subscriptions}")
        session["next"] = None
        session["notes"] = [["info", text_note]]
        session["payload"] = None
        return session

    def cancel(xmpp_instance, payload, session):
        function_name = sys._getframe().f_code.co_name
        jid_bare = session["from"].bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        text_note = "Operation has been cancelled.\n\nNo action was taken."
        session["notes"] = [["info", text_note]]
        return session

    async def discover(xmpp_instance, iq, session):
        function_name = sys._getframe().f_code.co_name
        jid = session["from"]
        jid_bare = jid.bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        chat_type = await XmppUtilities.get_chat_type(xmpp_instance, jid_bare)
        if XmppUtilities.is_access(xmpp_instance, jid, chat_type):
            form = xmpp_instance["xep_0004"].make_form("form", "Discover & Search")
            form["instructions"] = "Discover news subscriptions of all kinds"
            options = form.add_field(desc="Select type of search.",
                                     ftype="list-single",
                                     label="Browse",
                                     required=True,
                                     var="search_type")
            options.addOption("All", "all")
            options.addOption("Categories", "cat") # Should we write this in a singular form
            # options.addOption("Tags", "tag")
            session["allow_prev"] = False
            session["has_next"] = True
            session["next"] = functools.partial(XmppForms.discover_type,
                                                xmpp_instance)
            session["payload"] = form
            session["prev"] = None
        else:
            if chat_type == "error":
                text_warn = f"Could not determine chat type of {jid_bare}."
            elif chat_type == "groupchat":
                text_warn = ("This resource is restricted to moderators of "
                             f"{jid_bare}.")
            else:
                text_warn = "This resource is restricted."
            session["notes"] = [["warn", text_warn]]
        return session

    def discover_type(xmpp_instance, payload, session):
        function_name = sys._getframe().f_code.co_name
        jid_bare = session["from"].bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        values = payload["values"]
        search_type = values["search_type"]
        db_file = os.path.join(configurations.directory_config, "feeds.sqlite")
        if os.path.isfile(db_file):
            form = xmpp_instance["xep_0004"].make_form("form", "Discover")
            match search_type:
                case "all":
                    form["instructions"] = "Browsing subscriptions"
                    options = form.add_field(desc="Select a subscription to add.",
                                             # ftype="list-multi", # TODO To be added soon
                                             ftype="list-single",
                                             label="Subscription",
                                             required=True,
                                             var="subscription")
                    results = SQLiteGeneral.get_titles_tags_urls(db_file)
                    for result in results:
                        title = result[0]
                        tag = result[1]
                        url = result[2]
                        text = f"{title} ({tag})"
                        options.addOption(text, url)
                    # session["allow_complete"] = True
                    session["next"] = functools.partial(XmppForms.subscription_new,
                                                        xmpp_instance)
                case "cat":
                    form["instructions"] = "Browsing categories"
                    session["next"] = functools.partial(XmppForms.discover_category,
                                                        xmpp_instance)
                    options = form.add_field(desc="Select a category to browse.",
                                             ftype="list-single",
                                             label="Categories",
                                             required=True,
                                             var="category") # NOTE Uncategories or no option for entries without category
                    categories = SQLiteGeneral.get_categories(db_file)
                    for category in categories:
                        category = category[0]
                        options.addOption(category, category)
                # case "tag":
            session["allow_prev"] = True
            session["has_next"] = True
            session["payload"] = form
            session["prev"] = functools.partial(XmppForms.discover,
                                                xmpp_instance)
        else:
            text_note = "Database is missing.\nContact operator."
            session["next"] = None
            session["notes"] = [["info", text_note]]
            session["payload"] = None
        return session

    async def discover_category(xmpp_instance, payload, session):
        function_name = sys._getframe().f_code.co_name
        jid_bare = session["from"].bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        values = payload["values"]
        category = values["category"]
        db_file = os.path.join(configurations.directory_config, "feeds.sqlite")
        form = xmpp_instance["xep_0004"].make_form("form", "Search & Discover")
        form["instructions"] = "Browsing category \"{category}\""
        options = form.add_field(desc="Select a subscription to add.",
                                 # ftype="list-multi", # TODO To be added soon
                                 ftype="list-single",
                                 label="Subscription",
                                 required=True,
                                 var="subscription")
        results = SQLiteGeneral.get_titles_tags_urls_by_category(db_file,
                                                                 category)
        for result in results:
            title = result[0]
            tag = result[1]
            url = result[2]
            text = f"{title} ({tag})"
            options.addOption(text, url)
        # session["allow_complete"] = True
        session["next"] = functools.partial(XmppForms.subscription_new,
                                            xmpp_instance)
        session["payload"] = form
        return session

    async def subscriptions(xmpp_instance, iq, session):
        function_name = sys._getframe().f_code.co_name
        jid = session["from"]
        jid_bare = jid.bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        chat_type = await XmppUtilities.get_chat_type(xmpp_instance, jid_bare)
        if XmppUtilities.is_access(xmpp_instance, jid, chat_type):
            form = xmpp_instance["xep_0004"].make_form("form", "Subscriptions")
            form["instructions"] = ("Browse, view, toggle, or remove tags and "
                                    "subscriptions.")
            options = form.add_field(desc="Select action type.",
                                     ftype="list-single",
                                     label="Action",
                                     required=True,
                                     value="browse",
                                     var="action")
            options.addOption("Browse subscriptions", "browse")
            options.addOption("Browse tags", "tag")
            options.addOption("Remove subscriptions", "delete")
            options.addOption("Toggle subscriptions", "toggle")
            session["payload"] = form
            session["next"] = functools.partial(XmppForms.subscriptions_result,
                                                xmpp_instance)
            session["has_next"] = True
        else:
            if chat_type == "error":
                text_warn = f"Could not determine chat type of {jid_bare}."
            elif chat_type == "groupchat":
                text_warn = ("This resource is restricted to moderators of "
                             f"{jid_bare}.")
            else:
                text_warn = "This resource is restricted."
            session["notes"] = [["warn", text_warn]]
        return session

    def subscriptions_result(xmpp_instance, payload, session):
        function_name = sys._getframe().f_code.co_name
        jid_bare = session["from"].bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        values = payload["values"]
        form = xmpp_instance["xep_0004"].make_form("form", "Subscriptions")
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        match values["action"]:
            case "browse":
                form["instructions"] = "Editing subscriptions"
                options = form.add_field(desc="Select a subscription to edit.",
                                         # ftype="list-multi", # TODO To be added soon
                                         ftype="list-single",
                                         label="Subscription",
                                         required=True,
                                         var="subscriptions")
                subscriptions = SQLiteGeneral.get_feeds(db_file)
                # subscriptions = sorted(subscriptions, key=lambda x: x[1])
                for subscription in subscriptions:
                    title = subscription[1]
                    url = subscription[2]
                    options.addOption(title, url)
                session["has_next"] = True
                session["next"] = functools.partial(XmppForms.subscription_edit,
                                                    xmpp_instance)
                session["allow_complete"] = False
            case "delete":
                form["instructions"] = "Removing subscriptions"
                # form.addField(var="interval",
                #               ftype="text-single",
                #               label="Interval period")
                options = form.add_field(desc="Select subscriptions to remove.",
                                         ftype="list-multi",
                                         label="Subscriptions",
                                         required=True,
                                         var="subscriptions")
                subscriptions = SQLiteGeneral.get_feeds(db_file)
                # subscriptions = sorted(subscriptions, key=lambda x: x[1])
                for subscription in subscriptions:
                    title = subscription[1]
                    ix = str(subscription[0])
                    options.addOption(title, ix)
                session["cancel"] = functools.partial(XmppForms.cancel,
                                                      xmpp_instance)
                session["has_next"] = False
                # TODO Refer to confirmation dialog which would display feeds selected
                session["next"] = functools.partial(XmppForms.subscription_del_complete,
                                                    xmpp_instance)
                session["allow_complete"] = True
            case "toggle":
                form["instructions"] = "Toggling subscriptions"
                subscriptions = SQLiteGeneral.get_feeds_and_enabled_state(db_file)
                # subscriptions = sorted(subscriptions, key=lambda x: x[1])
                for subscription in subscriptions:
                    ix = str(subscription[0])
                    title = subscription[3]
                    url = subscription[1]
                    enabled_state = True if subscription[17] else False
                    enabled_state = subscription[17]
                    form.add_field(desc=url,
                                   ftype="boolean",
                                   label=title,
                                   value=enabled_state,
                                   var=ix)
                session["cancel"] = functools.partial(XmppForms.cancel,
                                                      xmpp_instance)
                session["has_next"] = False
                session["next"] = functools.partial(XmppForms.subscription_toggle,
                                                    xmpp_instance)
                session["allow_complete"] = True
            case "tag":
                form["instructions"] = "Browsing tags"
                options = form.add_field(desc="Select a tag to browse.",
                                         ftype="list-single",
                                         label="Tag",
                                         required=True,
                                         var="tag")
                tags = SQLiteGeneral.get_tags(db_file)
                # tags = sorted(tags, key=lambda x: x[0])
                for tag in tags:
                    name = tag[0]
                    ix = str(tag[1])
                    options.addOption(name, ix)
                session["allow_complete"] = False
                session["next"] = functools.partial(XmppForms.subscription_tag,
                                                    xmpp_instance)
                session["has_next"] = True
        session["allow_prev"] = True
        session["payload"] = form
        session["prev"] = functools.partial(XmppForms.subscriptions,
                                            xmpp_instance)
        return session

    def subscription_tag(xmpp_instance, payload, session):
        function_name = sys._getframe().f_code.co_name
        jid_bare = session["from"].bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        form = xmpp_instance["xep_0004"].make_form("form", "Subscriptions")
        values = payload["values"]
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        tag_id = values["tag"]
        tag_name = SQLiteGeneral.get_tag_name(db_file, tag_id)
        form["instructions"] = f"Subscriptions tagged with \"{tag_name}\"."
        options = form.add_field(desc="Select a subscription to edit.",
                                 # ftype="list-multi", # TODO To be added soon
                                 ftype="list-single",
                                 label="Subscription",
                                 required=True,
                                 var="subscriptions")
        subscriptions = SQLiteGeneral.get_feeds_by_tag_id(db_file, tag_id)
        # subscriptions = sorted(subscriptions, key=lambda x: x[1])
        for subscription in subscriptions:
            title = subscription[1]
            url = subscription[2]
            options.addOption(title, url)
        session["allow_complete"] = False
        session["allow_prev"] = True
        session["has_next"] = True
        session["next"] = functools.partial(XmppForms.subscription_edit,
                                            xmpp_instance)
        session["payload"] = form
        session["prev"] = functools.partial(XmppForms.subscriptions,
                                            xmpp_instance)
        return session

    def subscription_edit(xmpp_instance, payload, session):
        function_name = sys._getframe().f_code.co_name
        jid_bare = session["from"].bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        form = xmpp_instance["xep_0004"].make_form("form", "Subscription")
        values = payload["values"]
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        if "subscription" in values: urls = values["subscription"]
        elif "subscriptions" in values: urls = values["subscriptions"]
        url_count = len(urls)
        if isinstance(urls, list) and url_count > 1:
            form["instructions"] = f"Editing {url_count} subscriptions"
        else:
            if isinstance(urls, list):
                url = urls[0]
            # elif isinstance(urls, str):
            else:
                url = urls
            feed_id = SQLiteGeneral.get_feed_id(db_file, url)
            if feed_id:
                title = SQLiteGeneral.get_feed_title(db_file, feed_id)
                tags_result = SQLiteGeneral.get_tags_by_feed_id(db_file, feed_id)
                # tags_sorted = sorted(x[0] for x in tags_result)
                # tags = ", ".join(tags_sorted)
                tags = ""
                for tag in tags_result: tags += tag[0] + ", "
                form["instructions"] = f"Editing subscription #{feed_id}."
            else:
                form["instructions"] = "Adding a new subscription."
                title = ""
                tags = "" # TODO Suggest tags by element "categories"
            form.add_field(ftype="fixed",
                           value="Properties",
                           label="Properties")
            form.add_field(var="name",
                           ftype="text-single",
                           label="Name",
                           value=title,
                           required=True)
            # NOTE This does not look good in Gajim
            # url = form.add_field(ftype="fixed",
            #                      label=url)
            #url["validate"]["datatype"] = "xs:anyURI"
            options = form.add_field(var="url",
                                     ftype="list-single",
                                     label="URI",
                                     value=url)
            options.addOption(url, url)
            feed_id_str = str(feed_id)
            options = form.add_field(var="id",
                                     ftype="list-single",
                                     label="ID #",
                                     value=feed_id_str)
            options.addOption(feed_id_str, feed_id_str)
            form.add_field(desc="Comma-separated tags.",
                           ftype="text-single",
                           label="Tags",
                           value=tags,
                           var="tags_new")
            form.add_field(ftype="hidden",
                           value=tags,
                           var="tags_old")
        form.add_field(ftype="fixed",
                       value="Options",
                       label="Options")
        options = form.add_field(ftype="list-single",
                                 label="Priority",
                                 value="0",
                                 var="priority")
        options["validate"]["datatype"] = "xs:integer"
        options["validate"]["range"] = {"minimum": 1,
                                        "maximum": 5}
        i = 0
        while i <= 5:
            num = str(i)
            options.addOption(num, num)
            i += 1
        form.add_field(
            ftype="boolean",
            label="Enabled",
            value=True,
            var="enabled")
        session["allow_complete"] = True
        # session["allow_prev"] = True
        session["cancel"] = functools.partial(XmppForms.cancel, xmpp_instance)
        session["has_next"] = False
        session["next"] = functools.partial(XmppForms.subscription_complete,
                                            xmpp_instance)
        session["payload"] = form
        return session

    # FIXME Do not declare jid_bare twice
    # TODO Create a new form. Do not "recycle" the last form.
    async def subscription_complete(xmpp_instance, payload, session):
        function_name = sys._getframe().f_code.co_name
        jid_bare = session["from"].bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        values = payload["values"]
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        # url = values["url"]
        # feed_id = SQLiteGeneral.get_feed_id(db_file, url)
        feed_id = values["id"]
        enabled = values["enabled"]
        # if enabled:
        #     enabled_status = 1
        # else:
        #     enabled_status = 0
        #     await SQLiteGeneral.mark_feed_as_read(db_file, feed_id)
        enabled_status = 1 if enabled else 0
        if not enabled_status: await SQLiteGeneral.mark_feed_as_read(db_file,
                                                                     feed_id)
        await SQLiteGeneral.set_enabled_status(db_file, feed_id, enabled_status)
        name = values["name"]
        await SQLiteGeneral.set_feed_title(db_file, feed_id, name)
        priority = values["priority"]
        tags_new = values["tags_new"]
        tags_old = values["tags_old"]
        # Add new tags
        for tag in tags_new.split(","):
            tag = tag.strip()
            if not tag:
                continue
            tag = tag.lower()
            tag_id = SQLiteGeneral.get_tag_id(db_file, tag)
            if not tag_id:
                await SQLiteGeneral.set_new_tag(db_file, tag)
                tag_id = SQLiteGeneral.get_tag_id(db_file, tag)
            if not SQLiteGeneral.is_tag_id_of_feed_id(db_file, tag_id, feed_id):
                await SQLiteGeneral.set_feed_id_and_tag_id(db_file, feed_id,
                                                           tag_id)
        # Remove tags that were not submitted
        for tag in tags_old[0].split(","):
            tag = tag.strip()
            if not tag:
                continue
            if tag not in tags_new:
                tag_id = SQLiteGeneral.get_tag_id(db_file, tag)
                await SQLiteGeneral.delete_feed_id_tag_id(db_file, feed_id,
                                                          tag_id)
                SQLiteGeneral.is_tag_id_associated(db_file, tag_id)
                await SQLiteGeneral.delete_tag_by_index(db_file, tag_id)
        # form = xmpp_instance["xep_0004"].make_form("form", "Subscription")
        # form["instructions"] = "📁️ Subscription #{feed_id} has been {action}"
        form = payload
        form["title"] = "Done"
        # session["has_next"] = False
        session["next"] = None
        session["payload"] = form
        # session["type"] = "submit"
        return session

    async def subscription_import(xmpp_instance, payload, session):
        function_name = sys._getframe().f_code.co_name
        jid = session["from"]
        jid_bare = jid.bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        chat_type = await XmppUtilities.get_chat_type(xmpp_instance, jid_bare)
        if XmppUtilities.is_access(xmpp_instance, jid, chat_type):
            form = xmpp_instance["xep_0004"].make_form("form", "Import")
            form["instructions"] = "Importing feeds"
            url = form.add_field(desc="Enter URL to an OPML file.",
                                 ftype="text-single",
                                 label="URL",
                                 required=True,
                                 var="url")
            url["validate"]["datatype"] = "xs:anyURI"
            session["allow_complete"] = True
            session["has_next"] = False
            session["next"] = functools.partial(XmppForms.import_complete,
                                                xmpp_instance)
            session["payload"] = form
        else:
            if chat_type == "error":
                text_warn = f"Could not determine chat type of {jid_bare}."
            elif chat_type == "groupchat":
                text_warn = ("This resource is restricted to moderators of "
                             f"{jid_bare}.")
            else:
                text_warn = "This resource is restricted."
            session["notes"] = [["warn", text_warn]]
        return session

    async def subscription_export(xmpp_instance, payload, session):
        function_name = sys._getframe().f_code.co_name
        jid = session["from"]
        jid_bare = jid.bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        chat_type = await XmppUtilities.get_chat_type(xmpp_instance, jid_bare)
        if XmppUtilities.is_access(xmpp_instance, jid, chat_type):
            form = xmpp_instance["xep_0004"].make_form("form", "Export")
            form["instructions"] = ("It is always recommended to export "
                                    "subscriptions into an OPML file, in order "
                                    "to easily import subscriptions from one "
                                    "Syndication News Reader (i.e. Feed Reader "
                                    "or RSS Reader) to another. See About -> "
                                    "News Software for a list of Feed Readers "
                                    "offered for desktop and mobile devices.")
            options = form.add_field(desc="Choose export format.",
                                     ftype="list-multi",
                                     label="Format",
                                     required=True,
                                     value="opml",
                                     var="filetype")
            options.addOption("Gemtext", "gmi")
            options.addOption("Markdown", "md")
            options.addOption("OPML", "opml")
            # options.addOption("HTML", "html")
            # options.addOption("XBEL", "xbel")
            session["allow_complete"] = True
            session["has_next"] = False
            session["next"] = functools.partial(
                XmppForms.export_complete, xmpp_instance)
            session["payload"] = form
        else:
            if chat_type == "error":
                text_warn = f"Could not determine chat type of {jid_bare}."
            elif chat_type == "groupchat":
                text_warn = ("This resource is restricted to moderators of "
                             f"{jid_bare}.")
            else:
                text_warn = "This resource is restricted."
            session["notes"] = [["warn", text_warn]]
        return session

    async def about(xmpp_instance, iq, session):
        function_name = sys._getframe().f_code.co_name
        jid_bare = session["from"].bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        form = xmpp_instance["xep_0004"].make_form("form", "About")
        form["instructions"] = "Information about Slixfeed."
        options = form.add_field(var="option",
                                 ftype="list-single",
                                 label="About",
                                 required=True,
                                 value="about")
        file_about = os.path.join(configurations.directory_data, "info", "about.toml")
        entries = UtilityToml.open_file(file_about)
        for entry in entries:
            label = entries[entry]["title"]
            options.addOption(label, entry)
            # options.addOption("Tips", "tips")
        session["payload"] = form
        session["next"] = functools.partial(XmppForms.about_result,
                                            xmpp_instance)
        session["has_next"] = True
        return session

    async def about_result(xmpp_instance, payload, session):
        function_name = sys._getframe().f_code.co_name
        jid_bare = session["from"].bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        file_about = os.path.join(configurations.directory_data, "info", "about.toml")
        entries = UtilityToml.open_file(file_about)
        entry_key = payload["values"]["option"]
            # case "terms":
            #     title = "Policies"
            #     subtitle = "Terms and Conditions"
            #     content = action.manual("information.toml", "terms")
            # case "tips":
            #     # Tips and tricks you might have not known about Slixfeed and XMPP!
            #     title = "Help"
            #     subtitle = "Tips & Tricks"
            #     content = "This page is not yet available."
            # case "translators":
            #     title = "Translators"
            #     subtitle = "From all across the world"
            #     content = action.manual("information.toml", "translators")
        # title = entry_key.capitalize()
        # form = xmpp_instance["xep_0004"].make_form("result", title)
        entry = entries[entry_key]
        title = entries[entry_key]["title"]
        form = xmpp_instance["xep_0004"].make_form("result", title)
        subtitle = entries[entry_key]["subtitle"]
        form["instructions"] = subtitle
        for entry in entries[entry_key]["entries"]:
            title = entry["title"]
            form.add_field(ftype="fixed", value=title)
            if "summary" in entry:
                summary = entry["summary"]
                form.add_field(label="Summary", ftype="text-multi", value=summary)
            if "content" in entry:
                content = entry["content"]
                form.add_field(label="Content", ftype="text-multi", value=content)
            if "urls" in entry:
                for url in entry["urls"]:
                    form.add_field(label="URL", ftype="text-single", value=url[2])
        session["payload"] = form
        session["allow_complete"] = True
        session["allow_prev"] = True
        session["has_next"] = False
        session["next"] = None
        # session["payload"] = None # Crash Cheogram
        session["prev"] = functools.partial(XmppForms.about, xmpp_instance)
        return session

    async def motd(xmpp_instance, iq, session):
        function_name = sys._getframe().f_code.co_name
        jid_bare = session["from"].bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        # TODO add functionality to attach image.
        # Here you can add groupchat rules,post schedule, tasks or
        # anything elaborated you might deem fit. Good luck!
        text_note = "This feature is not yet available."
        session["notes"] = [["info", text_note]]
        return session

    async def manual(xmpp_instance, iq, session):
        function_name = sys._getframe().f_code.co_name
        jid_bare = session["from"].bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        file_cmds = os.path.join(configurations.directory_data, "info", "commands.toml")
        cmds = UtilityToml.open_file(file_cmds)
        form = xmpp_instance["xep_0004"].make_form("result", "Manual")
        form["instructions"] = "Help manual for interactive chat"

        # text = "🛟️ Help and Information about Slixfeed\n\n"
        # for cmd in cmds:
        #     name = cmd.capitalize()
        #     elements = cmds[cmd]
        #     text += name + "\n"
        #     for key, value in elements.items():
        #         text += " " + key.capitalize() + "\n"
        #         for line in value.split("\n"):
        #             text += "  " + line + "\n"
        # form["instructions"] = text

        for cmd in cmds:
            name = cmd.capitalize()
            form.add_field(var="title",
                           ftype="fixed",
                           value=name,
                           label=name)
            elements = cmds[cmd]
            for key, value in elements.items():
                key = key.replace("_", " ")
                key = key.capitalize()
                form.add_field(var="title",
                               ftype="text-multi",
                               label=key,
                               value=value)
        session["payload"] = form
        return session

    async def import_complete(xmpp_instance, payload, session):
        function_name = sys._getframe().f_code.co_name
        jid_bare = session["from"].bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        form = payload
        values = payload["values"]
        url = values["url"]
        if url.startswith("http") and url.endswith(".opml"):
            jid_bare = session["from"].bare
            config_account = accounts.retrieve(jid_bare)
            db_file = config_account.database
            result = await UtilityDownload.uri(url)
            count = await UtilityOpml.import_subscriptions(db_file, result)
            try:
                int(count)
                # form = xmpp_instance["xep_0004"].make_form("result", "Done")
                # form["instructions"] = ("✅️ Feeds have been imported")
                form["title"] = "Done"
                message = f"{count} feeds have been imported."
                form.add_field(var="Message",
                               ftype="text-single",
                               value=message)
                session["payload"] = form
            except:
                session["payload"] = None
                text_error = ("Import failed. File does not appear to be an "
                              "OPML file.")
                session["notes"] = [["error", text_error]]
        else:
            session["payload"] = None
            text_error = "Import aborted. Send URL of OPML file."
            session["notes"] = [["error", text_error]]
        session["has_next"] = False
        session["next"] = None
        return session

    async def export_complete(xmpp_instance, payload, session):
        function_name = sys._getframe().f_code.co_name
        jid_bare = session["from"].bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        form = xmpp_instance["xep_0004"].make_form("result", "Done")
        # form["type"] = "result"
        values = payload["values"]
        # form = xmpp_instance["xep_0004"].make_form("result", "Done")
        # form["instructions"] = ("✅️ Feeds have been exported")
        exts = values["filetype"]
        for ext in exts:
            config_account = accounts.retrieve(jid_bare)
            db_file = config_account.database
            filename, message = UtilitySubscription.export(jid_bare, ext)
            encrypt_omemo = config_account.settings["omemo"]
            encrypted = True if encrypt_omemo else False
            url = await XmppUpload.start(xmpp_instance, jid_bare,
                                         Path(filename), encrypted=encrypted)
            if url:
                form["instructions"] = message
                chat_type = await XmppUtilities.get_chat_type(xmpp_instance,
                                                              jid_bare)
                if encrypted:
                    url_encrypted, omemo_encrypted = await XmppOmemo.encrypt(
                        xmpp_instance, JID(jid_bare), "chat", url)
                    XmppMessage.send_omemo_oob(xmpp_instance, JID(jid_bare),
                                               url_encrypted, chat_type)
                else:
                    XmppMessage.send_oob(xmpp_instance, jid_bare, url,
                                         chat_type)
                url_field = form.add_field(var=ext.upper(),
                                           ftype="text-single",
                                           label=ext,
                                           value=url)
                url_field["validate"]["datatype"] = "xs:anyURI"
                session["has_next"] = False
                session["next"] = None
                session["payload"] = form
            else:
                text_warn = "OPML file export has been failed."
                session["notes"] = [["warn", text_warn]]
        return session

    # TODO Exclude feeds that are already in database or requester.
    # TODO Attempt to look up for feeds of hostname of JID (i.e. scan
    # jabber.de for feeds for juliet@jabber.de)
    async def promoted(xmpp_instance, iq, session):
        function_name = sys._getframe().f_code.co_name
        jid = session["from"]
        jid_bare = jid.bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        chat_type = await XmppUtilities.get_chat_type(xmpp_instance, jid_bare)
        if XmppUtilities.is_access(xmpp_instance, jid, chat_type):
            form = xmpp_instance["xep_0004"].make_form("form", "Subscribe")
            # NOTE Refresh button would be of use
            form["instructions"] = "Featured subscriptions"
            url = UtilityMiscellaneous.pick_a_feed()
            url_name = url["name"]
            # options = form.add_field(desc="Click to subscribe.",
            #                          ftype="boolean",
            #                          label=f"Subscribe to {url_name}?",
            #                          var="choice")
            # form.add_field(var="subscription",
            #                 ftype="hidden",
            #                 value=url["link"])
            options = form.add_field(desc="Click to subscribe.",
                                     ftype="list-single",
                                     label="Subscribe",
                                     var="uri")
            for i in range(10):
                url = UtilityMiscellaneous.pick_a_feed()
                options.addOption(url["name"], url["link"])
            # jid_bare = session["from"].bare
            """
            # Discover subscriptions for current hostname.
            if "@" in jid_bare:
                hostname = jid_bare.split("@")[1]
                # TODO Gemini
                url = "http://" + hostname
            result = await UtilitySubscription.discover(url)
            if not result:
                url = {"url" : url,
                       "index" : None,
                       "name" : None,
                       "code" : None,
                       "error" : True,
                       "exist" : False}
            elif isinstance(result, list):
                for url in result:
                    if url["link"]:
                        url_name = url["name"]
                        url_link = url["link"]
                        options.addOption(f"{url_name}\n{url_link}", url_link)
            else:
                url = result
                # Automatically set priority to 5 (highest)
                if url["link"]: options.addOption(url["name"], url["link"])
            """
            session["allow_complete"] = False
            session["allow_prev"] = True
            # singpolyma: Don"t use complete action if there may be more steps
            # https://gitgud.io/sjehuda/slixfeed/-/merge_requests/13
            # Gajim: On next form Gajim offers no button other than "Commands".
            # Psi: Psi closes the dialog.
            # Conclusion, change session["has_next"] from False to True
            # session["has_next"] = False
            session["has_next"] = True
            session["next"] = functools.partial(XmppForms.subscription_new,
                                                xmpp_instance)
            session["payload"] = form
            session["prev"] = functools.partial(XmppForms.promoted,
                                                xmpp_instance)
        else:
            if chat_type == "error":
                text_warn = f"Could not determine chat type of {jid_bare}."
            elif chat_type == "groupchat":
                text_warn = ("This resource is restricted to moderators of "
                             f"{jid_bare}.")
            else:
                text_warn = "This resource is restricted."
            session["notes"] = [["warn", text_warn]]
        return session

    async def settings(xmpp_instance, iq, session):
        """
        Respond to the initial request for a command.
    
        Arguments:
            iq      -- The iq stanza containing the command request.
            session -- A dictionary of data relevant to the command
                       session. Additional, custom data may be saved
                       here to persist across handler callbacks.
        """
        function_name = sys._getframe().f_code.co_name
        jid = session["from"]
        jid_bare = jid.bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        chat_type = await XmppUtilities.get_chat_type(xmpp_instance, jid_bare)
        if XmppUtilities.is_access(xmpp_instance, jid, chat_type):
            config_account = accounts.retrieve(jid_bare)
            db_file = config_account.database
            form = xmpp_instance["xep_0004"].make_form("form", "Settings")
            form["instructions"] = f"Editing settings of {jid_bare}"
            value = config_account.settings["enabled"]
            value = str(value)
            value = int(value)
            value = True if value else False
            form.add_field(desc="Enable news updates.",
                           ftype="boolean",
                           label="Enabled",
                           value=value,
                           var="enabled")
            value = config_account.settings["media"]
            value = str(value)
            value = int(value)
            value = True if value else False
            form.add_field(desc="Send audio, images or videos if found.",
                           ftype="boolean",
                           label="Display media",
                           value=value,
                           var="media")
            value = config_account.settings["old"]
            value = str(value)
            value = int(value)
            value = True if value else False
            form.add_field(desc="Treat all items of newly added subscriptions as new.",
                           ftype="boolean",
                           # label="Send only new items",
                           label="Include old news",
                           value=value,
                           var="old")
            value = config_account.settings["interval"]
            value = str(value)
            value = int(value)
            value = value/60
            value = int(value)
            value = str(value)
            options = form.add_field(desc="Interval update (in hours).",
                                     ftype="list-single",
                                     label="Interval",
                                     value=value,
                                     var="interval")
            options["validate"]["datatype"] = "xs:integer"
            options["validate"]["range"] = {"minimum": 1,
                                            "maximum": 48}
            i = 1
            while i <= 48:
                x = str(i)
                options.addOption(x, x)
                if i >= 12:
                    i += 6
                else:
                    i += 1
            value = config_account.settings["amount"]
            value = str(value)
            options = form.add_field(desc="Amount of items per update.",
                                     ftype="list-single",
                                     label="Amount",
                                     value=value,
                                     var="amount")
            options["validate"]["datatype"] = "xs:integer"
            options["validate"]["range"] = {"minimum": 1,
                                            "maximum": 5}
            i = 1
            while i <= 5:
                x = str(i)
                options.addOption(x, x)
                i += 1
            value = config_account.settings["archive"]
            value = str(value)
            options = form.add_field(desc="Number of news items to archive.",
                                     ftype="list-single",
                                     label="Archive",
                                     value=value,
                                     var="archive")
            options["validate"]["datatype"] = "xs:integer"
            options["validate"]["range"] = {"minimum": 0,
                                            "maximum": 500}
            i = 0
            while i <= 500:
                x = str(i)
                options.addOption(x, x)
                i += 50
            values = []
            for presence in ("online", "away", "chat", "dnd", "offline", "xa"):
                status_type = "status_" + presence
                if config_account.settings[status_type]:
                    values.append(presence)
            value = config_account.settings["archive"]
            options = form.add_field(desc="Notify for presences.",
                                     ftype="list-multi",
                                     label="Presence",
                                     required=True,
                                     value=values,
                                     var="presence")
            options.addOption("Online", "online")
            options.addOption("Chat", "chat")
            options.addOption("Away", "away")
            options.addOption("Busy", "dnd")
            options.addOption("eXtended Away", "xa")
            #options.addOption("Offline", "offline")
            session["allow_complete"] = True
            # session["has_next"] = True
            session["next"] = functools.partial(XmppForms.settings_complete,
                                                xmpp_instance)
            session["payload"] = form
        else:
            if chat_type == "error":
                text_warn = f"Could not determine chat type of {jid_bare}."
            elif chat_type == "groupchat":
                text_warn = ("This resource is restricted to moderators of "
                             f"{jid_bare}.")
            else:
                text_warn = "This resource is restricted."
            session["notes"] = [["warn", text_warn]]
        return session

    async def settings_complete(xmpp_instance, payload, session):
        function_name = sys._getframe().f_code.co_name
        jid_bare = session["from"].bare
        logger.debug(f"{function_name}	{jid_bare}	Start")
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        # In this case (as is typical), the payload is a form
        values = payload["values"]
        for key in values:
            val = values[key]
            if key == "presence":
                presences = val
                for status in ("online", "away", "chat", "dnd", "offline", "xa"):
                    key = "status_" + status
                    if status in presences:
                        presence_enabled = 1
                    else:
                        presence_enabled = 0
                    await SQLiteGeneral.update_setting_value(db_file, key,
                                                             presence_enabled)
                    config_account.settings[key] = presence_enabled
            else:
                if key in ("enabled", "media", "old"):
                    val = 1 if val == True else 0
                elif key in ("amount", "archive", "interval"):
                    val = int(val)
                    if key == "interval":
                        if val < 1: val = 1
                        val = val * 60
                elif key == "enabled":
                    is_enabled = config_account.settings["enabled"]
                    if val == 1 and str(is_enabled) == 0:
                        logger.info(f"{function_name}	{jid_bare}	Slixfeed has been enabled")
                        presence_body = "📫️ Welcome back."
                        XmppPresence.send(xmpp_instance, jid_bare, presence_body)
                        await asyncio.sleep(5)
                        UtilitySubscriptionTask.restart_task(jid_bare)
                        XmppChatTask.restart_task(xmpp_instance, jid_bare)
                        XmppStatusTask.restart_task(xmpp_instance, jid_bare)
                    elif val == 0 and str(is_enabled) == 1:
                        logger.info(f"{function_name}	{jid_bare}	Slixfeed has been disabled")
                        for task in ("interval", "status"):
                            UtilityTask.stop(config_account.tasks_manager, task)
                        presence_status = "xa"
                        presence_body = "📪️ Send command \"service start\" to receive updates."
                        XmppPresence.send(xmpp_instance, jid_bare, presence_body,
                                          presence_show=presence_status)
                await SQLiteGeneral.update_setting_value(db_file, key, val)
                config_account.settings[key] = val
            """
            val = config_account.settings[key] # NOTE Why would this instruction be added?
            if key in ("enabled", "media", "old"):
                if val == "1":
                    val = "Yes"
                elif val == "0":
                    val = "No"
            elif key == "interval":
                val = int(val)
                val = val/60
                val = int(val)
                val = str(val)
            """
        form = payload
        form["title"] = "Done"
        # session["allow_complete"] = True
        # session["has_next"] = False
        # session["next"] = functools.partial(XmppForms.profile, xmpp_instance)
        session["payload"] = form
        return session
