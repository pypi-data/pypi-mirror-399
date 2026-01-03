#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

from slixfeed.utility.datetime import UtilityDateTime
from slixfeed.utility.logger import UtilityLogger
from slixfeed.utility.text import UtilityText
from slixfeed.sqlite.general import SQLiteGeneral
import sys
import xml.etree.ElementTree as ETR

logger = UtilityLogger(__name__)

class UtilityOpml:

    # TODO Consider adding element jid as a pointer of import
    def generate(jid_bare: str, filename: str, subscriptions: list) -> None:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        logger.debug(f"{function_name}	{jid_bare}	Filename: {filename}")
        root = ETR.Element("opml")
        root.set("version", "1.0")
        head = ETR.SubElement(root, "head")
        ETR.SubElement(head, "title").text = jid_bare
        ETR.SubElement(head, "description").text = (
            "Set of subscriptions exported by Slixfeed")
        ETR.SubElement(head, "generator").text = "Slixfeed"
        ETR.SubElement(head, "urlPublic").text = (
            "https://schapps.woodpeckersnest.space")
        time_stamp = UtilityDateTime.current_time()
        ETR.SubElement(head, "dateCreated").text = time_stamp
        ETR.SubElement(head, "dateModified").text = time_stamp
        body = ETR.SubElement(root, "body")
        for subscription in subscriptions:
            outline = ETR.SubElement(body, "outline")
            outline.set("text", subscription[1])
            outline.set("xmlUrl", subscription[2])
            # outline.set("type", subscription[2])
        tree = ETR.ElementTree(root)
        tree.write(filename)

    async def import_subscriptions(db_file, result):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        if not result["error"]:
            document = result["content"]
            root = ETR.fromstring(document)
            before = SQLiteGeneral.get_number_of_items(db_file, "feeds_properties")
            subscriptions = []
            for child in root.findall(".//outline"):
                uri = child.get("xmlUrl")
                title = child.get("text")
                counter = 0
                while True:
                    identifier = UtilityText.identifier(uri, counter)
                    if SQLiteGeneral.check_identifier_exist(db_file, identifier):
                        counter += 1
                    else:
                        break
                subscription = {
                    "identifier" : identifier,
                    "title" : title,
                    "uri" : uri
                    }
                subscriptions.append(subscription)
            await SQLiteGeneral.import_feeds(db_file, subscriptions)
            await SQLiteGeneral.add_metadata(db_file)
            after = SQLiteGeneral.get_number_of_items(db_file, "feeds_properties")
            difference = after - before
            return difference
