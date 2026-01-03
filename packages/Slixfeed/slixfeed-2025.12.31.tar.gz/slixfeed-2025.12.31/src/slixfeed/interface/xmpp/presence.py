#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from slixfeed.configuration.profile import profile
from slixfeed.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

class XmppPresence:

    def send(xmpp_instance, jid_bare, presence_status, presence_show=""):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        xmpp_instance.send_presence(
            pto=jid_bare,
            pfrom=xmpp_instance.boundjid.bare,
            pshow=presence_show,
            pstatus=presence_status)
        logger.debug(f"{function_name}	{jid_bare}	show: {presence_show}; status: {presence_status}")
        logger.debug(f"{function_name}	{jid_bare}	Finish")

    def subscription(xmpp_instance, jid_bare, presence_type):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        xmpp_instance.send_presence_subscription(
            pto=jid_bare,
            pfrom=xmpp_instance.boundjid.bare,
            ptype=presence_type,
            pnick=profile.alias)
        logger.debug(f"{function_name}	{jid_bare}	type: {presence_type}")
        logger.debug(f"{function_name}	{jid_bare}	Finish")
