#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

        # self["xep_0050"].add_command(
        #     node="updates_enable",
        #     name="Enable/Disable News Updates",
        #     handler=option_enable_updates,
        #     )

    # Special interface
    # http://jabber.org/protocol/commands#actions

"""


import functools
from slixfeed.interface.xmpp.forms import XmppForms
from slixfeed.utility.logger import UtilityLogger
import sys

# time_now = datetime.now()
# time_now = time_now.strftime("%H:%M:%S")

# def print_time():
#     # return datetime.now().strftime("%H:%M:%S")
#     now = datetime.now()
#     current_time = now.strftime("%H:%M:%S")
#     return current_time

logger = UtilityLogger(__name__)

class XmppAdHoc:

    def add_command(xmpp_instance, node, name, handler):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        xmpp_instance["xep_0050"].add_command(
            node=node, name=name, handler=handler)
        logger.debug(f"{function_name}		Finish")

    def commands(xmpp_instance):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")

        commands = [
            ["subscription",
             "🪶️ Add a new subscription...",
              XmppForms.subscription_add],
            ["recent",
             "📰️ Browse subscriptions...",
              XmppForms.recent],
            ["subscriptions",
             "🎫️ Manage subscriptions...",
              XmppForms.subscriptions],
            ["promoted",
             "🔮️ Featured subscriptions...",
              XmppForms.promoted],
            ["discover",
             "🔍️ Discover subscriptions...",
              XmppForms.discover],
            ["import",
             "🗃️ Import subscriptions...",
              XmppForms.subscription_import],
            ["export",
             "🗄 Export subscriptions...",
              XmppForms.subscription_export],
            ["filters",
             "🛡️ Filters",
              XmppForms.filters],
#           ["activity",
#            "📝 Activity",
#             XmppForms.activity],
            ["settings",
             "📮️ Settings",
              XmppForms.settings],
            ["profile",
             "💼️ Profile",
              XmppForms.profile],
            ["manual",
             "📔️ Manual",
              XmppForms.manual],
            ["about",
             "📜️ About",
              XmppForms.about],
        ]

        for node, name, handler in commands:
            XmppAdHoc.add_command(
                xmpp_instance,
                node,
                name,
                functools.partial(handler, xmpp_instance))

        # XmppAdHoc.add_command(
        #     xmpp_instance,
        #     "about",
        #     "📜️ About",
        #     XmppForms.about)

        # xmpp_instance["xep_0050"].add_command(node="search",
        #                              name="Search",
        #                              handler=XmppForms.search)
