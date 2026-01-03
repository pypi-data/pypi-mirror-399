#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import lxml.etree as ET
import os
from slixfeed.configuration.singleton import configurations
from slixfeed.parser.focuscript import ParserFocuscript
from slixfeed.sqlite.focuscript import SQLiteFocuscript
from slixfeed.utility.download import UtilityDownload
from slixfeed.utility.focuscript import UtilityFocuscript
from slixfeed.utility.xml import UtilityXml
from slixfeed.utility.xslt import UtilityXslt
import sys

db_file_focuscript = configurations.database_focuscript
directory_focuscript = configurations.directory_focuscript

xmlns = {
    "focus" : "http://diggy.i2p/focus",
    "xsl"   : "http://www.w3.org/1999/XSL/Transform"}

def start():
    if len(sys.argv) == 1:
        pathname = input("Enter a pathname to a Focuscript: ")
        location = input("Enter a location to retrieve data from: ")
    elif len(sys.argv) == 3:
        location = sys.argv[2]
        if location.startswith("/"):
            location = "file://" + location
        elif location.startswith("~/"):
            location = "file://" + os.environ.get("HOME") + location[1:]
        result = asyncio.run(UtilityDownload.uri(location))
        if result["error"]:
            result_message = result["message"]
            result_status_code = result["status_code"]
            result = (
                "<feed xmlns=\"http://www.w3.org/2005/Atom\"><generator "
                "uri=\"https://git.xmpp-it.net/sch/Focus\" version=\"1.0\">The "
                "Focus</generator><entry><title>Network error.</title><summary"
                " type=\"xhtml\"><div xmlns=\"http://www.w3.org/1999/xhtml\">"
                "An error was encountered while attempting to retrieve data "
                f"from URI <code>{location}</code><br/><br/>Message: <code>"
                f"{result_message}</code>.<br/><br/>Status code: <code>"
                f"{result_status_code}</code></div></summary></entry></feed>")
        else:
            content = result["content"]
            data = UtilityXml.representation(content, location)
            if sys.argv[1] == "auto":
                focus_id = UtilityFocuscript.supported(location, data)
                if focus_id:
                    filename = SQLiteFocuscript.select_filename_by_id(
                        db_file_focuscript, focus_id)
                    pathname = os.path.join(directory_focuscript, filename)
                else:
                    result = (
                        "<feed xmlns=\"http://www.w3.org/2005/Atom\">"
                        "<generator uri=\"https://git.xmpp-it.net/sch/Focus\""
                        "version=\"1.0\">The Focus</generator><entry><title>"
                        "URI is not supported.</title><summary type=\"text\">"
                        "There is no Focuscript which supports the document of "
                        "the given URI.</summary></entry></feed>")
            else:
                pathname = sys.argv[1]
            doc = ET.parse(pathname)
            #if doc.xpath("//focus:focus", namespaces=xmlns):
            #elif doc.xpath("//xsl:transform", namespaces=xmlns):
            #nsmap = doc.getroot().nsmap
            #if nsmap["xsl"] == xmlns["xsl"]:
            #elif nsmap[None] == xmlns["focus"]:
            tag = doc.getroot().tag
            match tag:
                case "{http://diggy.i2p/focus}focus":
                    compatible = True
                    stylesheet = ParserFocuscript.stylesheet(pathname)
                case "{http://www.w3.org/1999/XSL/Transform}transform":
                    compatible = True
                    stylesheet = doc
                case _:
                    compatible = False
                    result = (
                        "<feed xmlns=\"http://www.w3.org/2005/Atom\"><generator "
                        "uri=\"https://git.xmpp-it.net/sch/Focus\" version=\"1.0\">"
                        "The Focus</generator><entry><title>Error: Invalid "
                        "stylesheet.</title><summary>Focuscript or XSLT stylesheet "
                        f"document \"{pathname}\" does not appear to be compatible."
                        "</summary></entry></feed>")
            if compatible:
                document = UtilityXslt.process(data, stylesheet)
                result = ET.tostring(document, pretty_print=True).decode()
    else:
        result = (
            "<feed xmlns=\"http://www.w3.org/2005/Atom\"><generator "
            "uri=\"https://git.xmpp-it.net/sch/Focus\" version=\"1.0\">The "
            "Focus</generator><entry><title>Error: Missing argument.</title>"
            "<summary>Please enter a location of a Focuscript and a URI."
            "</summary></entry></feed>")
    sys.stdout.flush()
    sys.stdout.write(result)
    sys.exit()
