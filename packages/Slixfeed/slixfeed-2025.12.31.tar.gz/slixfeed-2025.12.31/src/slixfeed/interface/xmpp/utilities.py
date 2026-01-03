#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from slixfeed.configuration.profile import profile
from slixfeed.interface.xmpp.disco import XmppServiceDiscovery
from slixfeed.interface.xmpp.muc import XmppMuc
from slixfeed.interface.xmpp.ping import XmppPing
from slixfeed.utility.logger import UtilityLogger
from slixmpp import Iq
from slixmpp.exceptions import IqError, IqTimeout
import sys

logger = UtilityLogger(__name__)

class XmppUtilities:

    async def check_connectivity(xmpp_instance, jid_bare=None, hostname=None,
                                 port=None):
        """
        Check for ping and disconnect if no ping has been received.

        Parameters
        ----------
        jid : str, optional
            Jabber ID. The default is None.

        Returns
        -------
        None.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        if not jid_bare: jid_bare = xmpp_instance.boundjid.bare
        while True:
            rtt = None
            try:
                rtt = await XmppPing.send(xmpp_instance, jid_bare)
                logger.info(f"{function_name}	{jid_bare}	Success! RTT: {rtt}")
            except IqError as e:
                e_iq_error_condition = e.iq["error"]["condition"]
                logger.error(f"{function_name}	{jid_bare}	Error pinging: {e_iq_error_condition}")
            except IqTimeout:
                logger.warning(f"{function_name}	{jid_bare}	No response", )
            if not rtt:
                logger.warning(f"{function_name}	{jid_bare}	Disconnecting...")
                xmpp_instance.disconnect()
                await asyncio.sleep(30)
                logger.info(f"{function_name}		Reconnecting...")
                xmpp_instance.reconnect(wait=5.0)
            await asyncio.sleep(60 * 2)

    def get_xmpp_instance_alias(xmpp_instance, room):
        """Get xmpp_instance alias of a given group chat"""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{room}	Start")
        jid_full = XmppMuc.get_own_jid(xmpp_instance, room)
        alias = jid_full.split("/")[1]
        return alias

    async def get_chat_type(xmpp_instance, jid_bare):
        """
        Check chat (i.e. JID) type.
    
        If iqresult["disco_info"]["features"] contains XML namespace
        of "http://jabber.org/protocol/muc", then it is a "groupchat".
    
        Unless it has forward slash, which would indicate that it is
        a chat which is conducted through a groupchat.
        
        Otherwise, determine type "chat".
    
        Parameters
        ----------
        jid_bare : str
            Jabber ID.
    
        Returns
        -------
        result : str
            "chat" or "groupchat" or "error".
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        result = "chat"
        try:
            iq = await XmppServiceDiscovery.retrieve_information(xmpp_instance,
                                                                 jid_bare)
            account = conference = gateway = pep = pubsub = False
            if isinstance(iq, Iq):
                iq_disco_info = iq["disco_info"]
                features = iq_disco_info["features"]
                identities = iq_disco_info["identities"]
                # TODO elif <feature var="jabber:iq:gateway"/>
                # NOTE Is it needed? We do not interact with gateways or services
                for identity in identities:
                     category = identity[0]
                     name = identity[3]
                     type = identity[1]
                     # (category, type, None, name)
                     # ('pubsub', 'pep', None, None)
                     # ('account', 'registered', None, None)
                     # ('conference', 'text', None, 'Room Title')
                     # ('conference', 'irc', None, '#i2p on irc.libera.chat')
                     # ('gateway', 'irc', None, 'IRC server irc.biboumi.i2p over Biboumi')
                     #if type == "irc" or category == "gateway":
                     match category:
                         case "gateway":
                             gateway = True
                         case "account":
                             account = True
                         case "conference":
                             #if (type == "text" and
                             if (not "/" in jid_bare and
                                 "http://jabber.org/protocol/muc" in features):
                                 conference = True
                         case "pubsub":
                             pubsub = True
                             if type == "pep":
                                 pep = True
                if conference:
                    result = "groupchat"
                elif gateway:
                    result = "gateway"
                logger.info(f"{function_name}	{jid_bare}	Chat Type: {result}")
            elif isinstance(iq, IqError):
                e = iq.iq["error"]["text"]
                logger.warning(f"{function_name}	{jid_bare}	Chat type could not be determined due to an error. Details: {str(e)}")
            else:
                logger.warning(f"{function_name}	{jid_bare}	Chat type could not be determined.")
        except IqError as e:
            logger.warning(f"{function_name}	{jid_bare}	Chat type could not be determined due to an error. Details: {str(e)}")
        except IqTimeout as e:
            logger.warning(f"{function_name}	{jid_bare}	Chat type could not be determined due to a timeout error. Details: {str(e)}")
        # except BaseException as e:
        #     logger.error("BaseException", str(e))
        # finally:
        #     logger.info("Chat type is:", chat_type)
        return result

    def is_access(xmpp_instance, jid, chat_type):
        """Determine access privilege"""
        function_name = sys._getframe().f_code.co_name
        room = jid.bare
        logger.debug(f"{function_name}	{room}	Start")
        alias = jid.resource
        if chat_type == "groupchat":
            is_moderator = XmppUtilities.is_moderator(xmpp_instance, room, alias)
            access = True if is_moderator else False
            if access:
                logger.info(f"{function_name}	{room}	Access granted to groupchat moderator {alias}")
        else:
            logger.info(f"{function_name}	{room}	Access granted to chat")
            access = True
        return access

    def is_operator(jid_bare):
        """Check if given JID is an operator"""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        result = False
        for operator in profile.operators["xmpp"]:
            if jid_bare == operator["address"]:
                result = True
                # operator_name = operator["name"]
                break
        return result

    def is_admin(xmpp_instance, room, alias):
        """Check if given JID is an administrator"""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{room}	Start")
        affiliation = XmppMuc.get_jid_property(
            xmpp_instance, room, alias, "affiliation")
        result = True if affiliation == "admin" else False
        return result

    def is_owner(xmpp_instance, room, alias):
        """Check if given JID is an owner"""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{room}	Start")
        affiliation = XmppMuc.get_jid_property(
            xmpp_instance, room, alias, "affiliation")
        result = True if affiliation == "owner" else False
        return result

    def is_moderator(xmpp_instance, room, alias):
        """Check if given JID is a moderator"""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{room}	Start")
        role = XmppMuc.get_jid_property(xmpp_instance, room, alias, "role")
        result = True if role == "moderator" else False
        return result

    # NOTE Would this properly work when Alias and Local differ?
    def is_member(xmpp_instance, room, jid_full):
        """Check if given JID is a member"""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{room}	Start")
        logger.debug(f"{function_name}	{room}	{jid_full}")
        alias = jid_full[jid_full.index("/")+1:]
        affiliation = XmppMuc.get_jid_property(
            xmpp_instance, room, alias, "affiliation")
        result = True if affiliation == "member" else False
        return result
