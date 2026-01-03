#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Catch IqError
  ERROR:slixmpp.basexmpp:internal-server-error: Database failure
  WARNING:slixmpp.basexmpp:You should catch IqError exceptions
"""

from slixfeed.utility.logger import UtilityLogger
from slixmpp.exceptions import IqTimeout, IqError
import sys

logger = UtilityLogger(__name__)

class XmppAvatar:

    async def set_photo(xmpp_instance, photo):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        try:
            await xmpp_instance.plugin["xep_0084"].publish_avatar(photo)
        except (IqTimeout, IqError, Exception) as e:
            logger.error(f"{function_name}		{str(e)}")
        try:
            await xmpp_instance.plugin["xep_0153"].set_avatar(avatar=photo)
        except (IqTimeout, IqError, Exception) as e:
            logger.error(f"{function_name}		{str(e)}")
