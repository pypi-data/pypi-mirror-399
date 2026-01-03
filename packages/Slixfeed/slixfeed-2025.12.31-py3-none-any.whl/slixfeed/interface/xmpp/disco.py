#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from slixfeed.utility.logger import UtilityLogger
from slixmpp.exceptions import IqError, IqTimeout
import sys

logger = UtilityLogger(__name__)

class XmppServiceDiscovery:

    async def retrieve_items(xmpp_instance, jid: str):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid}	Start")
        try:
            iq = await xmpp_instance["xep_0030"].get_items(jid=jid)
        except IqTimeout as e:
            logger.error(f"{function_name}	{jid}	Error Timeout: {str(e)}")
            iq = e
        except IqError as e:
            logger.error(f"{function_name}	{jid}	Error XmppIQ: {str(e)}")
            iq = e
        return iq

    async def retrieve_information(xmpp_instance, jid: str):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid}	Start")
        try:
            iq = await xmpp_instance["xep_0030"].get_info(jid=jid)
        except IqTimeout as e:
            logger.error(f"{function_name}	{jid}	Error Timeout: {str(e)}")
            iq = e
        except IqError as e:
            logger.error(f"{function_name}	{jid}	Error XmppIQ: {str(e)}")
            iq = e
        return iq

    async def set_identity(xmpp_instance, category, itype, jid, lang, name):
        """
        Identify for Service Descovery.

        Parameters
        ----------
        category : str
            "client" or "service".

        Returns
        -------
        None.

        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        await xmpp_instance["xep_0030"].add_identity(category=category,
                                                     itype=itype,
                                                     jid=jid,
                                                     lang=lang,
                                                     name=name)
