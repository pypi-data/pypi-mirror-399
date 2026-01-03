#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

from datetime import datetime
import lxml.etree as ET
from lxml.etree import XPathEvalError
import markdown
import re
from slixfeed.configuration.singleton import configurations
from slixfeed.sqlite.focuscript import SQLiteFocuscript
from slixfeed.utility.logger import UtilityLogger
import sys
from typing import Any

json_types = dict(zip(
    map(type, [False,   {1:10}, 1,     0.1,   [],   "",    None]),
               "boolean map     number number array string null".split()
))

logger = UtilityLogger(__name__)

db_file_focuscript = configurations.database_focuscript

xmlns = {
    "atom"      : "http://www.w3.org/2005/Atom",
    "atom03"    : "http://purl.org/atom/ns#",
    "atomsub"   : "urn:xmpp:microblog:0",
    "doap"      : "http://usefulinc.com/ns/doap#",
    "foaf"      : "http://xmlns.com/foaf/0.1/",
    "metalink4" : "urn:ietf:params:xml:ns:metalink",
    "pubsub"    : "http://jabber.org/protocol/pubsub",
    "rdf"       : "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs"      : "http://www.w3.org/2000/01/rdf-schema#",
    "rss"       : "http://purl.org/rss/1.0/",
    "rss09"     : "http://my.netscape.com/rdf/simple/0.9/",
    "rss10"     : "https://web.resource.org/rss/1.0/",
    "tf"        : "http://diggy.i2p/focus",
    "xf"        : "http://www.w3.org/2005/xpath-functions",
    "smf"       : "http://www.simplemachines.org/xml/recent",
    "xhtml"     : "http://www.w3.org/1999/xhtml",
    "xmpp"      : "https://linkmauve.fr/ns/xmpp-doap#",
    "xspf"      : "http://xspf.org/ns/0/"}

class UtilityFocuscript:

    def convert_json_to_xml(json_data: dict[str, Any]) -> ET._Element:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        def create_xml_element(ancestor: ET.Element, data: Any) -> None:
            if isinstance(data, dict):
                for key, value in data.items():
                    tag_name = json_types[type(value)]
                    descendant = ET.SubElement(ancestor, f"{{{xmlns["xf"]}}}{tag_name}", key=key)
                    create_xml_element(descendant, value)
            elif isinstance(data, list):
                for item in data:
                    tag_name = json_types[type(item)]
                    descendant = ET.SubElement(ancestor, f"{{{xmlns["xf"]}}}{tag_name}")
                    create_xml_element(descendant, item)
            else:
                ancestor.text = str(data)
        map = ET.Element("map", xmlns=xmlns["xf"])
        create_xml_element(map, json_data)
        return map

    def convert_twtxt_to_xml(twtxt_data: str) -> ET._Element:
        """
        Convert Twtxt data to XML format.

        :param twtxt_data: Twtxt data to convert.
        :type twtxt_data: str.

        :return: XML string representation.
        :rtype: str
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        metadata = {}
        for line in twtxt_data.split("\n"):
            if line.startswith("#"):
                if "=" in line:
                    key, value = line[1:].split("=")
                    key_strip = key.strip()
                    value_strip = value.strip()
                    if key_strip in ("follow", "link"):
                        if key_strip in metadata:
                            metadata[key_strip].append(value_strip)
                        else:
                            metadata[key_strip] = []
                    else:
                        metadata[key_strip] = value_strip
            else:
                break
        entries = []
        for line in twtxt_data.split("\n"):
            if line and not line.startswith("#"):
                context = None
                try:
                    date, text = line.split("	")
                except Exception as e:
                    # Append a line to previous entry.
                    entries[len(entries)-1][2] += "\n\n" + line
                    continue
                if text.startswith("(#"):
                    context = text[2:text.index(")")]
                    text = text[text.index(") ")+2:]
                entry = [date, context, text]
                entries.append(entry)
        twtxt = ET.Element("twtxt", xmlns="https://twtxt.dev/")
        for key in metadata:
            if key in ("next", "prev"):
                data = metadata[key].split()
                href = data.pop()
                title = ' '.join(data)
                if key == "prev":
                    relation = "previous"
                elif key == "next":
                    relation = key
                ET.SubElement(twtxt, "link", href=href, rel=relation, title=title)
            if key in ("follow", "link"):
                #if isinstance(metadata[key], list):
                for value in metadata[key]:
                    data = value.split()
                    href = data.pop()
                    title = ' '.join(data)
                    if key == "link":
                        relation = "related"
                    elif key == "follow":
                        relation = "follow"
                    ET.SubElement(twtxt, "link", href=href, rel=relation, title=title)
            else:
                ET.SubElement(twtxt, key).text = metadata[key]
        for date, context, text in entries:
            text_split = text.split()
            for cell_curr in text_split:
                if cell_curr.startswith("@<"):
                    cell_curr_mod = cell_curr.replace("@<", "[")
                    cell_next = text_split[text_split.index(cell_curr)+1]
                    cell_next_mod = "](" + cell_next.replace(">", ")")
                    text_split[text_split.index(cell_curr)+1] = cell_next_mod
                    text_split[text_split.index(cell_curr)] = cell_curr_mod
            text = ' '.join(text_split)
            text = text.replace(" ](", "](")
            # FIXME Line break is not realized.
            # NOTE Consider to process and convert line by line.
            text = markdown.markdown(text)
            if context:
                attributes = {"date" : date, "context" : context}
            else:
                attributes = {"date" : date}
            link = ET.SubElement(twtxt, "entry", attributes)
            link.text = text
        return twtxt

    def convert_gemtext_to_xml(gmi_data: str) -> ET._Element:
        """
        Convert Gemtext data to XML format.

        :param gmi_data: Gemtext data to convert.
        :type gmi_data: str.

        :return: XML string representation.
        :rtype: str.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        gemtext = ET.Element("gemini", xmlns="gemini://geminiprotocol.net/")
        is_line_code = False
        content_data = []
        gmi_data_split = gmi_data.split("\n")
        # Remove empty lines.
        for line in gmi_data_split:
            if not line: gmi_data_split.remove("")
        # Iterate lines and allocate respective XML tag.
        for line in gmi_data_split:
            if line.startswith("*"):
                bullet = ET.SubElement(gemtext, "bullet")
                bullet.text = line[1:].strip()
            elif line.startswith("```"):
                if is_line_code:
                    ascii = ET.SubElement(gemtext, "ascii")
                    ascii.text = "\n".join(content_data)
                    is_line_code = False
                else:
                    content_data.clear()
                    is_line_code = True
            elif is_line_code:
              content_data.append(line)
            elif line.startswith("###"):
                h3 = ET.SubElement(gemtext, "h3")
                h3.text = line[3:].strip()
            elif line.startswith("##"):
                h2 = ET.SubElement(gemtext, "h2")
                h2.text = line[2:].strip()
            elif line.startswith("#"):
                h1 = ET.SubElement(gemtext, "h1")
                h1.text = line[1:].strip()
            elif line.startswith(">"):
                epigraph = ET.SubElement(gemtext, "epigraph")
                epigraph.text = line[1:].strip()
            elif line.startswith("=>"):
                line_split = line[2:].split()
                if len(line_split) > 2:
                    link = line_split[0]
                    date = line_split[1]
                    try:
                        datetime.strptime(date, "%Y-%m-%d")
                        text = " ".join(line_split[2:])
                        attributes = {"date" : date, "href" : link, "title" : text.strip()}
                    except:
                        text = " ".join(line_split[1:])
                        attributes = {"href" : link, "title" : text.strip()}
                    link = ET.SubElement(gemtext, "link", attributes)
            elif line:
                paragraph = ET.SubElement(gemtext, "paragraph")
                paragraph.text = line.strip()
        return gemtext

    # NOTE Filetype recognition by content might be helpful.
    def supported(uri: str, data: ET._Element | ET._ElementTree):
        """
        Determine whether a given URI is supported by a Focuscript.
        Determine whether a given type of format of a given document is supported or not.

        :param uri: A URI.
        :type uri: str.

        :param data: A parsed XML document.
        :type data: ET._Element or ET._ElementTree.

        :return condition_id: ID of an XPath Query.
        :rtype: int
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{uri}	Start")
        protocol = uri.split(":")[0]
        protocol_match_rule_rows = SQLiteFocuscript.select_rows_match_protocol(
            db_file_focuscript)
        for protocol_match_rule_row in protocol_match_rule_rows:
            protocol_match_rule = protocol_match_rule_row["protocol"]
            if protocol_match_rule == "*": protocol_match_rule = ".*"
            if re.match(protocol_match_rule, protocol):
                protocol_id = protocol_match_rule_row["id"]
                break
        hostname = uri.split("://")[1].split("/")[0]
        hostname_match_rule_rows = SQLiteFocuscript.select_rows_match_hostname(
            db_file_focuscript)
        for hostname_match_rule_row in hostname_match_rule_rows:
            hostname_match_rule = hostname_match_rule_row["hostname"]
            if hostname_match_rule == "*": hostname_match_rule = ".*"
            if re.match(hostname_match_rule, hostname):
                hostname_id = hostname_match_rule_row["id"]
                break
        pathname = "/".join(uri.split("://")[1].split("/")[1:])
        pathname_match_rule_rows = SQLiteFocuscript.select_rows_match_pathname(
            db_file_focuscript)
        for pathname_match_rule_row in pathname_match_rule_rows:
            pathname_match_rule = pathname_match_rule_row["pathname"]
            if pathname_match_rule == "*": pathname_match_rule = ".*"
            if re.match(pathname_match_rule, pathname):
                pathname_id = pathname_match_rule_row["id"]
                break

        """
        hostname_rule = SQLiteFocuscript.select_match_hostname_by_id(
            db_file_focuscript, hostname_id)
        protocol_rule = SQLiteFocuscript.select_match_protocol_by_id(
            db_file_focuscript, protocol_id)
        pathname_rule = SQLiteFocuscript.select_match_pathname_by_id(
            db_file_focuscript, pathname_id)
        """

        # Collect all Focuscripts which match rules apply to.
        focus_id_rows = SQLiteFocuscript.select_focus_ids_by_match_ids(
            db_file_focuscript, protocol_id, hostname_id, pathname_id)

        # Examine condition (XPath Query) of each Focuscript.
        condition_id_selected = None
        match_rate_highest = 0
        if isinstance(data, ET._ElementTree):
            namespaces_document = data.getroot().nsmap
        elif isinstance(data, ET._Element):
            namespaces_document = data.nsmap
        for focus_id_row in focus_id_rows:
            focus_id = focus_id_row["focus_id"]
            condition_id = SQLiteFocuscript.select_condition_id_by_id(
                db_file_focuscript, focus_id)
            query = SQLiteFocuscript.select_query_by_id(
                db_file_focuscript, condition_id)
            namespace_rows = SQLiteFocuscript.select_namespaces_by_focus_id(
                db_file_focuscript, focus_id)
            namespaces_stylesheet = {}
            for namespace_row in namespace_rows:
                prefix_id = namespace_row["prefix_id"]
                xmlns_id = namespace_row["xmlns_id"]
                xmlns = SQLiteFocuscript.select_xmlns_by_id(
                    db_file_focuscript, xmlns_id)
                prefix = SQLiteFocuscript.select_prefix_by_id(
                    db_file_focuscript, prefix_id)
                namespaces_stylesheet[prefix] = xmlns
            """
            filename = SQLiteFocuscript.select_filename_by_condition_id(
                db_file_focuscript, condition_id)
            pathname = os.path.join(directory_focuscript, filename)
            stylesheet = ParserFocuscript.stylesheet(pathname)
            namespaces_stylesheet = stylesheet.nsmap
            """
            try:
                # Check whether condition matches.
                if data.xpath(query, namespaces=namespaces_stylesheet):
                    # Select a condition_id (of a focus_id) with
                    # the highest match of most XML Namespaces.
                    match_rate = 0
                    for prefix_document in namespaces_document:
                        for prefix_stylesheet in namespaces_stylesheet:
                            if namespaces_document[prefix_document] == namespaces_stylesheet[prefix_stylesheet]:
                                
                                match_rate += 1
                    if not condition_id_selected:
                        condition_id_selected = condition_id
                    if match_rate > match_rate_highest:
                        condition_id_selected = condition_id
                        match_rate_highest = match_rate
            except XPathEvalError as e:
                logger.error(f"{function_name}	{uri}	{str(e)}")
            except Exception as e:
                logger.error(f"{function_name}	{uri}	{str(e)}")

        focus_id = SQLiteFocuscript.select_focus_id_by_condition_id(
            db_file_focuscript, condition_id_selected)
        return focus_id

        # attr = data.getroot().attrib

        # root_name = data.docinfo.root_name
        # encoding = data.docinfo.encoding

        # supported = True if is supported by a focuscript
        # supported = False is if not

    def charge(filename=None):
        """Charge Focuscript into memory."""
        for script in os.listdir(directory_scripts):
            if script.endswith(".focus"):
                filename = os.path.join(directory_scripts, script)
                data = open(filename, "r").read()
                metadata = ParserFocuscript.metadata(data)
                

    def discharge(identifier):
        """Discharge Focuscript from memory."""
        pass

    def recharge(identifier):
        """Recharge Focuscript into memory."""
        pass
