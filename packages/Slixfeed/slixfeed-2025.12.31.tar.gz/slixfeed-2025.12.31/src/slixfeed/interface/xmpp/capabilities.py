#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from slixfeed.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

class XmppEntityCapabilities:

    async def update_capabilities(xmpp_instance, jid_full=None) -> None:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name}	{jid_full}	Start')
        await xmpp_instance['xep_0115'].update_caps(jid=jid_full)
