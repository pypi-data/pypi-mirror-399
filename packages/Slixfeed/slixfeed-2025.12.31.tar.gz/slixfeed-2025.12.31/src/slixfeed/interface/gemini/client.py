#!/usr/bin/python
# -*- coding: utf-8 -*-

import asyncio
from jetforce import GeminiServer, JetforceApplication, RateLimiter, Request, Response, Status
import os
from slixfeed.config import Cache, Config, Data
from slixfeed.configuration.singleton import configurations
from slixfeed.configuration.profile import profile
from slixfeed.interface.xmpp.actions import XmppActions
from slixfeed.parser.atom import ParserAtom
from slixfeed.parser.opml import ParserOpml
from slixfeed.utility.account import accounts
from slixfeed.utility.html import UtilityHtml
from slixfeed.utility.logger import UtilityLogger
from slixfeed.sqlite.general import SQLiteGeneral
from slixfeed.utility.subscription import UtilitySubscriptionTask
from slixfeed.utility.task import UtilityTask
import socket
import sys
#import uvicorn

logger = UtilityLogger(__name__)

general_rate_limiter = RateLimiter("100/m")
routes = JetforceApplication(rate_limiter=general_rate_limiter)
short_rate_limiter = RateLimiter("5/30s")
long_rate_limiter = RateLimiter("60/5m")

class GeminiClient:

    def __init__(self):
        asyncio.run(GeminiApplication.initiate())
        server = GeminiServer(routes, host="127.0.0.1", hostname="localhost")
        server.run()

        #asyncio.run(GeminiApplication.initiate())
        #asyncio.create_task(GeminiIpc.server())

        # Mount static graphic, script and stylesheet directories
        #app.mount("/css", StaticFiles(directory=directory_data_css), name="css")
        #app.mount("/data", StaticFiles(directory=directory_cache_json), name="data")
        #app.mount("/graphic", StaticFiles(directory=directory_data_graphic), name="graphic")
        #app.mount("/script", StaticFiles(directory=directory_data_script), name="script")
        #app.mount("/xsl", StaticFiles(directory=directory_data_xsl), name="xsl")

class GeminiProperties:

        directory_data = Data.get_directory()
        directory_data_gemini = os.path.join(directory_data, "gemini")
        directory_data_graphics = os.path.join(directory_data, "graphics")
        if not os.path.exists(directory_data_gemini): os.mkdir(directory_data_gemini)
        #directory_data_css = os.path.join(directory_data, "css")
        #directory_data_graphic = os.path.join(directory_data, "graphic")
        #directory_data_script = os.path.join(directory_data, "script")
        #directory_data_xsl = os.path.join(directory_data, "xsl")
        filename_atom = os.path.join(directory_data_gemini, "slixfeed.atom")
        #filename_favicon = os.path.join(directory_data_graphics, "image.ico")
        filename_gmi = os.path.join(directory_data_gemini, "slixfeed.gmi")
        filename_icon = os.path.join(directory_data_graphics, "image.svg")
        filename_opml = os.path.join(directory_data_gemini, "slixfeed.opml")

        directory_cache = Cache.get_directory()
        #directory_cache_json = os.path.join(directory_cache, "json")

gemini_properties = GeminiProperties()

class GeminiPages:

    @routes.route("/image.svg")
    def icon(request: Request):
        filename = gemini_properties.filename_icon
        data = open(filename, mode="br")
        result = data.read()
        response = Response(
            Status.SUCCESS,
            #"image/svg+xml",
            "application/octet-stream",
            result)
        return response

    @routes.route("", strict_trailing_slash=False)
    @short_rate_limiter.apply
    def entries_gmi(request: Request):
        filename = gemini_properties.filename_gmi
        data = open(filename, mode="r")
        result = data.read()
        response = Response(
            Status.SUCCESS,
            "text/gemini",
            result)
        return response

    @routes.route("/gmi/(?P<identifier>[-~dA-Za-z0-9]+)")
    def entries_gmi_ix(request: Request, identifier: str):
        filename = os.path.join(gemini_properties.directory_data_gemini,
                                f"{identifier}", "index.gmi")
        data = open(filename, mode="r")
        result = data.read()
        response = Response(
            Status.SUCCESS,
            "text/gemini",
            result)
        return response

    @routes.route("/gmi/(?P<identifier>[-~dA-Za-z0-9]+)/(?P<filename>[-~dA-Za-z0-9]+)")
    def entries_gmi_ix(request: Request, identifier: str, filename: str):
        filename = os.path.join(gemini_properties.directory_data_gemini,
                                f"{identifier}", f"{filename}")
        data = open(filename, mode="r")
        result = data.read()
        response = Response(
            Status.SUCCESS,
            "text/gemini",
            result)
        return response

    #@routes.route("/feed")
    #@routes.route("/rss")
    @routes.route("/atom")
    @short_rate_limiter.apply
    def entries_xml(request: Request):
        filename = gemini_properties.filename_atom
        data = open(filename, mode="r")
        result = data.read()
        response = Response(
            Status.SUCCESS,
            "application/atom+xml",
            result)
        return response

    @routes.route("/atom/(?P<identifier>[-~dA-Za-z0-9]+)")
    def entries_xml_ix(request: Request, identifier: str):
        filename = os.path.join(gemini_properties.directory_data_gemini,
                                f"{identifier}.atom")
        data = open(filename, mode="r")
        result = data.read()
        response = Response(
            Status.SUCCESS,
            "application/atom+xml",
            result)
        return response

    @routes.route("/opml")
    @long_rate_limiter.apply
    def subscriptions_xml(request: Request):
        filename = gemini_properties.filename_opml
        data = open(filename, mode="r")
        result = data.read()
        response = Response(
            Status.SUCCESS,
            "text/gemini",
            result)
        return response

    @routes.route("/links")
    @long_rate_limiter.apply
    def subscriptions_gmi(request: Request):
        pass

    @routes.route("/about")
    @short_rate_limiter.apply
    def about_gmi(request: Request):
        pass

class GeminiApplication:

    async def initiate() -> None:
        # TODO Start task scan (scan for updates)
        # TODO Start task template (create static templates, instead of creating them upon request)
        UtilitySubscriptionTask.restart_task("slixfeed")
        GeminiTask.restart_task("slixfeed")
        asyncio.create_task(GeminiIpc.server())

class GeminiPublish:

    async def content(account) -> None:
        config_account = accounts.retrieve(account)
        db_file = config_account.database
        # Generate OPML
        results_opml = SQLiteGeneral.get_feeds(db_file)
        opml_as_string = ParserOpml.document(results_opml)
        filename_opml = gemini_properties.filename_opml
        with open(filename_opml, "w") as fn:
            fn.write(opml_as_string)
        # Generate Atom
        #link = "/"
        atom = {}
        atom["items"] = []
        atom["icon"] = "image.svg"
        atom["title"] = "Slixfeed"
        atom["subtitle"] = "Slixfeed World Syndication Service"
        atom["language"] = "en"
        atom["links"] = []
        #results_atom = SQLiteGeneral.get_unread_entries(db_file, 5)
        results_atom = SQLiteGeneral.get_entries_recent(db_file, 15)
        for result in results_atom:
            ix, title_e, url, summary, feed_id, published, updated = result
            # TODO Enclosures
            enclosure = SQLiteGeneral.get_enclosure_by_entry_id(db_file, ix)
            if enclosure: enclosure = enclosure[0]
            f_title = SQLiteGeneral.get_feed_title(db_file, feed_id)
            f_title = f_title[0]
            #f_url = SQLiteGeneral.get_feed_url(db_file, feed_id)
            #f_url = f_url[0]
            f_identifier = SQLiteGeneral.get_feed_identifier(db_file, feed_id)
            atom_item = {}
            atom_item["title"] = title_e
            atom_item["links"] = SQLiteGeneral.get_links_by_entry_id(db_file, ix)
            atom_item["summary"] = summary
            atom_item["contents"] = SQLiteGeneral.get_contents_by_entry_id(db_file, ix)
            atom_item["published"] = published
            atom_item["updated"] = updated
            atom_item["authors"] = [("", "", f_title, f_identifier, "")]
            atom_item["categories"] = SQLiteGeneral.get_tags_by_entry_id(db_file, ix)
            atom_item["id"] = ""
            atom["items"].append(atom_item)
            await SQLiteGeneral.mark_as_read(db_file, ix)
        atom_as_string = ParserAtom.document(atom)
        filename_atom = gemini_properties.filename_atom
        with open(filename_atom, "w") as fn:
            fn.write(atom_as_string)
        # Generate Atom per subscription
        for ix in SQLiteGeneral.get_subscriptions_indices(db_file):
            feed_id = ix[0]
            #s_type = SQLiteGeneral.get_subscription_type(db_file, feed_id)
            #if s_type = "atom10": type = application/atom+xml
            #elif s_type = "rss20": type = application/rss+xml
            # NOTE Gemini, JSON, RDF, Twtxt.
            #link = SQLiteGeneral.get_subscription_uri(db_file, feed_id)
            #atom["links"].append({"type": type,
            #                      "rel": "self",
            #                      "href": link})
            # NOTE Or consider own.
            #link = "/" + SQLiteGeneral.get_feed_identifier(db_file, feed_id)
            #atom["links"].append({"type": "application/atom+xml",
            #                      "rel": "self",
            #                      "href": link})
            atom = {}
            atom["items"] = []
            atom["icon"] = SQLiteGeneral.get_subscription_icon(db_file, feed_id) or "image.svg"
            atom["title"] = SQLiteGeneral.get_subscription_title(db_file, feed_id)
            atom["subtitle"] = SQLiteGeneral.get_subscription_subtitle(db_file, feed_id)
            atom["language"] = SQLiteGeneral.get_subscription_locale_code(db_file, feed_id)
            atom["links"] = []
            for link in SQLiteGeneral.get_subscription_links(db_file, feed_id):
                atom["links"].append({"type" : link[3],
                                      "rel" : link[4],
                                      "href" : link[2]})
            results_atom = SQLiteGeneral.get_entries_of_subscription(db_file, feed_id)
            for result in results_atom:
                ix, title_e, url, summary, e_identifier, published, updated = result
                # TODO Enclosures
                enclosure = SQLiteGeneral.get_enclosure_by_entry_id(db_file, ix)
                if enclosure: enclosure = enclosure[0]
                atom_item = {}
                atom_item["title"] = title_e
                atom_item["links"] = SQLiteGeneral.get_links_by_entry_id(db_file, ix)
                atom_item["summary"] = summary
                atom_item["contents"] = SQLiteGeneral.get_contents_by_entry_id(db_file, ix)
                atom_item["published"] = published
                atom_item["updated"] = updated
                atom_item["authors"] = SQLiteGeneral.get_authors_by_entry_id(db_file, ix)
                atom_item["categories"] = SQLiteGeneral.get_tags_by_entry_id(db_file, ix)
                atom_item["id"] = e_identifier
                atom["items"].append(atom_item)
                await SQLiteGeneral.mark_as_read(db_file, ix)
            atom_as_string = ParserAtom.document(atom)
            f_identifier = SQLiteGeneral.get_feed_identifier(db_file, feed_id)
            filename_atom = os.path.join(gemini_properties.directory_data_gemini,
                                         f"{f_identifier}.atom")
            with open(filename_atom, "w") as fn:
                fn.write(atom_as_string)
        # Generate Gemini Feed
        gemini_feed = ""
        gemini_feed += "# Slixfeed\n\n"
        gemini_feed += "Slixfeed World Syndication Service\n\n"
        gemini_feed += "=> image.svg\n\n"
        #language = "en"
        #results = SQLiteGeneral.get_unread_entries(db_file, 5)
        results = SQLiteGeneral.get_entries_recent(db_file, 15)
        for result in results:
            # TODO Extracy summary_type and title_type
            ix, title_e, url, summary, feed_id, published, updated = result
            f_title = SQLiteGeneral.get_feed_title(db_file, feed_id)
            f_title = f_title[0]
            #f_url = SQLiteGeneral.get_feed_url(db_file, feed_id)
            #f_url = f_url[0]
            f_identifier = SQLiteGeneral.get_feed_identifier(db_file, feed_id)
            gemini_feed += f"# {title_e}\n\n"
            if summary:
                summary_cleared = UtilityHtml.remove_html_tags(summary)
                gemini_feed += f"## Summary\n{summary_cleared}\n\n"
            contents = SQLiteGeneral.get_contents_by_entry_id(db_file, ix)
            if contents:
                gemini_feed += f"## Contents\n\n"
                for content in contents:
                    if "html" in content[3]:
                        # TODO Extract links and add them as footnotes
                        content_cleared = UtilityHtml.remove_html_tags(content[2])
                        gemini_feed += f"{content_cleared}\n\n"
                    else:
                        gemini_feed += f"{content[2]}\n\n"
            links = SQLiteGeneral.get_links_by_entry_id(db_file, ix)
            if links:
                for link in links: gemini_feed += f"=> {link[2]}\n"
                gemini_feed += "\n"
            if published: gemini_feed += f"Published: {published}\n\n"
            if updated: gemini_feed += f"Updated: {updated}\n\n"
            gemini_feed += f"=> gmi/{f_identifier} {f_title}\n\n"
            gemini_feed += "\n"
            #atom_item["categories"] = SQLiteGeneral.get_tags_by_entry_id(db_file, ix)
            #atom_item["id"] = ""
            await SQLiteGeneral.mark_as_read(db_file, ix)
        filename_gmi = gemini_properties.filename_gmi
        with open(filename_gmi, "w") as fn:
            fn.write(gemini_feed)
        # Generate Gemini Feed per subscription
        for ix in SQLiteGeneral.get_subscriptions_indices(db_file):
            feed_id = ix[0]
            #s_type = SQLiteGeneral.get_subscription_type(db_file, feed_id)
            #if s_type = "atom10": type = application/atom+xml
            #elif s_type = "rss20": type = application/rss+xml
            # NOTE Gemini, JSON, RDF, Twtxt.
            #link = SQLiteGeneral.get_subscription_uri(db_file, feed_id)
            #atom["links"].append({"type": type,
            #                      "rel": "self",
            #                      "href": link})
            # NOTE Or consider own.
            #link = "/" + SQLiteGeneral.get_feed_identifier(db_file, feed_id)
            #atom["links"].append({"type": "application/atom+xml",
            #                      "rel": "self",
            #                      "href": link})
            gemini_feed = ""
            title = SQLiteGeneral.get_subscription_title(db_file, feed_id)
            gemini_feed += f"# {title}\n\n"
            subtitle = SQLiteGeneral.get_subscription_subtitle(db_file, feed_id)
            if subtitle: gemini_feed += f"{subtitle}\n\n"
            logo = SQLiteGeneral.get_subscription_logo(db_file, feed_id) or "image.svg"
            if logo: gemini_feed += f"=> {logo}\n\n"
            f_identifier = SQLiteGeneral.get_feed_identifier(db_file, feed_id)
            directory_gmi = os.path.join(gemini_properties.directory_data_gemini,
                                         f"{f_identifier}")
            if not os.path.exists(directory_gmi): os.mkdir(directory_gmi)
            #language = SQLiteGeneral.get_subscription_locale_code(db_file, feed_id)
            #links = []
            #for link in SQLiteGeneral.get_subscription_links(db_file, feed_id):
            #    links.append(link[2])
            results = SQLiteGeneral.get_entries_of_subscription(db_file, feed_id)
            for result in results:
                ix, title_e, url, summary, e_identifier, published, updated = result
                gemini_entry = ""
                gemini_entry += f"# {title_e}\n\n"
                if summary:
                    summary_cleared = UtilityHtml.remove_html_tags(summary)
                    gemini_entry += f"## Summary\n{summary_cleared}\n\n"
                contents = SQLiteGeneral.get_contents_by_entry_id(db_file, ix)
                if contents:
                    gemini_entry += f"## Contents\n\n"
                    for content in contents:
                        if "html" in content[3]:
                            # TODO Extract links and add them as footnotes
                            content_cleared = UtilityHtml.remove_html_tags(content[2])
                            gemini_entry += f"{content_cleared}\n\n"
                        else:
                            gemini_entry += f"{content[2]}\n\n"
                links = SQLiteGeneral.get_links_by_entry_id(db_file, ix)
                if links:
                    for link in links: gemini_entry += f"=> {link[2]}\n"
                    gemini_entry += "\n"
                if published: gemini_entry += f"Published: {published}\n\n"
                if updated: gemini_entry += f"Updated: {updated}\n\n"
                gemini_feed += gemini_entry
                f_title = SQLiteGeneral.get_feed_title(db_file, feed_id)
                f_title = f_title[0]
                gemini_entry += f"=> ../{f_identifier} {f_title}\n\n"
                gemini_entry += "\n"
                filename_gmi_e = os.path.join(directory_gmi, f"{e_identifier}.gmi")
                with open(filename_gmi_e, "w") as fn:
                    fn.write(gemini_entry)
                gemini_feed += f"=> {e_identifier}.gmi {f_title}\n\n"
                gemini_feed += "\n"

                #authors = SQLiteGeneral.get_authors_by_entry_id(db_file, ix)
                #categories = SQLiteGeneral.get_tags_by_entry_id(db_file, ix)

                await SQLiteGeneral.mark_as_read(db_file, ix)
            filename_gmi = os.path.join(directory_gmi, "index.gmi")
            with open(filename_gmi, "w") as fn:
                fn.write(gemini_feed)

class GeminiIpc:

    async def server():
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        filename_ipc_socket = os.path.join(gemini_properties.directory_data,
                                           "slixfeed.socket")
        # Setup socket
        if os.path.exists(filename_ipc_socket): os.remove(filename_ipc_socket)
        loop = asyncio.get_running_loop()
        ss = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        ss.setblocking(False)
        ss.bind(filename_ipc_socket)
        ss.listen(0)
        # conn = None
        # clients = []
        # clients = {}
        # Start listening loop
        while True:
            # Accept "request"
            conn, addr = await loop.sock_accept(ss)
            # # Terminate an old connection in favour of a new connection
            # if len(clients):
            #     for c in clients:
            #         print(c)
            #         c.close()
            #         del c
            # else:
            #     conn, addr = await loop.sock_accept(ss)
            #     clients.append(conn)
            #     print(clients)
            # Manage connections inside a dict
            # fd = conn.fileno()
            # clients[fd] = conn
            # datastream = await loop.sock_recv(conn, 1024)
            # if datastream.decode("utf-8") == "identifier":
            #     await loop.sock_sendall(conn, fd.encode("utf-8"))
            print("A connection from client has been detected. "
                  "Slixfeed is waiting for commands.")
            # print("There are {} clients connected to the IPC "
            #       "interface".format(len(clients)))
            # Process "request"
            while True:
                response = None
                # print("Awaiting for a command")
                # print(clients[fd])
                datastream = await loop.sock_recv(conn, 1024)
                if not datastream: break
                data = datastream.decode("utf-8")
                if "~" in data:
                    data_list = data.split("~")
                    account = data_list[0]
                    command = data_list[1]
                else:
                    command = data
                match command:
                    case _ if command.startswith("gemini:"):
                        information = XmppActions.fetch_gemini(command, account)
                        response = information["message"]
                    case "help":
                        response = XmppActions.print_help()
                    case "help all":
                        response = XmppActions.print_help_list()
                    case _ if (command.startswith("http") and
                               command.endswith(".opml")):
                        response = await XmppActions.import_opml(account, command)
                    case "info":
                        response = XmppActions.print_info_list()
                    case _ if command.startswith("info"):
                        entry = command[5:].lower()
                        response = XmppActions.print_info_specific(entry)
                    case _ if (command.startswith("http") or
                               command.startswith("feed:/") or
                               command.startswith("itpc:/") or
                               command.startswith("rss:/")):
                        information = await XmppActions.fetch_http(command, account)
                        response = information["message"]
                    case "exit":
                        conn.close()
                        break
                    case _:
                        response = XmppActions.print_unknown()
                # Send "response"
                await loop.sock_sendall(conn, response.encode("utf-8"))
        logger.debug(f"{function_name}		Finish")

class GeminiTask:

    async def looper(account):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{account}	Start")
        while True:
            await GeminiPublish.content(account)
            await asyncio.sleep(60 * 120)

    def restart_task(account):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{account}	Start")
        config_account = accounts.retrieve(account)
        UtilityTask.stop(config_account.tasks_manager, "publish")
        config_account.tasks_manager["publish"] = asyncio.create_task(
            GeminiTask.looper(account))
        logger.debug(f"{function_name}	{account}	Finish")
