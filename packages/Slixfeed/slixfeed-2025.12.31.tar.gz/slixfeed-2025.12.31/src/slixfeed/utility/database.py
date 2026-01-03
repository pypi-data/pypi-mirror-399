#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

import asyncio
import os
from slixfeed.utility.account import accounts
from slixfeed.sqlite.general import SQLiteGeneral
from slixfeed.utility.logger import UtilityLogger
from slixfeed.utility.text import UtilityText
from slixfeed.utility.uri import UtilityUri
import sys

logger = UtilityLogger(__name__)

class UtilityDatabase:

    async def instantiate(dir_data: str, account: str, defaults=None) -> None:
        """
        Instantiate action on database and return its filename location.
    
        Parameters
        ----------
        dir_data : str
            Directory.
        account : str
            Jabber ID.
    
        Returns
        -------
        db_file
            Filename.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{account}	Start")
        db_file = os.path.join(dir_data, "sqlite", f"{account}.db")
        SQLiteGeneral.create_a_database_for_an_account(db_file)
        for key in ("archive", "enabled", "filter", "interval", "length",
                    "media", "old", "omemo", "quantum", "random",
                    "status_online", "status_away", "status_chat", "status_dnd",
                    "status_xa", "status_offline"):
            if not SQLiteGeneral.is_setting_key(db_file, key):
            #if defaults and not SQLiteGeneral.is_setting_key(db_file, key):
                value = defaults[key]
                print(account, key, value)
                await SQLiteGeneral.set_setting_value(db_file, key, value)
        logger.debug(f"{function_name}	{account}	Finish")

    async def collect_new_entries(db_file, uri, entries) -> list:
        """Add entries that are not yet stored in database."""
        entries_new = []
        for entry in entries:
            for link in entry["links"]:
                await asyncio.sleep(0)
                if ("rel" in link and
                    link["rel"] == "alternate" and
                    "href" in link):
                    link_href = link["href"]
                    entry_link = UtilityUri.join_url(uri, link_href)
                    entry_link_trim = UtilityUri.trim_url(entry_link)
                    entry_id = UtilityText.md5sum(entry_link_trim)
                    if not SQLiteGeneral.get_entry_id_by_identifier(
                        db_file, entry_id):
                        entry["id"] = entry_id
                        entries_new.append(entry)
        return entries_new

    async def entry_valid(entry_id_local, uri, entry) -> bool:
        """Check whether a given stored entry is present in source document."""
        if "links" in entry:
            for link in entry["links"]:
                await asyncio.sleep(0)
                if ("rel" in link and
                    link["rel"] == "alternate" and
                    "href" in link):
                    link_href = link["href"]
                    entry_link = UtilityUri.join_url(uri, link_href)
                    entry_link_trim = UtilityUri.trim_url(entry_link)
                    entry_id = UtilityText.md5sum(entry_link_trim)
                    if entry_id_local == entry_id:
                        return True

    async def mark(jid_bare, ix_url=None):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        logger.debug(f"{function_name}	{jid_bare}	{ix_url}")
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        if ix_url:
            sub_marked = []
            url_invalid = []
            ixs_invalid = []
            message = ""
            for ix_or_url in ix_url:
                try:
                    ix = int(ix_or_url)
                    url = SQLiteGeneral.get_feed_url(db_file, ix)
                    if url:
                        # name = SQLiteGeneral.get_feed_title(db_file, ix)
                        await SQLiteGeneral.mark_feed_as_read(db_file, ix)
                        sub_marked.append(url)
                    else:
                        ixs_invalid.append(str(ix))
                except:
                    url = ix_or_url
                    feed_id = SQLiteGeneral.get_feed_id(db_file, url)
                    if feed_id:
                        await SQLiteGeneral.mark_feed_as_read(db_file, feed_id)
                        sub_marked.append(url)
                    else:
                        url_invalid.append(url)
            if len(sub_marked):
                message += "The following subscriptions have been marked as read.\n\n"
                for url in sub_marked:
                    message += f"{url}\n"
            if len(url_invalid):
                urls = ", ".join(url_invalid)
                message += f"The following URLs do not exist:\n\n{urls}\n"
            if len(ixs_invalid):
                ixs = ", ".join(ixs_invalid)
                message += f"The following indexes do not exist:\n\n{ixs}\n"
        else:
            await SQLiteGeneral.mark_all_as_read(db_file)
            message = "All subscriptions have been marked as read."
        return message

    def search(jid_bare, query):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        logger.debug(f"{function_name}	{jid_bare}	{query}")
        if query:
            if len(query) > 3:
                config_account = accounts.retrieve(jid_bare)
                db_file = config_account.database
                results = SQLiteGeneral.search_entries(db_file, query)
                message = f"{len(results)} Search results for \"{query}\".\n"
                if len(results):
                    for result in results:
                        link = result["link"]
                        title = result["title"]
                        message += f"\n{link}\n*{title}*\n"
                else:
                    message = f"No results were found for \"{query}\"."
            else:
                message = "Enter at least 4 characters to search."
        else:
            message = "Missing search query."
        return message
