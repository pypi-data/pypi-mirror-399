#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import asyncio
import os
from slixfeed.configuration.singleton import configurations
#from slixfeed.utility.logger import UtilityLogger
from slixfeed.utility.subscription import UtilitySubscription
from slixfeed.utility.toml import UtilityToml
import sys

#logger = UtilityLogger(__name__)

filename_settings = os.path.join(
    configurations.directory_settings, "settings.toml")
settings = UtilityToml.open_file(filename_settings)
settings_default = settings["default"]
settings_configuration = settings["configuration"]
settings_network = settings["network"]

filename_accounts = os.path.join(
    configurations.directory_settings, "accounts.toml")
accounts = UtilityToml.open_file(filename_accounts)

filename_selectors = os.path.join(
    configurations.directory_settings, "selectors.toml")
selectors = UtilityToml.open_file(filename_selectors)

accounts_list = []
for account in accounts: accounts_list.append(account)

db_file_focuscript = configurations.database_focuscript
directory_focuscript = configurations.directory_focuscript

def start():

    if len(sys.argv) == 1: print(f"Please enter --help for directives.")

    # Main
    parser = ArgumentParser(description="Slixfeed setup")

    # Accounts
    parser_accounts = parser.add_argument_group(
        "accounts", "configuration of accounts utilized by service.")
    parser_accounts.add_argument(
        "--interface",
        choices=["pubsub", "xmpp"],
        #choices=accounts_list,
        dest="interface",
        type=str)
    parser_accounts.add_argument(
        "--address",
        dest="address",
        type=str)
    parser_accounts.add_argument(
        "--password",
        dest="password",
        type=str)
    parser_accounts.add_argument(
        "--hostname",
        dest="hostname",
        type=str)
    parser_accounts.add_argument(
        "--port",
        dest="port",
        type=int)

    # Network
    parser_network = parser.add_argument_group("network")
    parser_network.add_argument(
        "--ipc",
        choices=[0, 1],
        dest="ipc",
        help="inter-process communication.",
        type=int)
    parser_network.add_argument(
        "--proxy-http",
        dest="proxy_http",
        help="http proxy (ex. http://127.0.0.1:8118).",
        metavar="URI",
        type=str)
    parser_network.add_argument(
        "--proxy-socks",
        dest="proxy_socks",
        help="socks proxy (ex. socks://127.0.0.1:9050).",
        metavar="URI",
        type=str)
    parser_network.add_argument(
        "--user-agent",
        dest="user_agent",
        help="http user-agent (ex. Falkon).",
        type=str)
    parser_network.add_argument(
        "--policy",
        choices=["allow", "deny", "whitelist", "blacklist"],
        dest="policy",
        help="access policy. permissive, restrictive, or determined by a list.",
        type=str)

    # Subscribers
    parser_subscribers = parser.add_argument_group(
        "subscribers", "routine settings of subscribers.")
    parser_subscribers.add_argument(
        "--amount",
        choices=range(1, 7),
        dest="amount",
        help="amount of messages to send per update (1..7).",
        metavar="DIGIT",
        type=int)
    parser_subscribers.add_argument(
        "--archive",
        choices=range(0, 500),
        dest="archive",
        help="amount of items to archive (0..500).",
        metavar="DIGIT",
        type=int)
    parser_subscribers.add_argument(
        "--enclosure",
        choices=[0, 1],
        dest="enclosure",
        help="send enclosures (e.g. documents, multimedia).",
        type=int)
    parser_subscribers.add_argument(
        "--encryption",
        choices=[0, 1],
        dest="encryption",
        type=int)
#    parser_subscribers.add_argument(
#        "--encryption-type",
#        choices=["omemo", "otr", "openpgp"],
#        dest="encryption_type",
#        type=str)
    parser_subscribers.add_argument(
        "--filter",
        choices=[0, 1],
        dest="filter",
        help="filtering contents by keywords.",
        type=int)
    parser_subscribers.add_argument(
        "--intervel",
        choices=range(10, 2880),
        dest="intervel",
        help="interval between messages by minutes (10..2880).",
        metavar="DIGIT",
        type=int)
    parser_subscribers.add_argument(
        "--message",
        choices=[
            "{entry_id}",
            "{entry_summary}",
            "{entry_title}",
            "{feed_id}",
            "{feed_title}"],
        dest="message",
        help="design format of a message.",
        nargs="*",
        type=str)
    parser_subscribers.add_argument(
        "--old",
        choices=[0, 1],
        dest="old",
        help="do not mark newly added entries as read.",
        type=int)
    parser_subscribers.add_argument(
        "--random",
        choices=[0, 1],
        dest="random",
        help="random order of updates.",
        type=int)
    parser_subscribers.add_argument(
        "--summary",
        choices=range(10, 500),
        dest="summary",
        help="message length by characters (0..500).",
        metavar="DIGIT",
        type=int)

    # Selectors
    parser_selectors = parser.add_argument_group(
        "selectors", "selectors settings to restrict access to service.")
    parser_selectors.add_argument(
        "--list",
        choices=["whitelist", "blacklist"],
        dest="list",
        type=str)
    parser_selectors.add_argument(
        "--kind",
        choices=["address", "hostname", "tld"],
        dest="kind",
        type=str)
    parser_selectors.add_argument(
        "--add",
        dest="add",
        metavar="KIND",
        type=str)
    parser_selectors.add_argument(
        "--delete",
        dest="delete",
        metavar="KIND",
        type=str)

    # Filters
    #parser_filters = parser.add_argument_group(
    #    "Filters", "Content filtering based on keywords.")

    # Utilities
    parser_utilities = parser.add_argument_group("utilities")
    parser_utilities.add_argument(
        "--export",
        dest="export",
        choices=["gmi", "md", "opml"], # atom, toml, xbel
        help="export subscriptions to a specified filetype.",
        metavar="FILETYPE")
    parser_utilities.add_argument(
        "--import",
        dest="filename",
        help="import subscriptions from a filename.",
        metavar="FILENAME")
    #parser_utilities.add_argument(
    #    "--interface",
    #    dest="interface",
    #    help="an interface of a subscriber.",
    #    metavar="INTERFACE")
    parser_utilities.add_argument(
        "--subscriber",
        dest="subscriber",
        help="an address of a subscriber.",
        metavar="ADDRESS")

    args = parser.parse_args()

    # Missing interdependent arguments
    if args.add or args.delete:
        if not args.kind:
            print("Argument --kind is required.")
        if not args.kind:
            print("Argument --list is required.")
    if args.kind and not args.list:
        print("Argument --list is required.")
    if args.list and not args.kind:
        print("Argument --kind is required.")

    if not args.subscriber and (args.export or args.filename):
        print("Argument --subscriber is required.")

    # Accounts
    if args.address or args.hostname or args.password or args.port:
        account = accounts[args.interface]
        if args.address: account["address"] = args.address
        if args.hostname: account["hostname"] = args.hostname
        if args.password: account["password"] = args.password
        if args.port: account["port"] = args.port
        UtilityToml.save_file(filename_accounts, accounts)
    # Selectors
    elif args.kind:
        edited = False
        kind = args.kind
        value = args.delete or args.add
        if args.list == "blacklist":
            entry = "deny"
        #elif args.list == "whitelist":
        else:
            entry = "allow"
        if args.add:
            if value in selectors[entry][kind]:
                print("Value exists!")
            else:
                selectors[entry][kind].append(value)
                edited = True
        if args.delete:
            if value in selectors[entry][kind]:
                selectors[entry][kind].remove(value)
                edited = True
            else:
                print("Value does not exist!")
        else:
            for value in selectors[entry][kind]:
                print(value)
        if edited:
            UtilityToml.save_file(filename_selectors, selectors)
    # Subscriptions
    #elif args.interface and args.subscriber:
    elif args.subscriber:
        if args.filename:
            message = asyncio.run(UtilitySubscription.import_opml(
                args.subscriber, args.filename))
            print(message)
        elif args.export:
            filename, message = UtilitySubscription.export(
                args.subscriber, args.export)
            print(message)
            print(filename)
    # Settings
    else:
        if args.amount:
            settings_default["amount"] = args.amount
        if args.archive:
            settings_default["archive"] = args.archive
        if args.enclosure:
            settings_default["enclosure"] = args.enclosure
        if args.encryption:
            settings_default["encryption"] = args.encryption
        #if args.encryption_type:
        #    settings_default["encryption"]["type"] = args.encryption_type
        if args.filter:
            settings_default["filter"] = args.filter
        if args.intervel:
            settings_default["intervel"] = args.intervel
        if args.message:
            settings_default["message"] = args.message
        if args.old:
            settings_default["old"] = args.old
        if args.random:
            settings_default["random"] = args.random
        if args.summary:
            settings_default["summary"] = args.summary

        if args.proxy_http:
            settings_network["http_proxy"] = args.proxy_http
        if args.proxy_socks:
            settings_network["socks_proxy"] = args.proxy_socks
        if args.user_agent:
            settings_network["user_agent"] = args.user_agent

        if args.ipc:
            settings_configuration["ipc"] = args.ipc

        if args.interface:
            settings_configuration["interface"] = args.interface

        if args.policy:
            match args.poilcy:
                case "allow":
                    allow = deny = 0
                case "blacklist":
                    allow = 0
                    deny = 1
                case "deny":
                    allow = deny = 1
                case "whitelist":
                    allow = 1
                    deny = 0
            settings["selectors"]["allow"] = allow
            settings["selectors"]["deny"] = deny
        UtilityToml.save_file(filename_settings, settings)
