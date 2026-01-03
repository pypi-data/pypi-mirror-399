#!/usr/bin/python
# -*- coding: utf-8 -*-

import lxml.etree as ET
from slixfeed.utility.focuscript import UtilityFocuscript
from slixfeed.utility.logger import UtilityLogger
from slixfeed.utility.parse import UtilityParse
import sys

logger = UtilityLogger(__name__)

class UtilityXml:

    def representation(content: str, uri: str) -> ET._ElementTree:
        """Pricess data, and create an XML representation of it."""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{uri}	Start")
        if (content.startswith("<!DOCTYPE HTML") or
            content.startswith("<!DOCTYPE html") or
            content.startswith("<html")):
            data = UtilityParse.html(content, uri)
        elif content.startswith("<?xml") or content.startswith("<"):
            data = UtilityParse.xml(content, uri)
        elif content.startswith("{"):
            json = UtilityParse.json(content, uri)
            data = UtilityFocuscript.convert_json_to_xml(json)
        elif uri.endswith(".gmi"):
            data = UtilityFocuscript.convert_gemtext_to_xml(content)
        elif uri.endswith(".txt"):
            data = UtilityFocuscript.convert_twtxt_to_xml(content)
        else:
            data = None
        return data
