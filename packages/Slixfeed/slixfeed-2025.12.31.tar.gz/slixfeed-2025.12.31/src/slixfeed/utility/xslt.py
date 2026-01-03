#!/usr/bin/python
# -*- coding: utf-8 -*-

import lxml.etree as ET
from slixfeed.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

class UtilityXslt:

    def process(data: ET._Element, stylesheet: ET._Element) -> ET._XSLTResultTree:
        """Process an XML document by a specified XSLT stylesheet."""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        transform = ET.XSLT(stylesheet)
        try:
            return transform(data)
        except ET.XSLTApplyError as e:
            logger.error(f"{function_name}		XSLTApplyError: {str(e)}")
        except Exception as e:
            logger.error(f"{function_name}		{str(e)}")

        #newdom = transform(data)
        #xml_data_bytes = ET.tostring(newdom, pretty_print=True)
        #xml_data_str = xml_data_bytes.decode("utf-8")

        #xml_data_bytes = memoryview(newdom)
        #xml_data_str = str(memoryview(newdom), "UTF-8")
        #return xml_data_str
