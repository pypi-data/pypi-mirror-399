#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

TODO

1) remove_subscription (clean_roster)
   Remove presence from contacts that do not share presence.

"""

from slixfeed.utility.logger import UtilityLogger
from slixmpp.exceptions import IqError, IqTimeout
from slixmpp.jid import JID
from slixmpp.stanza.iq import Iq
import sys

logger = UtilityLogger(__name__)

class XmppRoster:

    async def add_contact(xmpp_instance, jid_bare: str):
        """
        Add a contact to roster.

        Parameters
        ----------
        jid_bare : str
            A representation of a Jabber ID, or JID.

        Returns
        -------
        None.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        xmpp_instance.update_roster(jid_bare, subscription="both")

    # NOTE Perhaps return eith Iq or Exception
    async def remove_contact(xmpp_instance, jid: JID) -> Iq:
        """
        Remove a contact from roster.

        Parameters
        ----------
        jid : JID
            A representation of a Jabber ID, or JID.

        Returns
        -------
        None.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        try:
            iq = await xmpp_instance.del_roster_item(jid)
            return iq
        except IqError as e:
            iq = e
            logger.error(f"{function_name}	{jid.bare}	IqError: {str(e)}")
        except IqTimeout as e:
            iq = e
            logger.error(f"{function_name}	{jid.bare}	IqTimeout: {str(e)}")
        except Exception as e:
            iq = e
            logger.error(f"{function_name}	{jid.bare}	Exception: {str(e)}")
        #return iq
        #xmpp_instance.update_roster(jid.bare, subscription="remove")
