#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from slixfeed.utility.logger import UtilityLogger
from slixmpp.exceptions import IqError, IqTimeout
import sys

logger = UtilityLogger(__name__)

class XmppIQ:

    async def send(iq):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        try:
            result = await iq.send(timeout=15)
        except IqTimeout as e:
            logger.error(f"{function_name}		Error Timeout: {str(e)}")
            result = e
        except IqError as e:
            logger.error(f"{function_name}		Error XmppIQ: {str(e)}")
            result = e
        return result
