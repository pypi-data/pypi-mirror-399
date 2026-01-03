#!/usr/bin/python
# -*- coding: utf-8 -*-

import asyncio
from aiohttp import web as HttpServer
from aiohttp.web import Application, FileResponse, HTTPFound, Request, Response, RouteTableDef
import os
from slixfeed.config import Cache, Config, Data
from slixfeed.configuration.singleton import configurations
from slixfeed.configuration.profile import profile
from slixfeed.interface.xmpp.actions import XmppActions
from slixfeed.parser.atom import ParserAtom
from slixfeed.parser.opml import ParserOpml
from slixfeed.utility.account import accounts
from slixfeed.utility.logger import UtilityLogger
from slixfeed.utility.toml import UtilityToml
from slixfeed.sqlite.general import SQLiteGeneral
from slixfeed.utility.subscription import UtilitySubscriptionTask
from slixfeed.utility.task import UtilityTask
import socket
import sys
#import uvicorn

logger = UtilityLogger(__name__)

routes = RouteTableDef()

class HttpClient:

    def __init__(self):
        #uvicorn.run(app, host="localhost", port=port)
        #uvicorn.run(app, host="localhost", port=8000)
        app = HttpServer.Application()
        app.on_startup.append(HttpApplication.initiate)
        app.add_routes(routes)
        app.router.add_get('/atom', HttpPages.atom, name='atom')
        app.router.add_get('/', HttpPages.entries, name='entries')
        app.router.add_get('/subscriptions', HttpPages.subscriptions, name='subscriptions')
        #asyncio.create_task(HttpServer.run_app(app, port=8080))
        HttpServer.run_app(app, port=8080)

        #asyncio.run(HttpApplication.initiate())
        #asyncio.create_task(HttpIpc.server())

        # Mount static graphic, script and stylesheet directories
        #app.mount("/css", StaticFiles(directory=directory_data_css), name="css")
        #app.mount("/data", StaticFiles(directory=directory_cache_json), name="data")
        #app.mount("/graphic", StaticFiles(directory=directory_data_graphic), name="graphic")
        #app.mount("/script", StaticFiles(directory=directory_data_script), name="script")
        #app.mount("/xsl", StaticFiles(directory=directory_data_xsl), name="xsl")

class HttpProperties:

        directory_data = Data.get_directory()
        directory_http = os.path.join(directory_data, "http")
        directory_graphics = os.path.join(directory_data, "graphics")
        if not os.path.exists(directory_http): os.mkdir(directory_http)
        directory_css = os.path.join(directory_data, "css")
        #directory_graphic = os.path.join(directory_data, "graphic")
        #directory_script = os.path.join(directory_data, "script")
        directory_xslt = os.path.join(directory_data, "xslt")
        filename_atom = os.path.join(directory_http, "slixfeed.atom")
        filename_atom_html = os.path.join(directory_http, "index.html")
        #filename_favicon = os.path.join(directory_graphics, "image.ico")
        filename_icon = os.path.join(directory_graphics, "image.svg")
        filename_opml = os.path.join(directory_http, "slixfeed.opml")
        filename_opml_html = os.path.join(directory_http, "collection.html")

        directory_cache = Cache.get_directory()
        #directory_cache_json = os.path.join(directory_cache, "json")

http_properties = HttpProperties()

class HttpPages:

    @routes.get("/opml")
    @routes.get("/links")
    async def redirect_to_atom(request: Request):
        location = request.app.router['subscriptions'].url_for()
        raise HTTPFound(location=location)

    @routes.get("/xml")
    @routes.get("/rss")
    @routes.get("/feed")
    async def redirect_to_atom(request: Request):
        location = request.app.router['atom'].url_for()
        raise HTTPFound(location=location)

    @routes.get("/favicon.ico")
    async def favicon(request: Request):
        #return FileResponse(http_properties.filename_favicon)
        pass

    @routes.get("/css/{filename}")
    async def css(request: Request):
        filename = request.match_info["filename"]
        pathname = os.path.join(http_properties.directory_css,
                                f"{filename}")
        data = open(pathname, mode="r")
        result = data.read()
        response = Response(
            text=result,
            content_type="text/css")
        return response

    @routes.get("/image.svg")
    async def icon(request: Request):
        return FileResponse(http_properties.filename_icon)

    @routes.get("/xslt/{filename}")
    async def xslt(request: Request):
        filename = request.match_info["filename"]
        pathname = os.path.join(http_properties.directory_xslt,
                                f"{filename}")
        data = open(pathname, mode="r")
        result = data.read()
        response = Response(
            text=result,
            # NOTE This should be text/xsl. The reason for application/xml
            #      is so that it be rendered in browsers of vendors that
            #      try to suppress the XSLT technology.
            content_type="application/xml")
        return response

    @routes.get("/")
    async def entries(request: Request):
        if ("atom" in request.rel_url.query or
            "rss" in request.rel_url.query or
            "xml" in request.rel_url.query):
            filename = http_properties.filename_atom
            data = open(filename, mode="r")
            result = data.read()
            response = Response(
                text=result,
                content_type="application/xml")
        else:
            filename = http_properties.filename_atom_html
            data = open(filename, mode="r")
            result = data.read()
            response = Response(
                text=result,
                content_type="text/html")
        return response

    @routes.get("/atom")
    async def atom(request: Request):
        filename = http_properties.filename_atom
        data = open(filename, mode="r")
        result = data.read()
        response = Response(
            text=result,
            content_type="application/xml")
        return response

    @routes.get("/{identifier}")
    async def entries_ix(request: Request):
        identifier = request.match_info["identifier"]
        if ("atom" in request.rel_url.query or
            "rss" in request.rel_url.query or
            "xml" in request.rel_url.query):
            filename = os.path.join(http_properties.directory_http,
                                    f"{identifier}.atom")
            data = open(filename, mode="r")
            result = data.read()
            response = Response(
                text=result,
                content_type="application/xml")
        else:
            filename = os.path.join(http_properties.directory_http,
                                    f"{identifier}.html")
            data = open(filename, mode="r")
            result = data.read()
            response = Response(
                text=result,
                content_type="text/html")
        return response

    @routes.get("/subscriptions")
    async def subscriptions(request: Request):
        if ("opml" in request.rel_url.query or
            "xml" in request.rel_url.query):
            filename = http_properties.filename_opml
            data = open(filename, mode="r")
            result = data.read()
            response = Response(
                text=result,
                content_type="application/xml")
        else:
            filename = http_properties.filename_opml_html
            data = open(filename, mode="r")
            result = data.read()
            response = Response(
                text=result,
                content_type="text/html")
        return response

class HttpApplication:

    async def initiate(app: Application) -> None:
        # TODO Start task scan (scan for updates)
        # TODO Start task template (create static templates, instead of creating them upon request)
        UtilitySubscriptionTask.restart_task("slixfeed")
        HttpTask.restart_task("slixfeed")
        asyncio.create_task(HttpIpc.server())

class HttpPublish:

    async def content(account) -> None:
        config_account = accounts.retrieve(account)
        db_file = config_account.database
        filename_xslt_atom = os.path.join(http_properties.directory_xslt,
                                          f"atom.xsl")
        filename_xslt_opml = os.path.join(http_properties.directory_xslt,
                                          f"opml.xsl")
        # Generate OPML
        results_opml = SQLiteGeneral.get_feeds(db_file)
        opml_as_str = ParserOpml.document(results_opml)
        filename_opml = http_properties.filename_opml
        with open(filename_opml, "w") as fn:
            fn.write(opml_as_str)
        # Generate HTML of OPML
        opml_html_as_str = ParserOpml.transform(filename_opml, filename_xslt_opml)
        filename_opml_html = http_properties.filename_opml_html
        with open(filename_opml_html, "w") as fn:
            fn.write(opml_html_as_str)
        # Generate Atom
        #link = "/"
        atom = {}
        atom["items"] = []
        atom["icon"] = "/image.svg"
        atom["title"] = "Slixfeed"
        atom["subtitle"] = "Slixfeed World Syndication Service"
        atom["language"] = "en"
        atom["links"] = []
        #results_atom = SQLiteGeneral.get_unread_entries(db_file, 5)
        results_atom = SQLiteGeneral.get_entries_recent(db_file, 15)
        for result in results_atom:
            ix, title_e, url, summary, feed_id, published, updated = result
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
        filename_atom = http_properties.filename_atom
        with open(filename_atom, "w") as fn:
            fn.write(atom_as_string)
        # Generate HTML of Atom
        atom_html_as_str = ParserAtom.transform(filename_atom, filename_xslt_atom)
        filename_atom_html = http_properties.filename_atom_html
        with open(filename_atom_html, "w") as fn:
            fn.write(atom_html_as_str)
        # Generate files per subscription
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
            atom["icon"] = SQLiteGeneral.get_subscription_icon(db_file, feed_id) or "/image.svg"
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
            f_identifier = SQLiteGeneral.get_feed_identifier(db_file, feed_id)
            # Generate Atom
            atom_as_str = ParserAtom.document(atom)
            filename_atom = os.path.join(http_properties.directory_http,
                                         f"{f_identifier}.atom")
            with open(filename_atom, "w") as fn:
                fn.write(atom_as_str)
            # Generate HTML of Atom
            atom_html_as_str = ParserAtom.transform(filename_atom, filename_xslt_atom)
            filename_html = os.path.join(http_properties.directory_http,
                                         f"{f_identifier}.html")
            with open(filename_html, "w") as fn:
                fn.write(atom_html_as_str)
        # Generate documents from TOML file.
        file_about = os.path.join(configurations.directory_data, "info", "about.toml")
        sections = UtilityToml.open_file(file_about)
        for section in sections:
            atom = {}
            atom["items"] = []
            atom["icon"] = "/image.svg"
            atom["title"] = sections[section]["title"]
            atom["subtitle"] = sections[section]["subtitle"]
            atom["language"] = "en"
            atom["links"] = []
            entries = sections[section]["entries"]
            for entry in entries:
                atom_item = {}
                atom_item["title"] = entry["title"]
                atom_item["links"] = entry["urls"] if "urls" in entry else []
                atom_item["summary"] = entry["summary"] if "summary" in entry else ""
                atom_item["contents"] = [["", "", entry["content"], "text/plain", ""]] if "content" in entry else []
                atom_item["published"] = ""
                atom_item["updated"] = ""
                atom_item["authors"] = [["","","Slixfeed", "https://git.xmpp-it.net/sch/Slixfeed", ""]]
                atom_item["categories"] = []
                atom_item["id"] = ""
                atom["items"].append(atom_item)
            f_identifier = section
            # Generate Atom
            atom_as_str = ParserAtom.document(atom)
            filename_atom = os.path.join(http_properties.directory_http,
                                         f"{f_identifier}.atom")
            with open(filename_atom, "w") as fn:
                fn.write(atom_as_str)
            # Generate HTML of Atom
            atom_html_as_str = ParserAtom.transform(filename_atom, filename_xslt_atom)
            filename_html = os.path.join(http_properties.directory_http,
                                         f"{f_identifier}.html")
            with open(filename_html, "w") as fn:
                fn.write(atom_html_as_str)

class HttpIpc:

    async def server():
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        filename_ipc_socket = os.path.join(http_properties.directory_data,
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

class HttpTask:

    async def looper(account):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{account}	Start")
        while True:
            await HttpPublish.content(account)
            await asyncio.sleep(60 * 120)

    def restart_task(account):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{account}	Start")
        config_account = accounts.retrieve(account)
        UtilityTask.stop(config_account.tasks_manager, "publish")
        config_account.tasks_manager["publish"] = asyncio.create_task(
            HttpTask.looper(account))
        logger.debug(f"{function_name}	{account}	Finish")
