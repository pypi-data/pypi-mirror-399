#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from io import BytesIO
import json
from json.decoder import JSONDecodeError
import lxml.etree as ET
from slixfeed.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

class UtilityParse:

    def json(content: str, uri: str) -> dict:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{uri}	Start")
        try:
            return json.loads(content)
        except JSONDecodeError as e:
            logger.error(f"{function_name}	{uri}	A parsing error has occurred.")
            logger.debug(f"{function_name}	{uri}	{e}")
        except Exception as e:
            logger.error(f"{function_name}	{uri}	An error has occurred while attempting to parse content.")
            logger.debug(f"{function_name}	{uri}	{e}")

    def xml(content: str, uri: str) -> ET._ElementTree:
        """
        Parse XML data; and return a parsed version of it, and state of validity.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{uri}	Start")
        try:
            #return ET.parse(BytesIO(content.encode())), True
            return ET.parse(BytesIO(content.encode()))
        except ET.ParseError as e:
            logger.error(f"{function_name}	{uri}	A parsing error has occurred.")
            logger.debug(f"{function_name}	{uri}	{e}")
            logger.debug(f"{function_name}	{uri}	Attempting to parse by recovery mode.")
            #corrector = ET.XMLParser(encoding='utf-8', recover=True)
            #return ET.parse(StringIO(content), corrector)
            corrector = ET.XMLParser(recover=True)
            #return ET.parse(BytesIO(content.encode()), corrector), False
            return ET.parse(BytesIO(content.encode()), corrector)
        except Exception as e:
            logger.error(f"{function_name}	{uri}	An error has occurred while attempting to parse content.")
            logger.debug(f"{function_name}	{uri}	{e}")

    def html(content: str, uri: str) -> ET._ElementTree:
        """
        Parse an (X)HTML document;
        Create an XHTML document;
        Set XML Namespace of XHTML, if missing; then
        Move descendants of (X)HTML document to XHTML document.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{uri}	Start")
        try:
            data = ET.HTML(content.encode())
            ET.strip_elements(data, "script", with_tail=False)
            ET.strip_tags(data, ET.Comment)
            nsmap = data.nsmap
            #if (not None in nsmap or
            #    None in nsmap and
            #    nsmap[None] != "http://www.w3.org/1999/xhtml"):
            if not None in nsmap:
                logger.debug(f"{function_name}	{uri}	Setting XML Namespace to http://www.w3.org/1999/xhtml.")
                nsmap[None] = "http://www.w3.org/1999/xhtml"
            elif (None in nsmap and
                  nsmap[None] != "http://www.w3.org/1999/xhtml"):
                logger.debug(f"{function_name}	{uri}	Replacing XML Namespace {nsmap[None]} to http://www.w3.org/1999/xhtml.")
                nsmap[None] = "http://www.w3.org/1999/xhtml"
            xhtml = ET.Element("html", attrib=data.attrib, nsmap=nsmap)
            for element in data.getchildren(): xhtml.append(element)
            xhtml = apply_namespace(xhtml, "http://www.w3.org/1999/xhtml")
            return xhtml
        except ET.ParseError as e:
            logger.error(f"{function_name}	{uri}	A parsing error has occurred.")
            logger.debug(f"{function_name}	{uri}	{e}")
        except Exception as e:
            logger.error(f"{function_name}	{uri}	An error has occurred while attempting to parse content.")
            logger.debug(f"{function_name}	{uri}	{e}")

def apply_namespace(data: ET._ElementTree, namespace: str):
    function_name = sys._getframe().f_code.co_name
    logger.debug(f"{function_name}	{namespace}	Start")
    for element in data.iter():
        if not element.tag.startswith("{"):
            element.tag = f"{{{namespace}}}{element.tag}"
    return data
