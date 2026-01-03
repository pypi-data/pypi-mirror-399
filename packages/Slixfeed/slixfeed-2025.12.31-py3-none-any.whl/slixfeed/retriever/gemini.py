#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from slixfeed.utility.logger import UtilityLogger

logger = UtilityLogger(__name__)

#from Agunua import GeminiUri
import Agunua
import sys

class RetrieverGemini:

    def data(uri: str) -> dict:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{uri}	Start")
        data = Agunua.GeminiUri(uri, get_content=True, maxsize=5000000)
        if data.network_success and data.status_code == "20":
            result = {
                "charset": data.charset,
                "content": data.payload.strip(),
                "content_length": data.size,
                "content_type": data.mediatype,
                "error": False,
                "language": data.lang,
                "message": data.error,
                "original_url": uri,
                "status_code": data.status_code,
                "response_url": data.url}
        else:
            result = {
                "charset": None,
                "content": None,
                "content_length": None,
                "content_type": None,
                "error": True,
                "language": None,
                "message": data.error,
                "original_url": uri,
                "status_code": data.status_code,
                "response_url": None}
        return result
