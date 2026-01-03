#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

FIXME

1) feed_mode_scan does not find feed for https://www.blender.org/
   even though it should be according to the pathnames dictionary.

TODO

1) Function scan at "for entry in entries"
   Suppress directly calling function "add_entry" (accept db_file)
   Pass a list of valid entries to a new function "add_entries"
   (accept db_file) which would call function "add_entry" (accept cur).
   * accelerate adding of large set of entries at once.
   * prevent (or mitigate halt of consequent actions).
   * reduce I/O.

2) Call sqlite function from function statistics.
   Returning a list of values might not be a good practice.

3) Special statistics for operator:
   * Size of database(s);
   * Amount of JIDs subscribed;
   * Amount of feeds of all JIDs;
   * Amount of entries of all JIDs.

4) Replace SQLiteGeneral.remove_nonexistent_entries by SQLiteGeneral.check_entry_exist
   Same check, just reverse.

"""

import asyncio
import os
from slixfeed.config import Config
from slixfeed.utility.datetime import UtilityDateTime
from slixfeed.utility.html import UtilityHtml
from slixfeed.utility.logger import UtilityLogger
from slixfeed.sqlite.general import SQLiteGeneral
from slixfeed.utility.uri import UtilityUri
from slixmpp.xmlstream import ET
import sys
from urllib.parse import urlsplit
import xml.etree.ElementTree as ETR

logger = UtilityLogger(__name__)

class Feed:

    def pack_entry_into_dict(db_file, entry):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        entry_id = entry[0]
        authors = SQLiteGeneral.get_authors_by_entry_id(db_file, entry_id)
        entry_authors = []
        for author in authors:
            entry_author = {
                "name": author[2],
                "email": author[3],
                "url": author[4]}
            entry_authors.append(entry_author)
        contributors = SQLiteGeneral.get_contributors_by_entry_id(db_file, entry_id)
        entry_contributors = []
        for contributor in contributors:
            entry_contributor = {
                "name": contributor[2],
                "email": contributor[3],
                "url": contributor[4]}
            entry_contributors.append(entry_contributor)
        links = SQLiteGeneral.get_links_by_entry_id(db_file, entry_id)
        entry_links = []
        for link in links:
            entry_link = {
                "url": link[2],
                "type": link[3],
                "rel": link[4],
                "size": link[5]}
            entry_links.append(entry_link)
        tags = SQLiteGeneral.get_tags_by_entry_id(db_file, entry_id)
        entry_tags = []
        for tag in tags:
            entry_tag = {
                "term": tag[2],
                "scheme": tag[3],
                "label": tag[4]}
            entry_tags.append(entry_tag)
        contents = SQLiteGeneral.get_contents_by_entry_id(db_file, entry_id)
        entry_contents = []
        for content in contents:
            entry_content = {
                "text": content[2],
                "type": content[3],
                "base": content[4],
                "lang": content[5]}
            entry_contents.append(entry_content)
        feed_entry = {
            "authors"      : entry_authors,
            "category"     : entry[10],
            "comments"     : entry[12],
            "contents"     : entry_contents,
            "contributors" : entry_contributors,
            "summary_base" : entry[9],
            "summary_lang" : entry[7],
            "summary_text" : entry[6],
            "summary_type" : entry[8],
            "enclosures"   : entry[13],
            "href"         : entry[11],
            "link"         : entry[3],
            "links"        : entry_links,
            "published"    : entry[14],
            "rating"       : entry[13],
            "tags"         : entry_tags,
            "title"        : entry[4],
            "title_type"   : entry[3],
            "updated"      : entry[15]}
        return feed_entry
