#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from slixfeed.configuration.profile import profile
from slixfeed.utility.logger import UtilityLogger
from slixmpp.jid import JID
import sys
import xml.sax.saxutils

logger = UtilityLogger(__name__)

"""

NOTE

See XEP-0367: Message Attaching

"""

class XmppMessage:

    def send(xmpp_instance, jid, message_body, chat_type="chat"):
        print(f"SEND MESSAGE: {jid}")
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        jid_from = xmpp_instance.boundjid.full if xmpp_instance.is_component else None
        xmpp_instance.send_message(mto=jid,
                                   mfrom=jid_from,
                                   mbody=message_body,
                                   mtype=chat_type)

    def send_headline(xmpp_instance, jid, message_subject,
                      message_body, chat_type="chat"):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        jid_from = xmpp_instance.boundjid.full if xmpp_instance.is_component else None
        xmpp_instance.send_message(mto=jid,
                                   mfrom=jid_from,
                                   # mtype="headline",
                                   msubject=message_subject,
                                   mbody=message_body,
                                   mtype=chat_type,
                                   mnick=profile.alias)

    def send_omemo(xmpp_instance, jid: JID, response_encrypted,
                   chat_type="chat"):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        # jid_from = xmpp_instance.boundjid.full if xmpp_instance.is_component else None
        # message = xmpp_instance.make_message(mto=jid, mfrom=jid_from, mtype=chat_type)
        # eme_ns = "eu.siacs.conversations.axolotl"
        # message["eme"]["namespace"] = eme_ns
        # message["eme"]["name"] = xmpp_instance["xep_0380"].mechanisms[eme_ns]
        # message["eme"] = {"name": xmpp_instance["xep_0380"].mechanisms[eme_ns]}
        # message["eme"] = {"namespace": eme_ns}
        # message.append(response_encrypted)
        for namespace, message in response_encrypted.items():
            message["eme"]["namespace"] = namespace
            message["eme"]["name"] = xmpp_instance["xep_0380"].mechanisms[namespace]
        message.send()

    def send_omemo_oob(xmpp_instance, jid: JID, url_encrypted, chat_type="chat",
                       aesgcm=False):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        jid_from = xmpp_instance.boundjid.full if xmpp_instance.is_component else None
        # if not aesgcm: url_encrypted = xml.sax.saxutils.escape(url_encrypted)
        message = xmpp_instance.make_message(mto=jid, mfrom=jid_from, mtype=chat_type)
        eme_ns = "eu.siacs.conversations.axolotl"
        # message["eme"]["namespace"] = eme_ns
        # message["eme"]["name"] = xmpp_instance["xep_0380"].mechanisms[eme_ns]
        message["eme"] = {"namespace": eme_ns}
        # message["eme"] = {"name": xmpp_instance["xep_0380"].mechanisms[eme_ns]}
        message["oob"]["url"] = url_encrypted
        message.append(url_encrypted)
        message.send()

    # FIXME Solve this function
    def send_omemo_reply(xmpp_instance, message, response_encrypted):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        eme_ns = "eu.siacs.conversations.axolotl"
        # message["eme"]["namespace"] = eme_ns
        # message["eme"]["name"] = xmpp_instance["xep_0380"].mechanisms[eme_ns]
        message["eme"] = {"namespace": eme_ns}
        # message["eme"] = {"name": xmpp_instance["xep_0380"].mechanisms[eme_ns]}
        message.append(response_encrypted)
        message.reply(message["body"]).send()

    # NOTE We might want to add more characters
    # def escape_to_xml(raw_string):
    # escape_map = {
    #     """ : "&quot;",
    #     """ : "&apos;"
    # }
    # return xml.sax.saxutils.escape(raw_string, escape_map)
    def send_oob(xmpp_instance, jid, url, chat_type="chat"):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        jid_from = xmpp_instance.boundjid.full if xmpp_instance.is_component else None
        url = xml.sax.saxutils.escape(url)
        # try:
        #html = (f"<body xmlns=\"http://www.w3.org/1999/xhtml\">"
        #        f"<a href=\"{url}\">{url}</a></body>")
        message = xmpp_instance.make_message(mto=jid,
                                             mfrom=jid_from,
                                             mbody=url,
                                             #mhtml=html,
                                             mtype=chat_type)
        message["oob"]["url"] = url
        message.send()
        # except:
        #     logging.error("ERROR!")
        #     logging.error(jid, url, chat_type, html)

    # FIXME Solve this function
    def send_oob_reply_message(message, url, response):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        reply = message.reply(response)
        reply["oob"]["url"] = url
        reply.send()

    # def send_reply(message, message_body):
    #     message.reply(message_body).send()

    def send_reply(message, response):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        message.reply(response).send()
