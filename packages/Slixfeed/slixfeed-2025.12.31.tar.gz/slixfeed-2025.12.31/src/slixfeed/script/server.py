#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

TODO

2) Machine Learning for scrapping Title, Link, Summary and Timstamp;
   Scrape element </article> (example: Liferea)
   http://intertwingly.net/blog/
   https://www.brandenburg.de/

3) Set MUC subject
   Feeds which entries are to be set as groupchat subject.
   Perhaps not, as it would require to check every feed for this setting.
   Maybe a separate bot;

13) Tip Of The Day.  Did you know...

14) Brand: News Broker, Newsman, Newsdealer, Laura Harbinger

16) Search messages of government regulated publishers, and promote other sources.
    Dear reader, we couldn"t get news from XYZ as they don"t provide RSS feeds.
    However, you might want to get news from (1) (2) and (3) instead!

17) The operator account will be given reports from the bot about its
    activities every X minutes.
    When a suspicious activity is detected, it will be reported immediately.

"""

# from eliot import start_action, to_file
# # to_file(open("slixfeed.log", "w"))
# # with start_action(action_type="set_date()", jid=jid):
# # with start_action(action_type="message()", msg=msg):

from argparse import ArgumentParser
import asyncio
import os
from slixfeed.configuration.singleton import configurations
from slixfeed.service.ipc import ServiceIpc
from slixfeed.utility.logger import UtilityLogger
from slixfeed.utility.toml import UtilityToml
from slixfeed.version import __version__
# import socket
# import socks
import sys

def start():

    function_name = sys._getframe().f_code.co_name

    filename_settings = os.path.join(configurations.directory_settings,
                                     "settings.toml")
    settings = UtilityToml.open_file(filename_settings)
    network_settings = settings["network"]

    # Configure account

    #print("User agent:", network_settings["user_agent"] or "Slixfeed/0.1")
    #if network_settings["http_proxy"]:
    #    print("HTTP Proxy:", network_settings["http_proxy"])

    # values = config.get_value("accounts", "XMPP Proxy",
    #                           ["socks5_host", "socks5_port"])
    # if values[0] and values[1]:
    #     host = values[0]
    #     port = values[1]
    #     s = socks.socksocket()
    #     s.set_proxy(socks.SOCKS5, host, port)
    #     # socks.set_default_proxy(socks.SOCKS5, host, port)
    #     # socket.socket = socks.socksocket

    #parser = ArgumentParser(description=Slixfeed.__doc__)
    parser = ArgumentParser(description="Slixfeed OSTN News Service")

    # Setup the command line arguments.
    parser.add_argument("-v", "--version",
                        action="version",
                        help="Print version",
                        version=__version__)
    parser.add_argument("--no-log", "--nolog",
                        action="store_true",
                        dest="nolog",
                        help="Do not create a log file")

    # Output verbosity options.
    parser.add_argument("-d", "--debug",
                        action="store_const",
                        const="debug",
                        default="info",
                        dest="loglevel",
                        help="set logging to DEBUG")
    parser.add_argument("-q", "--quiet",
                        action="store_const",
                        const="error",
                        default="info",
                        dest="loglevel",
                        help="set logging to ERROR")
    parser.add_argument("-w", "--warning",
                        action="store_const",
                        const="warn",
                        default="info",
                        dest="loglevel",
                        help="set logging to WARNING")

    parser.add_argument("--ipc",
                        action="store_true",
                        dest="ipc",
                        help="inter-process communication.")

    args = parser.parse_args()

    # Setup logging.
    #logging.basicConfig(level=args.loglevel,
    #                    format="%(levelname)-8s %(message)s")

    filename_log = os.path.join(
        configurations.directory_cache,
        "slixfeed_log.tsv")
    filename_log_old = os.path.join(
        configurations.directory_cache,
        "slixfeed_log.tsv.old")
    if os.path.exists(filename_log): os.rename(filename_log, filename_log_old)
    loglevel = args.loglevel
    logger = UtilityLogger("slixfeed")
    if not args.nolog:
        logger.set_filename(filename_log)
        with open(filename_log, "a") as file:
            file.write("Time	Level	Module	Function	Identifier	Message\n")
    logger.set_level(loglevel)
    # # logging.basicConfig(format="[%(levelname)s] %(message)s")
    # logger = logging.getLogger()
    # logdbg = logger.debug
    # logerr = logger.error
    # lognfo = logger.info
    # logwrn = logger.warning

    filename_accounts = os.path.join(
        configurations.directory_settings, "accounts.toml")
    accounts = UtilityToml.open_file(filename_accounts)

    db_file_focuscript = configurations.database_focuscript
    if not os.path.exists(db_file_focuscript):
        from slixfeed.sqlite.focuscript import SQLiteFocuscript
        SQLiteFocuscript.create_database(db_file_focuscript)

    if configurations.settings["configuration"]["ipc"]:
        #asyncio.run(ServiceIpc.server())
        loop = asyncio.get_event_loop()
        loop.create_task(ServiceIpc.server())
        message_ipc = "POSIX sockets: IPC server initialized."
        logger.info(f"{function_name}		{message_ipc}")

    match configurations.interface:
        case "activitypub":
            from slixfeed.interface.activitypub.client import ActivityPubClient
            credentials = accounts["activitypub"]
            address, password, hostname, port = get_credentials(credentials)
            interface_instance = ActivityPubClient(address, password, hostname, port)
        case "bitmessage":
            from slixfeed.interface.bitmessage.client import BitMessageClient
            credentials = accounts["bitmessage"]
            address, password, hostname, port = get_credentials(credentials)
            interface_instance = BitMessageClient(address, password, hostname, port)
        case "email":
            from slixfeed.interface.email.client import EmailClient
            credentials = accounts["email"]
            address, password, hostname, port = get_credentials(credentials)
            #interface_instance = EmailClient(address, password, hostname, port)
            #interface_instance = EmailClient()
            from slixfeed.interface.email.client import cli
            interface_instance = cli.start()
        case "gemini":
            from slixfeed.interface.gemini.client import GeminiClient
            #credentials = accounts["gemini"]
            #address, password, hostname, port = get_credentials(credentials)
            interface_instance = GeminiClient()
        case "gopher":
            from slixfeed.interface.gopher.client import GopherClient
            #credentials = accounts["gopher"]
            #address, password, hostname, port = get_credentials(credentials)
            interface_instance = GopherClient()
        case "http":
            from slixfeed.interface.http.client import HttpClient
            #credentials = accounts["http"]
            #hostname, port = get_credentials(credentials)
            #interface_instance = HttpClient(hostname, port)
            interface_instance = HttpClient()
        case "irc":
            from slixfeed.interface.irc.client import IrcClient
            credentials = accounts["irc"]
            address, password, hostname, port = get_credentials(credentials)
            interface_instance = IrcClient(address, password, hostname, port)
        case "lxmf":
            from slixfeed.interface.lxmf.client import LxmfClient
            credentials = accounts["lxmf"]
            address, password, hostname, port = get_credentials(credentials)
            interface_instance = LxmfClient(address, password, hostname, port)
        case "mqtt":
            from slixfeed.interface.mqtt.client import MqttClient
            credentials = accounts["mqtt"]
            address, password, hostname, port = get_credentials(credentials)
            interface_instance = MqttClient(address, password, hostname, port)
        case "nostr":
            from slixfeed.interface.nostr.client import NostrClient
            credentials = accounts["nostr"]
            address, password, hostname, port = get_credentials(credentials)
            interface_instance = NostrClient(address, password, hostname, port)
        case "simple":
            from slixfeed.interface.nostr.client import SimpleClient
            credentials = accounts["simple"]
            address, password, hostname, port = get_credentials(credentials)
            interface_instance = SimpleClient(address, password, hostname, port)
        case "xmpp":
            from slixfeed.interface.xmpp.client import XmppClient
            credentials = accounts["xmpp"]
            address, password, hostname, port = get_credentials(credentials)
            interface_instance = XmppClient(address, password, hostname, port)
        case "component":
            from slixfeed.interface.xmpp.component import XmppComponent
            credentials = accounts["component"]
            address, password, hostname, port = get_credentials(credentials)
            while not hostname:
                hostname = input("Please enter a hostname: ")
            while not port:
                port = input(f"Please enter a port number for hostname {hostname}: ")
            interface_instance = XmppComponent(address, password, hostname, port)
        case "pubsub":
            from slixfeed.interface.xmpp.pubsub import XmppPubSub
            credentials = accounts["pubsub"]
            address, password, hostname, port = get_credentials(credentials)
            interface_instance = XmppPubSub(address, password, hostname, port)
        case _:
            from slixfeed.interface.xmpp.client import XmppClient
            credentials = accounts["xmpp"]
            address, password, hostname, port = get_credentials(credentials)
            interface_instance = XmppClient(address, password, hostname, port)

def get_credentials(credentials):
    # Try configuration file
    address = credentials["address"] if "address" in credentials else None
    password = credentials["password"] if "password" in credentials else None
    if not address:
        print("Please. Configure an address of service account.")
        sys.exit(0)
    if not password:
        print(f"Please. Configure a password of account {address}.")
        sys.exit(0)
    hostname = credentials["hostname"] if "hostname" in credentials else None
    port = credentials["port"] if "port" in credentials else None
    return address, password, hostname, port
