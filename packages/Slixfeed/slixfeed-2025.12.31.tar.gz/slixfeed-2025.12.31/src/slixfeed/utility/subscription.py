#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

"""

FIXME

1) https://wiki.pine64.org
     File "/slixfeed/crawl.py", line 178, in feed_mode_guess
       address = UtilityUri.join_url(url, parted_url.path.split("/")[1] + path)
                               ~~~~~~~~~~~~~~~~~~~~~~~~~~^^^
   IndexError: list index out of range

TODO

1.1) Attempt to scan more paths: /blog/, /news/ etc., including root / 
   Attempt to scan sub domains
   https://esmailelbob.xyz/en/
   https://blog.esmailelbob.xyz/feed/

2) DeviantArt
   https://www.deviantart.com/nedesem/gallery
   https://backend.deviantart.com/rss.xml?q=gallery:nedesem
   https://backend.deviantart.com/rss.xml?q=nedesem

   https://www.deviantart.com/search?q=
   https://backend.deviantart.com/rss.xml?q=search:

FEEDS CRAWLER PROJECT

3) Mark redirects for manual check

Title : JSON Feed
Link  : https://www.jsonfeed.org/feed.json.xml

Title : JSON Feed
Link  : https://www.jsonfeed.org/feed.json/atom.xml

Title : JSON Feed
Link  : https://www.jsonfeed.org/feed.json/feed.xml

Title : JSON Feed
Link  : https://www.jsonfeed.org/feed.json/feeds/rss/news.xml.php

Title : JSON Feed
Link  : https://www.jsonfeed.org/feed.json/jekyll/feed.xml

Title : JSON Feed
Link  : https://www.jsonfeed.org/feed.json/news.xml

Title : JSON Feed
Link  : https://www.jsonfeed.org/feed.json/news.xml.php

Title : JSON Feed
Link  : https://www.jsonfeed.org/feed.json/rdf.xml

Title : JSON Feed
Link  : https://www.jsonfeed.org/feed.json/rss.xml

Title : JSON Feed
Link  : https://www.jsonfeed.org/feed.json/videos.xml

4) Retrieve active feeds of active accounts and scan the feed with the earliest scanned time first.

"""

import asyncio
from lxml import html
import os
from slixfeed.configuration.singleton import configurations
from slixfeed.parser.atom import ParserAtom
from slixfeed.parser.focuscript import ParserFocuscript
from slixfeed.parser.uri import ParserUri
from slixfeed.sqlite.focuscript import SQLiteFocuscript
from slixfeed.sqlite.general import SQLiteGeneral
from slixfeed.utility.account import accounts
from slixfeed.utility.database import UtilityDatabase
from slixfeed.utility.datetime import UtilityDateTime
from slixfeed.utility.download import UtilityDownload
from slixfeed.utility.gemtext import UtilityGemText
from slixfeed.utility.focuscript import UtilityFocuscript
from slixfeed.utility.logger import UtilityLogger
from slixfeed.utility.markdown import UtilityMarkdown
from slixfeed.utility.opml import UtilityOpml
from slixfeed.utility.parse import UtilityParse
from slixfeed.utility.task import UtilityTask
from slixfeed.utility.text import UtilityText
from slixfeed.utility.uri import UtilityUri
from slixfeed.utility.xml import UtilityXml
from slixfeed.utility.xslt import UtilityXslt
import sys
from urllib.parse import urlsplit # TODO Move to module UtilityUri

logger = UtilityLogger(__name__)

db_file_focuscript = configurations.database_focuscript
directory_focuscript = configurations.directory_focuscript

class UtilitySubscription:

    def export(jid_bare, extension):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        logger.debug(f"{function_name}	{jid_bare}	File extension {extension}")
        dir_cache = configurations.directory_cache
        if not os.path.isdir(dir_cache):
            os.mkdir(dir_cache)
        if not os.path.isdir(dir_cache + "/" + extension):
            os.mkdir(dir_cache + "/" + extension)
        filename = os.path.join(
            dir_cache, extension, "slixfeed_" + UtilityDateTime.timestamp() + "." + extension)
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        subscriptions = SQLiteGeneral.get_feeds(db_file)
        match extension:
            # case "html":
            #     response = "Not yet implemented."
            case "gmi":
                UtilityGemText.generate(jid_bare, filename, subscriptions)
            case "md":
                UtilityMarkdown.generate(jid_bare, filename, subscriptions)
            case "opml":
                UtilityOpml.generate(jid_bare, filename, subscriptions)
            # case "xbel":
            #     response = "Not yet implemented."
        message = f"Subscriptions were successfully exported to {extension}."
        return filename, message

    async def import_opml(jid_bare, uri):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        result = await UtilityDownload.uri(uri)
        count = await UtilityOpml.import_subscriptions(db_file, result)
        if count:
            message = f"Successfully imported {count} subscriptions."
        else:
            message = "OPML file was not imported."
        return message

    async def subscribe(uri, jid_bare, identifier=None):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        scheme = ParserUri.scheme(uri)
        #scheme = uri.split(":")[0]
        if scheme in ("feed", "itpc", "rss"):
            uri = UtilityUri.feed_to_http(uri)
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        feed_id = SQLiteGeneral.get_feed_id(db_file, uri)
        information = {
            "error"         : False,
            "subscriptions" : [],
            "title"         : ""}
        if feed_id:
            title = SQLiteGeneral.get_feed_title(db_file, feed_id)
            message = f"URI {uri} already exist as {title} (ID: {feed_id})."
            information["index"] = str(feed_id)
            information["subscriptions"].append(
                {"name" : title, "link" : uri})
        else:
            information["index"] = title = ""
            config_account = accounts.retrieve(jid_bare)
            setting_old = config_account.settings["old"]
            counter = 0
            while True:
                identifier = UtilityText.identifier(uri, counter)
                if SQLiteGeneral.check_identifier_exist(db_file, identifier):
                    counter += 1
                else:
                    break
            while True:
                result = await UtilityDownload.uri(uri)
                if result["error"]:
                    information["error"] = True
                    information["subscriptions"].append(
                        {"name" : "", "link" : uri})
                    result_message = result["message"]
                    result_status_code = result["status_code"]
                    message = (
                        "An error was encountered while attempting to retrieve "
                        f"data from URI {uri}\n"
                        f"Message: {result_message}.\n"
                        f"Status code: {result_status_code}.")
                    break
                else:
                    content = result["content"]
                    data = UtilityXml.representation(content, uri)
                    focus_id = UtilityFocuscript.supported(uri, data)
                    if data is not None and focus_id:
                        filename = SQLiteFocuscript.select_filename_by_id(
                            db_file_focuscript, focus_id)
                        pathname = os.path.join(directory_focuscript, filename)
                        # uri, condition, filetype
                        stylesheet = ParserFocuscript.stylesheet(pathname)
                        document = UtilityXslt.process(data, stylesheet)
                        #import lxml.etree as ET
                        #content_str = ET.tostring(document, encoding="UTF-8")
                        #data = UtilityParse.xml(content_str, uri)
                        version = SQLiteFocuscript.select_version_by_focus_id(
                            db_file_focuscript, focus_id)
                    #elif (data is not None and
                    #      data.getroot().tag == "{http://www.w3.org/2005/Atom}feed"):
                    elif data is not None:
                        try:
                         data.getroot().tag == "{http://www.w3.org/2005/Atom}feed"
                        except:
                         breakpoint()
                        document = data
                        version = "Atom 1.0"
                    else:
                        document = None
                    if document:
                        # NOTE Consider to call to functions.
                        atom = await ParserAtom.syndication_format(document)
                        # UtilityHtml.purify(content)
                        # UtilityHtml.sanitize(content)
                        # UtilityHtml.complete_href_attributes(uri, content)
                        # UtilityDateTime.convert_struct_time_to_iso8601(date)
                        entries_count = len(document.findall("{http://www.w3.org/2005/Atom}entry"))
                        atom["properties"] = {
                            "entries"     : entries_count,
                            "encoding"    : result["charset"] or document.docinfo.encoding,
                            "identifier"  : identifier,
                            "status_code" : result["status_code"],
                            "valid"       : "", # TODO
                            "version"     : version}
                        await SQLiteGeneral.insert_feed(db_file, uri,
                            atom["feed"]["title"]["text"],
                            atom["properties"]["identifier"],
                            entries=atom["properties"]["entries"],
                            version=atom["properties"]["version"],
                            encoding=atom["properties"]["encoding"],
                            language=atom["feed"]["language"],
                            status_code=atom["properties"]["status_code"],
                            updated=atom["feed"]["updated"],
                            links=atom["feed"]["links"])
                        # NOTE Consider cur.lastrowid
                        feed_id = SQLiteGeneral.get_feed_id(db_file, uri)
                        entries_new = await UtilityDatabase.collect_new_entries(
                            db_file, uri, atom["entries"])
                        await SQLiteGeneral.add_entries_and_update_feed_state(
                            db_file, feed_id, entries_new)
                        if not setting_old:
                            await SQLiteGeneral.mark_feed_as_read(db_file, feed_id)
                        title = atom["feed"]["title"]["text"]
                        message = ("A new subscription has been added to the "
                                    f"subscription list:\n{uri}\n{title}")
                        information["subscriptions"].append(
                            {"name" : title, "link" : uri})
                        break
                    # NOTE
                    # This section concerns to automatic discovery
                    # of subscriptions within (X)HTML documents.
                    else:
                        subscriptions = await UtilitySubscription.discover(uri, content)
                        if not subscriptions:
                            result_status_code = result["status_code"]
                            result_message = result["message"]
                            message = (
                                f"No subscription was found for URI {uri}\n"
                                f"Message: {result_message}.\n"
                                f"Status code: {result_status_code}.")
                            information["subscriptions"].append(
                                {"name" : "", "link" : uri})
                            break
                        elif len(subscriptions) > 1:
                            # Stop the loop and deliver a list of dicts.
                            message = (f"{len(subscriptions)} subscriptions "
                                        f"were detected for {uri}\n")
                            for subscription in subscriptions:
                                name = subscription["name"]
                                link = subscription["link"]
                                message += f"\n{link}\n{name}\n"
                            information["subscriptions"] = subscriptions
                            break
                        else:
                            uri = subscriptions[0]["link"]
                            scheme = ParserUri.scheme(uri)
                            if scheme in ("feed", "itpc", "rss"):
                                uri = UtilityUri.feed_to_http(uri)
                            feed_id = SQLiteGeneral.get_feed_id(db_file, uri)
                            if feed_id:
                                title = SQLiteGeneral.get_feed_title(db_file, feed_id)
                                message = (
                                    f"An automatically discovered URI {uri} "
                                    f"already exist as {title} (ID: {feed_id}).")
                                information["index"] = str(feed_id)
                                information["subscriptions"].append(
                                    {"name" : title, "link" : uri})
                                break
                            # Start over the while loop and try again.

        information["message"] = message
        information["name"] = title
        return information

    async def unsubscribe(jid_bare, ix_uri=None):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        logger.debug(f"{function_name}	{jid_bare}	{ix_uri}")
        if ix_uri:
            message = ""
            sub_removed = []
            invalid_uri = []
            invalid_ixs = []
            config_account = accounts.retrieve(jid_bare)
            db_file = config_account.database
            for ix_or_uri in ix_uri:
                try:
                    feed_id = int(ix_or_uri)
                    uri = SQLiteGeneral.get_feed_uri(db_file, feed_id)
                    if uri:
                        # name = SQLiteGeneral.get_feed_title(db_file, feed_id)
                        ixs = SQLiteGeneral.get_entry_id_indices_by_feed_id(
                            db_file, feed_id)
                        await SQLiteGeneral.delete_entry_id_by_indices(db_file, ixs)
                        await SQLiteGeneral.remove_feed_by_index(db_file, feed_id)
                        sub_removed.append(uri)
                    else:
                        invalid_ix = str(feed_id)
                        invalid_ixs.append(invalid_ix)
                except:
                    uri = ix_or_uri
                    feed_id = SQLiteGeneral.get_feed_id(db_file, uri)
                    if feed_id:
                        ixs = SQLiteGeneral.get_entry_id_indices_by_feed_id(
                            db_file, feed_id)
                        await SQLiteGeneral.delete_entry_id_by_indices(db_file, ixs)
                        await SQLiteGeneral.remove_feed_by_index(db_file, feed_id)
                        # await SQLiteGeneral.remove_feed_by_uri(db_file, uri)
                        sub_removed.append(uri)
                    else:
                        invalid_uri.append(uri)
            if len(sub_removed):
                sub_removed.insert(0, "")
                message += "\n (v) ".join(sub_removed)
            if len(invalid_uri):
                invalid_uri.insert(0, "")
                message += "\n (x) ".join(invalid_uri)
            if len(invalid_ixs):
                invalid_ixs.insert(0, "")
                message += "\n (x) ".join(invalid_ixs)
        else:
            message = "Missing argument. Enter a subscription URI or ID."
        return message

    async def rename(jid_bare, command):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        command = command[7:]
        feed_id = command.split(" ")[0]
        name = " ".join(command.split(" ")[1:])
        if name:
            try:
                feed_id = int(feed_id)
                config_account = accounts.retrieve(jid_bare)
                db_file = config_account.database
                name_old = SQLiteGeneral.get_feed_title(db_file, feed_id)
                if name_old:
                    if name == name_old:
                        message = "Input name is identical to the existing name."
                    else:
                        await SQLiteGeneral.set_feed_title(db_file, feed_id,
                                                    name)
                        message = (f"Subscription #{feed_id} has been renamed"
                                   f"to \"{name}\" (was: {name_old}).")
                else:
                    message = f"Subscription with ID {feed_id} does not exist."
            except:
                message = "Subscription ID must be a numeric value."
        else:
            message = "Missing argument.Enter subscription ID and name."
        return message

    # TODO Do not pass object ClientXMPP.
    # NOTE Pass only parameters that are essential.
    async def scan(account: str):
        """
        Start calling for update check up.
    
        Parameters
        ----------
        jid : str
            Jabber ID.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{account}	Start")
        config_account = accounts.retrieve(account)
        db_file = config_account.database
        uri_rows = SQLiteGeneral.get_active_feeds_url_sorted_by_last_scanned(db_file)
        for uri_row in uri_rows:
            uri = uri_row[0]
            result = await UtilityDownload.uri(uri)
            feed_id = SQLiteGeneral.get_feed_id(db_file, uri)
            if not result["error"]:
                identifier = SQLiteGeneral.get_feed_identifier(db_file, feed_id)
                if not identifier:
                    counter = 0
                    while True:
                        identifier = UtilityText.identifier(uri, counter)
                        if SQLiteGeneral.check_identifier_exist(db_file, identifier):
                            counter += 1
                        else:
                            break
                    await SQLiteGeneral.update_feed_identifier(db_file, feed_id,
                                                               identifier)
                result_status_code = result["status_code"]
                await SQLiteGeneral.update_feed_status(db_file, feed_id,
                                                       result_status_code)
                content = result["content"]
                data = UtilityXml.representation(content, uri)
                focus_id = UtilityFocuscript.supported(uri, data)
                if data is not None and focus_id:
                    filename = SQLiteFocuscript.select_filename_by_id(
                        db_file_focuscript, focus_id)
                    pathname = os.path.join(directory_focuscript, filename)
                    stylesheet = ParserFocuscript.stylesheet(pathname)
                    document = UtilityXslt.process(data, stylesheet)
                    version = SQLiteFocuscript.select_version_by_focus_id(
                        db_file_focuscript, focus_id)
                #elif (data is not None and
                #      data.getroot().tag == "{http://www.w3.org/2005/Atom}feed"):
                #elif (data is not None and
                #      not "tag" in dir(data) and
                #      data.tag != "{http://www.w3.org/1999/xhtml}html"):
                elif (data is not None and
                      "getroot" in dir(data) and
                      data.getroot().tag == "{http://www.w3.org/2005/Atom}feed"):
                    document = data
                    version = "Atom 1.0"
                else:
                    document = None
                if document:
                    atom = await ParserAtom.syndication_format(document)
                    entries_count = len(document.findall("{http://www.w3.org/2005/Atom}entry"))
                    atom["properties"] = {
                        "entries"     : entries_count,
                        "encoding"    : result["charset"] or document.docinfo.encoding,
                        "identifier"  : identifier,
                        "status_code" : result["status_code"],
                        "type"        : "", # TODO
                        "valid"       : "", # TODO
                        "version"     : version} # TODO
                    #await SQLiteGeneral.update_feed_validity(
                    #    db_file, feed_id, atom["properties"]["valid"])
                    await SQLiteGeneral.update_feed_properties(
                        db_file, feed_id, atom)
                    entries_new = await UtilityDatabase.collect_new_entries(
                        db_file, uri, atom["entries"])
                    if entries_new:
                        await SQLiteGeneral.add_entries_and_update_feed_state(
                            db_file, feed_id, entries_new)
                        # TODO Setting "archive" should be fixed to all accounts.
                        config_account = accounts.retrieve(account)
                        limit = config_account.settings["archive"]
                        ix_rows = SQLiteGeneral.get_entry_id_indices_by_feed_id(
                            db_file, feed_id)
                        invalid = {}
                        for ix_row in ix_rows:
                            ix = ix_row[0]
                            read_status = SQLiteGeneral.is_entry_read(db_file, ix)
                            entry_identifier_local = SQLiteGeneral.get_entry_identifier(
                                db_file, ix)
                            valid = False
                            for entry in atom["entries"]:
                                #exists = await UtilityDatabase.entry_exists(uri, entry)
                                #if not exists: invalid[ix] = read_status
                                await asyncio.sleep(0)
                                if "links" in entry:
                                    for link in entry["links"]:
                                        if ("rel" in link and
                                            link["rel"] == "alternate" and
                                            "href" in link):
                                            link_href = UtilityUri.join_url(
                                                uri, link["href"])
                                            link_href = UtilityUri.trim_url(link_href)
                                            entry_identifier_external = UtilityText.md5sum(
                                                link_href)
                                            if entry_identifier_local == entry_identifier_external:
                                                valid = True
                                                continue
                            if not valid: invalid[ix] = read_status
                        if len(invalid):
                            await SQLiteGeneral.process_invalid_entries(
                                db_file, invalid)
                        # TODO Return number of archived entries and add if
                        #      statement to run archive maintainence function.
                        await SQLiteGeneral.maintain_archive(db_file, limit)
                    # await SQLiteGeneral.process_invalid_entries(db_file, ixs)
                    await asyncio.sleep(60 * 2)
            #val = config_account.settings["check"]
            #await asyncio.sleep(60 * float(val))
            # Schedule to call this function again in 90 minutes
            # loop.call_at(
            #     loop.time() + 60 * 90,
            #     loop.create_task,
            #     xmpp_instance.scan(jid)
            # )

    # Move to UtilityCrawler
    async def discover(uri: str, document=None) -> list:
        """
        Parameters
        ----------
        uri : str
            URI.
        document : TYPE
            DESCRIPTION.

        Returns
        -------
        result : list
            Single URI as list or selection of URIs as str.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        logger.debug(f"{function_name}		Probing URI {uri}")
        result = []
        results = []
        if not document:
            response = await UtilityDownload.uri(uri)
            if not response["error"]: document = response["content"]
        try:
            # tree = etree.fromstring(res[0]) # etree is for xml
            tree = html.fromstring(document) # FIXME Variable html is not declared
        except Exception as e:
            logger.error(f"{function_name}		{str(e)}")
            try:
                # /questions/15830421/xml-unicode-strings-with-encoding-declaration-are-not-supported
                # xml = html.fromstring(document.encode("utf-8"))
                # parser = etree.XMLParser(ns_clean=True, recover=True, encoding="utf-8")
                # tree = fromstring(xml, parser=parser)
    
                # /questions/57833080/how-to-fix-unicode-strings-with-encoding-declaration-are-not-supported
                #tree = html.fromstring(bytes(document, encoding="utf8"))
    
                # https://twigstechtips.blogspot.com/2013/06/python-lxml-strings-with-encoding.html
                #parser = etree.XMLParser(recover=True)
                #tree = etree.fromstring(document, parser)
    
                tree = html.fromstring(document.encode("utf-8"))
            except Exception as e:
                logger.error(f"{function_name}		{str(e)}")
                logger.warning(f"{function_name}		Failed to parse URI as feed for {uri}")
                tree = None
        #if tree:
        # FutureWarning: The behavior of this method will change in future versions. Use specific 'len(elem)' or 'elem is not None' test instead.
        if tree is not None:
            if not results:
                logger.info(f"{function_name}		Feed auto-discovery engaged for {uri}")
                results = UtilitySubscription.feed_mode_link(uri, tree)
            if not results:
                logger.info(f"{function_name}		Feed link scan mode engaged for {uri}")
                results = UtilitySubscription.feed_mode_scan(uri, tree)
            if not results:
                logger.info(f"{function_name}		Feed arbitrary mode engaged for {uri}")
                results = UtilitySubscription.feed_mode_guess(uri)
            if not results:
                logger.info(f"{function_name}		No feeds were found for {uri}")
            if results:
                result = await UtilitySubscription.process_selection(uri, results)
        else:
                logger.warning(f"{function_name}		Failed to parse content of {uri}")
        return result

    # TODO Improve scan by gradual decreasing of path
    def feed_mode_guess(uri):
        """
        Lookup for feeds by pathname using HTTP Requests.

        Parameters
        ----------
        db_file : str
            Path to database file.
        uri : str
            URI.

        Returns
        -------
        msg : str
            Message with URIs.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        logger.debug(f"{function_name}		{uri}")
        uris = []
        parted_uri = urlsplit(uri)
        # Check whether URI has path (i.e. not root)
        # Check parted_uri.path to avoid error in case root wasn"t given
        # TODO Make more tests
        pathnames = configurations.pathnames
        if parted_uri.path and parted_uri.path.split("/")[1]:
            pathnames.extend(
                [".atom", ".feed", ".rdf", ".rss"]
                ) if ".rss" not in pathnames else -1
            # if paths.index(".rss"):
            #     paths.extend([".atom", ".feed", ".rdf", ".rss"])
        parted_uri_path = parted_uri.path if parted_uri.path else "/"
        for path in pathnames:
            address = UtilityUri.join_url(uri, parted_uri_path.split("/")[1] + path)
            if address not in uris: uris.append(address)
        return uris

    def feed_mode_scan(uri, tree):
        """
        Scan page for potential feeds by pathname.

        Parameters
        ----------
        db_file : str
            Path to database file.
        uri : str
            URI.
        tree : TYPE
            DESCRIPTION.

        Returns
        -------
        msg : str
            Message with URIs.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        logger.debug(f"{function_name}		{uri}")
        uris = []
        for path in configurations.pathnames:
            # xpath_query = "//*[@*[contains(.,"{}")]]".format(path)
            # xpath_query = "//a[contains(@href,"{}")]".format(path)
            num = 5
            xpath_query = (f"(//a[contains(@href,\"{path}\")])[position()<={num}]")
            addresses = tree.xpath(xpath_query)
            xpath_query = (f"(//a[contains(@href,\"{path}\")])[position()>last()-{num}]")
            addresses += tree.xpath(xpath_query)
            # NOTE Should number of addresses be limited or
            # perhaps be N from the start and N from the end
            for address in addresses:
                address = UtilityUri.join_url(uri, address.xpath("@href")[0])
                if address not in uris: uris.append(address)
        return uris

    def feed_mode_link(uri, tree):
        """
        Discover by (X)HTML element link.

        Parameters
        ----------
        db_file : str
            Path to database file.
        uri : str
            URI.
        tree : TYPE
            DESCRIPTION.
    
        Returns
        -------
        msg : str
            Message with URIs.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        logger.debug(f"{function_name}		{uri}")
        # NOTE RFC 6648 Prefix X- is deprecated
        # TODO Add JSON Feed and twtxt
        xpath_query = ("//link[(@rel=\"alternate\") and "
                       "(@type=\"application/atom+xml\" or "
                       "@type=\"application/rdf+xml\" or "
                       "@type=\"application/rss+xml\" or "
                       "@type=\"text/gemini\")]")
        feeds = tree.xpath(xpath_query)
        if feeds:
            uris = []
            for feed in feeds:
                address = UtilityUri.join_url(uri, feed.xpath("@href")[0])
                if address not in uris: uris.append(address)
            return uris

    # TODO Segregate function into function that returns
    # URIs (string) and Feeds (dict) and function that
    # composes text message (string).
    # Maybe that is not necessary to do.
    async def process_selection(uri, uris):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        logger.debug(f"{function_name}		{uri}")
        subscriptions = []
        for uri in uris:
            result = await UtilityDownload.uri(uri)
            if not result["error"] and result["content"]:
                document = result["content"]
                if UtilityParse.xml(document, uri):
                    subscriptions.append({
                        "name" : "", # TODO
                        "link" : uri})
        return subscriptions

class UtilitySubscriptionTask:

    async def looper(account):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{account}	Start")
        #config_account = accounts.retrieve(account)
        #await asyncio.sleep(60)
        while True:
            logger.info(f"{function_name}	{account}	Looping task: check")
            await UtilitySubscription.scan(account)
            #value = config_account.settings["check"]
            value = 80
            await asyncio.sleep(60 * float(value))

    def restart_task(account):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{account}	Start")
        config_account = accounts.retrieve(account)
        UtilityTask.stop(config_account.tasks_manager, "check")
        config_account.tasks_manager["check"] = asyncio.create_task(
            UtilitySubscriptionTask.looper(account))
        logger.debug(f"{function_name}	{account}	Finish")
