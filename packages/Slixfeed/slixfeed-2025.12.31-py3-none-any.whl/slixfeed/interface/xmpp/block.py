#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from slixfeed.utility.logger import UtilityLogger
from slixmpp.exceptions import IqError, IqTimeout
#from slixmpp.jid import JID
from slixmpp.stanza.iq import Iq
import sys

logger = UtilityLogger(__name__)

class XmppBlock:

    async def get_blocked(xmpp_instance) -> Iq:
        """
        List blocked Jabber IDs.

        Parameters
        ----------
        None.

        Returns
        -------
        iq.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        try:
            iq = await xmpp_instance.plugin["xep_0191"].get_blocked()
            logger.info(f"{function_name}		Retrieving blocked JID list")
            return iq
        except IqError as e:
            logger.error(f"{function_name}		IqError: {str(e)}")
        except IqTimeout as e:
            logger.error(f"{function_name}		IqTimeout: {str(e)}")
        except Exception as e:
            logger.error(f"{function_name}		Exception: {str(e)}")

    async def block(xmpp_instance, jid_bare: str) -> Iq:
        """
        Add a Jabber ID to list.

        Parameters
        ----------
        jid_bare : str
            A representation of a Jabber ID.

        Returns
        -------
        iq.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        try:
            iq = await xmpp_instance.plugin["xep_0191"].block(jid_bare)
            logger.info(f"{function_name}	{jid_bare}	Blocking JID")
            return iq
        except IqError as e:
            iq = e
            logger.error(f"{function_name}	{jid_bare}	IqError: {str(e)}")
        except IqTimeout as e:
            iq = e
            logger.error(f"{function_name}	{jid_bare}	IqTimeout: {str(e)}")
        except Exception as e:
            iq = e
            logger.error(f"{function_name}	{jid_bare}	Exception: {str(e)}")
        return iq

    async def unblock(xmpp_instance, jid_bare: str) -> Iq:
        """
        Remove a Jabber ID from list.

        Parameters
        ----------
        jid_bare : str
            A representation of a Jabber ID.

        Returns
        -------
        iq.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        try:
            iq = await xmpp_instance.plugin["xep_0191"].unblock(jid_bare)
            logger.info(f"{function_name}	{jid_bare}	Unblocking JID")
            return iq
        except IqError as e:
            iq = e
            logger.error(f"{function_name}	{jid_bare}	IqError: {str(e)}")
        except IqTimeout as e:
            iq = e
            logger.error(f"{function_name}	{jid_bare}	IqTimeout: {str(e)}")
        except Exception as e:
            iq = e
            logger.error(f"{function_name}	{jid_bare}	Exception: {str(e)}")
        return iq
