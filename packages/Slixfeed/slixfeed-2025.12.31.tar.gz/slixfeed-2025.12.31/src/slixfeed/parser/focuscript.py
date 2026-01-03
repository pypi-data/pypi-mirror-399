#!/usr/bin/python
# -*- coding: utf-8 -*-

import lxml.etree as ET
from slixfeed.utility.logger import UtilityLogger
import sys
#import xml.etree.ElementTree as ET

logger = UtilityLogger(__name__)

xmlns = "{http://diggy.i2p/focus}"

class ParserFocuscript:

    def configuration(focusfile: str) -> dict:
        """Extract configuration elements from a Focuscript document."""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        data = ET.parse(focusfile)
        focus = {}
        configuration = data.find(xmlns + "configuration")
        base = configuration.find(xmlns + "base")
        if base is not None: focus["base"] = base.text
        for tag in ("condition", "exclude", "grant", "match"):
            focus[tag] = []
            for element in configuration.findall(xmlns + tag):
                focus[tag].append(element.text)
        focus["execute"] = []
        for element in configuration.findall(xmlns + "execute"):
            focus["execute"].append({
                "moment" : element.attrib["moment"],
                "name"   : element.attrib["name"]})
        interval = configuration.find(xmlns + "interval")
        if interval is not None:
            value = int(interval.text)
            unit = interval.attrib["unit"]
            match unit:
                case "day":
                    formula = 60*60*24
                case "hour":
                    formula = 60*60
                case "minute":
                    formula = 60
            focus["interval"] = value * formula
        return focus

    def metadata(focusfile: str) -> dict:
        """Extract metadata elements from a Focuscript document."""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        data = ET.parse(focusfile)
        focus = {}
        metadata = data.find(xmlns + "metadata")
        for tag in ("description", "icon", "identifier", "image", "license",
                    "logo", "mimetype", "rights", "subject", "title",
                    "version"):
            element = metadata.find(xmlns + tag)
            if element is not None: focus[tag] = element.text
        for tag in ("author", "contributor"):
            focus[tag] = []
            for element in metadata.findall(xmlns + tag):
                focus[tag].append(element.text)
        focus["links"] = []
        for link in metadata.findall(xmlns + "link"):
            attributes = {
                "href"  : link.attrib["href"] if "href" in link.attrib else "",
                "rel"   : link.attrib["rel"] if "rel" in link.attrib else "",
                "title" : link.attrib["title"] if "title" in link.attrib else "",
                "type"  : link.attrib["type"] if "type" in link.attrib else ""}
            focus["links"].append(attributes)
        return focus

    def namespace(focusfile: str) -> dict:
        """Extract namespace elements from a Focuscript document."""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        data = ET.parse(focusfile)
        namespace = data.findall(xmlns + "namespace")
        focus = {}
        for tag in ("append", "dismiss", "mode"):
            focus[tag] = []
            for element in namespace.findall(xmlns + tag):
                focus[tag].append(element)
        return focus

    def stylesheet(focusfile: str) -> ET._Element:
        """Extract stylesheet elements from a Focuscript document."""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        data = ET.parse(focusfile)
        fcs_elem = data.find(xmlns + "stylesheet")
        xsl_elem = fcs_elem.find("{http://www.w3.org/1999/XSL/Transform}transform")
        #return ET.ElementTree(xsl_elem) # ET._ElementTree
        return xsl_elem

    def xmlns(focusfile: str) -> ET._Element:
        """Extract stylesheet namespaces from a Focuscript document."""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        data = ET.parse(focusfile)
        fcs_elem = data.find(xmlns + "stylesheet")
        xsl_elem = fcs_elem.find("{http://www.w3.org/1999/XSL/Transform}transform")
        return xsl_elem.getroot().nsmap
