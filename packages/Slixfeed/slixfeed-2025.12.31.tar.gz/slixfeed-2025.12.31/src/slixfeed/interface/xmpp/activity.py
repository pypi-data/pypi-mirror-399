#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from slixfeed.utility.logger import UtilityLogger
from slixmpp.exceptions import IqError, IqTimeout
#from slixmpp.jid import JID
from slixmpp.stanza.iq import Iq
import sys

logger = UtilityLogger(__name__)

class XmppActivity:

    async def publish(xmpp_instance, general: str, specific: str, text: str) -> Iq:
        """
        Publish activity.

        Parameters
        ----------
        general : str
            The general category of the activity.
        specific : str
            Specific activity being done as part of the general category.
        text : str
            Description or reason for the activity.

        Returns
        -------
        iq.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        try:
            iq = await xmpp_instance.plugin["xep_0108"].publish_activity(general,
                                                                         specific=specific,
                                                                         text=text)
            return iq
        except IqError as e:
            iq = e
            logger.error(f"{function_name}		IqError: {str(e)}")
        except IqTimeout as e:
            iq = e
            logger.error(f"{function_name}	{jid_bare}	IqTimeout: {str(e)}")
        except Exception as e:
            iq = e
            logger.error(f"{function_name}	{jid_bare}	Exception: {str(e)}")
        return iq
