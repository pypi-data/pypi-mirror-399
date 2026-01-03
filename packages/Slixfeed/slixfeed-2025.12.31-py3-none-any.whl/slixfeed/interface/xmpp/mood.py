#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from slixfeed.utility.logger import UtilityLogger
from slixmpp.exceptions import IqError, IqTimeout
#from slixmpp.jid import JID
from slixmpp.stanza.iq import Iq
import sys

logger = UtilityLogger(__name__)

class XmppMood:

    async def publish(xmpp_instance, value: str, text="") -> Iq:
        """
        Publish activity.

        Parameters
        ----------
        value : str
            The name of the mood.
        text : str
            Description or reason for the mood.

        Returns
        -------
        iq.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        try:
            iq = await xmpp_instance.plugin["xep_0107"].publish_mood(value=value,
                                                                     text=text)
            return iq
        except IqError as e:
            iq = e
            logger.error(f"{function_name}		IqError: {str(e)}")
        except IqTimeout as e:
            iq = e
            logger.error(f"{function_name}		IqTimeout: {str(e)}")
        except Exception as e:
            iq = e
            logger.error(f"{function_name}		Exception: {str(e)}")
        return iq
