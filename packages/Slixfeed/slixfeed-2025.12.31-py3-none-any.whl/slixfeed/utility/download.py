#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

import chardet
import os
from slixfeed.utility.logger import UtilityLogger
from slixfeed.parser.uri import ParserUri
from slixfeed.retriever.gemini import RetrieverGemini
from slixfeed.retriever.http import RetrieverHttp
import sys

logger = UtilityLogger(__name__)

class UtilityDownload:

    async def uri(uri: str) -> dict:
        """Identify protocol to download from."""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{uri}	Start")
        if uri.startswith("/"): uri = "file://" + uri
        scheme = ParserUri.scheme(uri)
        match scheme:
            case "acct":
                result = {"charset"     : None,
                          "error"       : True,
                          "message"     : "ActivityPub is not yet supported.",
                          "status_code" : None}
            case "file":
                pathname = uri[7:]
                if os.path.exists(pathname):
                    content = open(pathname, "rb").read()
                    charset = chardet.detect(content)["encoding"]
                    result = {"charset"     : charset,
                              "content"     : content,
                              "error"       : False,
                              "status_code" : None}
                else:
                    result = {"charset"     : None,
                              "error"       : True,
                              "message"     : "Location does not exist.",
                              "status_code" : None}
            case "finger":
                result = RetrieverFinger.data(uri)
            case _ if scheme in ("ftp", "ftps"):
                result = {"charset"     : None,
                          "error"       : True,
                          "message"     : "FTP is not yet supported.",
                          "status_code" : None}
            case "gemini":
                result = RetrieverGemini.data(uri)
            case "gopher":
                result = {"charset"     : None,
                          "error"       : True,
                          "message"     : "Gopher is not yet supported.",
                          "status_code" : None}
            case _ if scheme in ("http", "https"):
                # Consider utilizing RetrieverHttp.data_response
                result = await RetrieverHttp.data(uri)
            case "nntp":
                result = {"charset"     : None,
                          "error"       : True,
                          "message"     : "NNTP is not yet supported.",
                          "status_code" : None}
            case "xmpp":
                result = await RetrieverXmpp.data(uri)
            case _:
                result = {"charset"     : None,
                          "error"       : True,
                          "message"     : "Unknown protocol.",
                          "status_code" : None}
        return result
