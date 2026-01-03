#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

TODO

1) Look into self.set_jid in order to be able to join to groupchats
   https://slixmpp.readthedocs.io/en/latest/api/basexmpp.html#slixmpp.basexmpp.BaseXMPP.set_jid

2) czar
   https://slixmpp.readthedocs.io/en/latest/api/plugins/xep_0223.html
   https://slixmpp.readthedocs.io/en/latest/api/plugins/xep_0222.html#module-slixmpp.plugins.xep_0222

"""

import functools
from slixfeed.interface.xmpp.events import XmppEvents
from slixfeed.utility.logger import UtilityLogger
from slixmpp import ComponentXMPP
import sys

logger = UtilityLogger(__name__)

class XmppComponent(ComponentXMPP):
    """
    Slixfeed:
    News bot that sends updates from RSS feeds.
    """
    def __init__(self, jid, password, hostname, port):
        ComponentXMPP.__init__(self, jid, password, hostname, port)

        # Register plugins.
        xeps = [
            "xep_0004", # Data Forms
            "xep_0030", # Service Discovery
            "xep_0045", # Multi-User Chat
            "xep_0050", # Ad-Hoc Commands
            "xep_0054", # vcard-temp
            "xep_0060", # Publish-Subscribe
#            "xep_0065", # SOCKS5 Bytestreams
            "xep_0066", # Out of Band Data
            "xep_0071", # XHTML-IM
            "xep_0084", # User Avatar
            "xep_0085", # Chat State Notifications
            "xep_0107", # User Mood
            "xep_0108", # User Activity
            "xep_0115", # Entity Capabilities
            "xep_0122", # Data Forms Validation
#            "xep_0128", # Service Discovery Extensions
            "xep_0153", # vCard-Based Avatars
            "xep_0163", # Personal Eventing Protocol
            "xep_0172", # User Nickname
            "xep_0191", # Blocking Command
#            "xep_0199", # XMPP Ping
            "xep_0203", # Delayed Delivery
            "xep_0249", # Direct MUC Invitations
            "xep_0292", # vCard4 Over XMPP
            "xep_0363", # HTTP File Upload
            "xep_0369", # Mediated Information eXchange (MIX)
            "xep_0380", # Explicit Message Encryption
            "xep_0402", # PEP Native Bookmarks
#            "xep_0437", # Room Activity Indicators
            "xep_0444", # Message Reactions
        ]

        for xep in xeps: self.register_plugin(xep)
#        self.register_plugin("xep_0199", {"keepalive": True})

        try:
            import slixmpp_omemo
            self.omemo_present = True
        except Exception as e:
            function_name = sys._getframe().f_code.co_name
            logger.critical(
                f"{function_name}		OMEMO encryption could not be enabled.  Reason: {str(e)}")
            self.omemo_present = False

        if self.omemo_present:
            #from slixmpp.xmlstream.handler import CoroutineCallback
            #from slixmpp.xmlstream.matcher import MatchXPath
            #self.register_handler(CoroutineCallback(
            #    "Messages",
            #    MatchXPath(f"{{{self.default_ns}}}message"),
            #    self.on_message  # type: ignore[arg-type]
            #))

            from slixfeed.interface.xmpp.encryption import XEP_0384Impl
            from slixfeed.interface.xmpp.encryption import XmppOmemo
            import slixfeed.interface.xmpp.encryption as slixfeed_xmpp_encryption
            from slixmpp.plugins import register_plugin
            register_plugin(XEP_0384Impl)
            self.register_plugin("xep_0384", # OMEMO Encryption
                                 module=XEP_0384Impl)

        """
        if self.omemo_present:
            try:
                self.register_plugin(
                    "xep_0384",
                    {
                        "data_dir": Data.get_pathname_to_omemo_directory(),
                    },
                    module=slixmpp_omemo,) # OMEMO Encryption
            except (PluginCouldNotLoad,):
                logger.error("An error has occured when loading the OMEMO plugin.")
                sys.exit(1)
            try:
                self.register_plugin("xep_0454")
            except slixmpp.plugins.base.PluginNotFound:
                logger.error("Could not load xep_0454. Ensure you have "
                             "\"cryptography\" from extras_require installed.")
        """
        # proxy_enabled = config.get_value("accounts", "XMPP", "proxy_enabled")
        # if proxy_enabled == "1":
        #     values = config.get_value("accounts", "XMPP", [
        #         "proxy_host",
        #         "proxy_port",
        #         "proxy_username",
        #         "proxy_password"
        #         ])
        #     logger.info("Proxy is enabled: {}:{}".format(values[0], values[1]))
        #     self.use_proxy = True
        #     self.proxy_config = {
        #         "host": values[0],
        #         "port": values[1],
        #         "username": values[2],
        #         "password": values[3]
        #     }
        #     proxy = {"socks5": (values[0], values[1])}
        #     self.proxy = {"socks5": ("localhost", 9050)}

        # Register events.
        events = [
            ["connection_failed",
             XmppEvents.on_connection_failed],
            ["session_start",
             XmppEvents.on_session_start],
#            ["session_resumed",
#             XmppEvents.on_session_resumed],
            ["session_end",
             XmppEvents.on_session_end],
            ["got_offline",
             XmppEvents.cancel_all_tasks],
            ["changed_status",
             XmppEvents.on_changed_status],
            ["presence_unavailable",
             XmppEvents.on_presence_unavailable],
            ["presence_error",
             XmppEvents.cancel_all_tasks],
            ["disco_info",
             XmppEvents.on_disco_info],
            ["chatstate_active",
             XmppEvents.on_chatstate_active],
            ["chatstate_composing",
             XmppEvents.on_chatstate_composing],
            ["chatstate_gone",
             XmppEvents.calibrate_status_message],
            ["chatstate_inactive",
             XmppEvents.calibrate_status_message],
            ["chatstate_paused",
             XmppEvents.calibrate_status_message],
            ["message",
             XmppEvents.on_message],
            ["groupchat_invite", # XEP_0045
             XmppEvents.join_to_groupchat], # Movim
            ["groupchat_direct_invite", # XEP_0249
             XmppEvents.join_to_groupchat], # Gajim and Psi
#            ["reactions",
#             XmppEvents.on_reactions],
            ["presence_subscribe",
             XmppEvents.service_open],
            ["presence_subscribed",
             XmppEvents.service_open],
            ["presence_unsubscribe",
             XmppEvents.service_close],
            ["presence_unsubscribed",
             XmppEvents.service_close],
        ]

        for event, handler in events: self.add_event_handler(
            event, functools.partial(handler, self))

        # The message event is triggered whenever a message
        # stanza is received. Be aware that it includes
        # MUC messages and error messages.
#        self.add_event_handler("message",
#                               self.on_message)

#        asyncio.run(debug=True)

        # Check connectivity
        #loop = asyncio.get_event_loop()
        #self.task_ping_instance = loop.create_task(
        #        XmppUtilities.check_connectivity(self))

#        asyncio.get_event_loop().create_task(
#                XmppUtilities.check_connectivity(self))

#        loop.set_debug()

        # Connect to the XMPP server and start processing XMPP stanzas.
        self.connect(hostname, port)
        self.loop.run_forever()
        #asyncio.get_event_loop().run_forever()
