#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

import os
from slixfeed.configuration.singleton import configurations
from slixfeed.utility.logger import UtilityLogger
from slixfeed.utility.toml import UtilityToml
import sys

logger = UtilityLogger(__name__)

class Interface:
    def __init__(self):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")

        filename_accounts = os.path.join(
            configurations.directory_settings, "accounts.toml")
        accounts = UtilityToml.open_file(filename_accounts)

        match configurations.interface:
            case "activitypub":
                from slixfeed.interface.activitypub.client import ActivityPubClient
                credentials = accounts["activitypub"]
                address, password, hostname, port = Interface.get_credentials(credentials)
                self.instance = ActivityPubClient(address, password, hostname, port)
            case "bitmessage":
                from slixfeed.interface.bitmessage.client import BitMessageClient
                credentials = accounts["bitmessage"]
                address, password, hostname, port = Interface.get_credentials(credentials)
                self.instance = BitMessageClient(address, password, hostname, port)
            case "email":
                from slixfeed.interface.email.client import EmailClient
                credentials = accounts["email"]
                address, password, hostname, port = Interface.get_credentials(credentials)
                self.instance = EmailClient(address, password, hostname, port)
            case "gemini":
                from slixfeed.interface.gemini.client import GeminiClient
                credentials = accounts["gemini"]
                address, password, hostname, port = Interface.get_credentials(credentials)
                self.instance = GeminiClient(address, password, hostname, port)
            case "gopher":
                from slixfeed.interface.gopher.client import GopherClient
                credentials = accounts["gopher"]
                address, password, hostname, port = Interface.get_credentials(credentials)
                self.instance = GopherClient(address, password, hostname, port)
            case "http":
                from slixfeed.interface.http.client import HttpClient
                #credentials = accounts["http"]
                #hostname, port = get_credentials(credentials)
                #instance = HttpClient(hostname, port)
                self.instance = HttpClient()
            case "irc":
                from slixfeed.interface.irc.client import IrcClient
                credentials = accounts["irc"]
                address, password, hostname, port = Interface.get_credentials(credentials)
                self.instance = IrcClient(address, password, hostname, port)
            case "lxmf":
                from slixfeed.interface.lxmf.client import LxmfClient
                credentials = accounts["lxmf"]
                address, password, hostname, port = Interface.get_credentials(credentials)
                self.instance = LxmfClient(address, password, hostname, port)
            case "mqtt":
                from slixfeed.interface.mqtt.client import MqttClient
                credentials = accounts["mqtt"]
                address, password, hostname, port = Interface.get_credentials(credentials)
                self.instance = MqttClient(address, password, hostname, port)
            case "nostr":
                from slixfeed.interface.nostr.client import NostrClient
                credentials = accounts["nostr"]
                address, password, hostname, port = Interface.get_credentials(credentials)
                self.instance = NostrClient(address, password, hostname, port)
            case "simple":
                from slixfeed.interface.nostr.client import SimpleClient
                credentials = accounts["simple"]
                address, password, hostname, port = Interface.get_credentials(credentials)
                self.instance = SimpleClient(address, password, hostname, port)
            case "xmpp-client":
                from slixfeed.interface.xmpp.client import XmppClient
                credentials = accounts["xmpp"]["client"]
                address, password, hostname, port = Interface.get_credentials(credentials)
                self.instance = XmppClient(address, password, hostname, port)
            case "xmpp-component":
                from slixfeed.interface.xmpp.component import XmppComponent
                credentials = accounts["xmpp"]["component"]
                address, password, hostname, port = Interface.get_credentials(credentials)
                while not hostname:
                    hostname = input("Please enter a hostname: ")
                while not port:
                    port = input(f"Please enter a port number for hostname {hostname}: ")
                self.instance = XmppComponent(address, password, hostname, port)
            case "xmpp-pubsub":
                from slixfeed.interface.xmpp.pubsub import XmppPubSub
                credentials = accounts["xmpp"]["client"]
                address, password, hostname, port = Interface.get_credentials(credentials)
                self.instance = XmppPubSub(address, password, hostname, port)
            case _:
                from slixfeed.interface.xmpp.client import XmppClient
                credentials = accounts["xmpp"]["client"]
                address, password, hostname, port = Interface.get_credentials(credentials)
                self.instance = XmppClient(address, password, hostname, port)

    def get_credentials(credentials):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        # Try configuration file
        address = credentials["jid"] if "jid" in credentials else None
        password = credentials["password"] if "password" in credentials else None
        while not address:
            address = input("Please enter an account address: ")
        while not password:
            password = input(f"Please enter the password of account {address}: ")
        hostname = credentials["hostname"] if "hostname" in credentials else None
        port = credentials["port"] if "port" in credentials else None
        return address, password, hostname, port

interface = Interface()
