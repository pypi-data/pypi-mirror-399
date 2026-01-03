#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import os
import shutil
from slixfeed.config import Data
from slixfeed.configuration.singleton import configurations
from slixfeed.parser.focuscript import ParserFocuscript
from slixfeed.sqlite.focuscript import SQLiteFocuscript
from slixfeed.utility.logger import UtilityLogger
import socket
import sys
#import time

logger = UtilityLogger(__name__)

db_file_focuscript = configurations.database_focuscript
directory_focuscript = configurations.directory_focuscript

def start():
    if len(sys.argv) == 1:
        location = input("Enter plugin location: ")
    else:
        for argument in sys.argv[1:]:
            extension = argument.split(".").pop()
            match extension:
                case "focus":
                    metadata = ParserFocuscript.metadata(argument)
                    identifier = metadata["identifier"]
                    if not os.path.exists(db_file_focuscript):
                        SQLiteFocuscript.create_database(db_file_focuscript)
                    if SQLiteFocuscript.select_id_by_identifier(db_file_focuscript, identifier):
                        print(f"Focuscript {identifier} already exists.")
                    else:
                        asyncio.run(install_focuscript(argument))
                #case "sfd":
                case _ if "xsl" or "xslt":
                    print(
                        "Slixfeed supports Focuscript, a utility of XSLT.\n"
                        "Focuscripts are XML documents with embedded XSLT "
                        "stylesheets.\n"
                        "Please. Embed this XSLT stylesheet into a Focuscript, "
                        "and try again."
                       )
                case _:
                    print("Please enter a location of an Addon or a Focuscript.")

async def install_focuscript(focuscript):
    directory_data = Data.get_directory()
    filename = os.path.basename(focuscript)
    pathname = os.path.join(directory_focuscript, filename)
    shutil.copyfile(focuscript, pathname)
    focus = {}
    focus["metadata"] = ParserFocuscript.metadata(focuscript)
    identifier = focus["metadata"]["identifier"]
    version = focus["metadata"]["version"]
    version_id = SQLiteFocuscript.select_id_by_version(
        db_file_focuscript, version)
    if not version_id:
        version_id = await SQLiteFocuscript.insert_version_to_version(
            db_file_focuscript, version)
    focus["configuration"] = ParserFocuscript.configuration(focuscript)
    interval = focus["configuration"]["interval"]
    interval_id = SQLiteFocuscript.select_id_by_seconds(
        db_file_focuscript, interval)
    if not interval_id:
        interval_id = await SQLiteFocuscript.insert_seconds_to_interval(
            db_file_focuscript, interval)
    for condition in focus["configuration"]["condition"]:
        condition_id = SQLiteFocuscript.select_id_by_condition(
            db_file_focuscript, condition)
        if not condition_id:
            condition_id = await SQLiteFocuscript.insert_query_to_condition(
                db_file_focuscript, condition)
    uri_id = None # TODO
    focuscript_id = await SQLiteFocuscript.insert_properties_to_focuscript(
        db_file_focuscript, identifier, filename,
        condition_id=condition_id,
        interval_id=interval_id,
        uri_id=uri_id,
        version_id=version_id)
    for exclude in focus["configuration"]["exclude"]:
        protocol = exclude.split(":")[0]
        hostname = exclude.replace("//", "").split(":")[1].split("/")[0]
        pathname = "/".join(exclude.replace("//", "").split(":")[1].split("/")[1:])
        protocol_id = SQLiteFocuscript.select_id_by_exclude_protocol(
            db_file_focuscript, protocol)
        if not protocol_id:
            protocol_id = await SQLiteFocuscript.insert_protocol_to_exclude_protocol(
                db_file_focuscript, protocol)
        hostname_id = SQLiteFocuscript.select_id_by_exclude_hostname(
            db_file_focuscript, hostname)
        if not hostname_id:
            hostname_id = await SQLiteFocuscript.insert_hostname_to_exclude_hostname(
                db_file_focuscript, hostname)
        pathname_id = SQLiteFocuscript.select_id_by_exclude_pathname(
            db_file_focuscript, pathname)
        if not pathname_id:
            pathname_id = await SQLiteFocuscript.insert_pathname_to_exclude_pathname(
                db_file_focuscript, pathname)
        focus_exclude_id = await SQLiteFocuscript.insert_focus_id_and_exclude_id_to_aff_focus_exclude(
            db_file_focuscript, focuscript_id, hostname_id, pathname_id, protocol_id)
    for match in focus["configuration"]["match"]:
        protocol = match.split(":")[0]
        hostname = match.replace("//", "").split(":")[1].split("/")[0]
        pathname = "/".join(match.replace("//", "").split(":")[1].split("/")[1:])
        protocol_id = SQLiteFocuscript.select_id_by_match_protocol(
            db_file_focuscript, protocol)
        if not protocol_id:
            protocol_id = await SQLiteFocuscript.insert_protocol_to_match_protocol(
                db_file_focuscript, protocol)
        hostname_id = SQLiteFocuscript.select_id_by_match_hostname(
            db_file_focuscript, hostname)
        if not hostname_id:
            hostname_id = await SQLiteFocuscript.insert_hostname_to_match_hostname(
                db_file_focuscript, hostname)
        pathname_id = SQLiteFocuscript.select_id_by_match_pathname(
            db_file_focuscript, pathname)
        if not pathname_id:
            pathname_id = await SQLiteFocuscript.insert_pathname_to_match_pathname(
                db_file_focuscript, pathname)
        focus_match_id = await SQLiteFocuscript.insert_focus_id_and_match_id_to_aff_focus_match(
            db_file_focuscript, focuscript_id, hostname_id, pathname_id, protocol_id)
    stylesheet = ParserFocuscript.stylesheet(focuscript)
    for prefix in stylesheet.nsmap:
        if prefix:
            xmlns = stylesheet.nsmap[prefix]
            xmlns_id = SQLiteFocuscript.select_id_by_xmlns(db_file_focuscript, xmlns)
            if not xmlns_id:
                xmlns_id = await SQLiteFocuscript.insert_xmlns_to_namespace(
                    db_file_focuscript, xmlns)
            prefix_id = SQLiteFocuscript.select_id_by_prefix(db_file_focuscript, prefix)
            if not prefix_id:
                prefix_id = await SQLiteFocuscript.insert_prefix_to_prefix(
                    db_file_focuscript, prefix)
            focus_namespace_id = await SQLiteFocuscript.insert_focus_id_and_xmlns_id_and_prefix_id_to_aff_focus_namespace(
                db_file_focuscript, focuscript_id, xmlns_id, prefix_id)
        
    print(f"Focuscript \"{filename}\" has been installed.")
