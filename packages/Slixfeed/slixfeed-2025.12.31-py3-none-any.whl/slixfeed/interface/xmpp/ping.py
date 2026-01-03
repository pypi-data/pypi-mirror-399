#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from slixfeed.utility.logger import UtilityLogger
from slixmpp.exceptions import IqError, IqTimeout
import sys

logger = UtilityLogger(__name__)

class XmppPing:

    async def send(xmpp_instance, jid_bare, jid_from=None):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        jid_from = jid_bare if xmpp_instance.is_component else None
        try:
            rtt = await xmpp_instance["xep_0199"].ping(
                jid_bare, ifrom=jid_from, timeout=10)
            logger.info(f"{function_name}	{jid_bare}	Ping")
            return rtt
        except (IqTimeout, IqError, Exception) as e:
            logger.warning(f"{function_name}	{jid_bare}	{str(e)}")
