#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

TODO

1) Send message to inviter that bot has joined to groupchat.

2) If groupchat requires captcha, send the consequent message.

3) If groupchat error is received, send that error message to inviter.

FIXME

1) Save name of groupchat instead of jid as name

"""
from asyncio import TimeoutError
from slixfeed.configuration.profile import profile
from slixfeed.utility.logger import UtilityLogger
from slixmpp.exceptions import IqError, IqTimeout, PresenceError
import sys

logger = UtilityLogger(__name__)

class XmppMuc:

    def get_own_jid(xmpp_instance, room):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{room}	Start")
        jid_full = xmpp_instance.plugin["xep_0045"].get_our_jid_in_room(room)
        return jid_full

    def get_jid_property(xmpp_instance, room, alias, jid_property):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{room}	Start")
        property = xmpp_instance.plugin["xep_0045"].get_jid_property(
            room, alias, jid_property)
        return property

    def get_self_alias(xmpp_instance, room):
        """Get self alias of a given group chat"""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{room}	Start")
        jid_full = xmpp_instance.plugin["xep_0045"].get_our_jid_in_room(room)
        alias = jid_full.split("/")[1]
        logger.debug(f"{function_name}	{room}	Finish")
        return alias

    async def enter(xmpp_instance, jid_bare, alias=None, password=None):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        jid_from = xmpp_instance.boundjid.full #if xmpp_instance.is_component else None
        try:
            logger.info(f"{function_name}	{jid_bare}	Joining to MUC group chat")
            await xmpp_instance.plugin["xep_0045"].join_muc_wait(
                jid_bare, profile.alias, presence_options = {"pfrom" : jid_from},
                password=password, maxchars=0, maxstanzas=0, seconds=0, since=0,
                timeout=30)
            result = "success"
        except IqError as e:
            logger.error(f"{function_name}	{jid_bare}	IQ error")
            logger.debug(f"{function_name}	{jid_bare}	{str(e)}")
            result = "error"
        except IqTimeout as e:
            logger.error(f"{function_name}	{jid_bare}	IQ timeout")
            logger.debug(f"{function_name}	{jid_bare}	{str(e)}")
            result = "timeout"
        except TimeoutError as e:
            logger.error(f"{function_name}	{jid_bare}	AsyncIO timeout")
            logger.debug(f"{function_name}	{jid_bare}	{str(e)}")
            result = "timeout"
        except PresenceError as e:
            logger.error(f"{function_name}	{jid_bare}	Presence error")
            logger.debug(f"{function_name}	{jid_bare}	{str(e)}")
            if (e.condition == "forbidden" and
                e.presence["error"]["code"] == "403"):
                logger.warning(f"{function_name}	{jid_bare}	{alias} is banned from group chat")
                result = "ban"
            elif e.condition == "conflict":
                message = e.presence["error"]["text"]
                logger.warning(f"{function_name}	{jid_bare}	{message}")
                result = "conflict"
            else:
                result = "error"
        except Exception as e:
            logger.error(f"{function_name}	{jid_bare}	Unknown error")
            logger.debug(f"{function_name}	{jid_bare}	{str(e)}")
            result = "error"
        return result

    def leave(xmpp_instance, jid_bare):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        jid_from = xmpp_instance.boundjid.full if xmpp_instance.is_component else None
        status_message = (f"This bot has left the group. {xmpp_instance.boundjid.bare}")
        xmpp_instance.plugin["xep_0045"].leave_muc(jid_bare, profile.alias,
                                                   status_message, jid_from)
