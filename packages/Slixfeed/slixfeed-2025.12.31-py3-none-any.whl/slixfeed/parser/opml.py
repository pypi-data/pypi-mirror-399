#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import lxml.etree as ET
from slixfeed.utility.logger import UtilityLogger
import sys
#import xml.etree.ElementTree as ET

logger = UtilityLogger(__name__)

class ParserOpml:

    def document(opml: list):
        """Generate an OPML Collection document."""
        e_opml = ET.Element("opml")
        e_opml.set("version", "1.0")
        e_head = ET.SubElement(e_opml, "head")
        ET.SubElement(e_head, "title").text = "Slixfeed World"
        ET.SubElement(e_head, "description").text = "Slixfeed World Collection"
        ET.SubElement(e_head, "generator").text = "Slixfeed"
        ET.SubElement(e_head, "urlPublic").text = "https://git.xmpp-it.net/sch/Slixfeed"
        time_stamp = datetime.datetime.now(datetime.UTC).isoformat()
        ET.SubElement(e_head, "dateCreated").text = time_stamp
        ET.SubElement(e_head, "dateModified").text = time_stamp
        e_body = ET.SubElement(e_opml, "body")
        for item in opml:
            ix, title, uri = item
            e_outline = ET.SubElement(e_body, "outline")
            e_outline.set("text", title)
            e_outline.set("identifier", str(ix))
            e_outline.set("xmlUrl", uri)
        xslt_reference = ET.ProcessingInstruction(
            "xml-stylesheet",
            "type=\"text/xml\" href=\"/xslt/opml.xsl\"")
        e_opml.addprevious(xslt_reference)
        xml_data = ET.ElementTree(e_opml)
        xml_data_bytes = ET.tostring(xml_data, pretty_print=True,
                                     xml_declaration=True, encoding="utf-8")
        xml_data_str = xml_data_bytes.decode("utf-8")
        return xml_data_str
