#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

from slixfeed.utility.logger import UtilityLogger
from slixmpp.xmlstream import ET
import sys

logger = UtilityLogger(__name__)

class UtilityAtom:

    def create_rfc4287_entry(feed_entry):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        node_entry = ET.Element("entry")
        node_entry.set("xmlns", "http://www.w3.org/2005/Atom")
        # Title
        title = ET.SubElement(node_entry, "title")
        if feed_entry["title"]:
            if feed_entry["title_type"]: title.set("type", feed_entry["title_type"])
            title.text = feed_entry["title"]
        elif feed_entry["summary_text"]:
            if feed_entry["summary_type"]: title.set("type", feed_entry["summary_type"])
            title.text = feed_entry["summary_text"]
            # if feed_entry["summary_base"]: title.set("base", feed_entry["summary_base"])
            # if feed_entry["summary_lang"]: title.set("lang", feed_entry["summary_lang"])
        else:
            title.text = feed_entry["published"]
        # Some feeds have identical content for contents and summary
        # So if content is present, do not add summary
        if feed_entry["contents"]:
            # Content
            for feed_entry_content in feed_entry["contents"]:
                content = ET.SubElement(node_entry, "content")
                # if feed_entry_content["base"]: content.set("base", feed_entry_content["base"])
                if feed_entry_content["lang"]: content.set("lang", feed_entry_content["lang"])
                if feed_entry_content["type"]: content.set("type", feed_entry_content["type"])
                content.text = feed_entry_content["text"]
        else:
            # Summary
            summary = ET.SubElement(node_entry, "summary") # TODO Try "content"
            # if feed_entry["summary_base"]: summary.set("base", feed_entry["summary_base"])
            # TODO Check realization of "lang"
            if feed_entry["summary_type"]: summary.set("type", feed_entry["summary_type"])
            if feed_entry["summary_lang"]: summary.set("lang", feed_entry["summary_lang"])
            summary.text = feed_entry["summary_text"]
        # Authors
        for feed_entry_author in feed_entry["authors"]:
            author = ET.SubElement(node_entry, "author")
            name = ET.SubElement(author, "name")
            name.text = feed_entry_author["name"]
            if feed_entry_author["url"]:
                uri = ET.SubElement(author, "uri")
                uri.text = feed_entry_author["url"]
            if feed_entry_author["email"]:
                email = ET.SubElement(author, "email")
                email.text = feed_entry_author["email"]
        # Contributors
        for feed_entry_contributor in feed_entry["contributors"]:
            contributor = ET.SubElement(node_entry, "author")
            name = ET.SubElement(contributor, "name")
            name.text = feed_entry_contributor["name"]
            if feed_entry_contributor["url"]:
                uri = ET.SubElement(contributor, "uri")
                uri.text = feed_entry_contributor["url"]
            if feed_entry_contributor["email"]:
                email = ET.SubElement(contributor, "email")
                email.text = feed_entry_contributor["email"]
        # Category
        category = ET.SubElement(node_entry, "category")
        category.set("category", feed_entry["category"])
        # Tags
        for feed_entry_tag in feed_entry["tags"]:
            tag = ET.SubElement(node_entry, "category")
            tag.set("term", feed_entry_tag["term"])
        # Link
        link = ET.SubElement(node_entry, "link")
        link.set("href", feed_entry["link"])
        # Links
        for feed_entry_link in feed_entry["links"]:
            link = ET.SubElement(node_entry, "link")
            link.set("href", feed_entry_link["url"])
            link.set("type", feed_entry_link["type"])
            link.set("rel", feed_entry_link["rel"])
        # Date updated
        if feed_entry["updated"]:
            updated = ET.SubElement(node_entry, "updated")
            updated.text = feed_entry["updated"]
        # Date published
        if feed_entry["published"]:
            published = ET.SubElement(node_entry, "published")
            published.text = feed_entry["published"]
        return node_entry
