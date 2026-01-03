#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

TODO

2) Check also for HTML, not only feed.bozo.
    
7) See project /offpunk/offblocklist.py

NOTE

1) You might not want to utilize aiohttp, because you
   no more scan as many feeds as possible all at once
   due to CPU spike.
   Consider https://pythonhosted.org/feedparser/http-useragent.html

"""

import aiofiles
from aiohttp import ClientError, ClientSession, ClientTimeout
from asyncio import TimeoutError
from slixfeed.configuration.singleton import configurations
from slixfeed.utility.charset import UtilityCharset
from slixfeed.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

class RetrieverHttp:

    async def data(url: str, pathname=None, binary=False):
        """
        Download content of given URL.

        Parameters
        ----------
        url : str
            URL.
        pathname : list
            Pathname (including filename) to save content to.
        binary : bool
            Is the desired content of binary.

        Returns
        -------
        msg: list or str
            Document or error message.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{url}	Start")
        user_agent = configurations.settings_network["user_agent"] or "Slixfeed/0.1"
        headers = {
            "User-Agent": user_agent}
        proxy = configurations.settings_network["http_proxy"] or None
        timeout = ClientTimeout(total=10)
        async with ClientSession(headers=headers) as session:
        # async with ClientSession(trust_env=True) as session:
            try:
                async with session.get(
                    url,
                    proxy=proxy,
                    # proxy_auth=(proxy_username, proxy_password),
                    timeout=timeout) as response:
                    response_status = response.status
                    if response_status in (200, 201):
                        encoding = None
                        if binary:
                            f = await aiofiles.open(pathname, mode="wb")
                            await f.write(await response.read())
                            await f.close()
                            response_text = None
                        else:
                            try:
                                response_text = await response.text()
                            except Exception as e:
                                logger.error(f"{function_name}	{url}	{e}")
                                response_text = await response.content.read()
                            #if not isinstance(response_text, str):
                            if isinstance(response_text, bytes):
                                encoding = UtilityCharset.detect(
                                    response_text)["encoding"]
                                logger.info(f"{function_name}	{url}	{encoding}")
                                if encoding:
                                    response_text_decoded = UtilityCharset.decode(
                                        url, response_text, encoding, "utf-8")
                                if response_text_decoded:
                                    response_text = response_text_decoded
                        try:
                            result = {
                                # Perhaps "or encoding" should be removed.
                                "charset": response.charset or encoding,
                                "content": response_text.strip(),
                                "content_length": response.content_length,
                                "content_type": response.content_type,
                                "error": False,
                                "message": None,
                                "original_url": url,
                                "status_code": response_status,
                                "response_url": response.url}
                        except:
                            result = {
                                "error": True,
                                "message": "Could not get document.",
                                "original_url": url,
                                "status_code": response_status,
                                "response_url": response.url}
                    else:
                        result = {
                            "error": True,
                            "message": "HTTP Error:" + str(response_status),
                            "original_url": url,
                            "status_code": response_status,
                            "response_url": response.url}
            except ClientError as e:
                result = {
                    "error": True,
                    "message": "Error:" + str(e) if e else "ClientError",
                    "original_url": url,
                    "status_code": None}
            except TimeoutError as e:
                result = {
                    "error": True,
                    "message": "Timeout:" + str(e) if e else "TimeoutError",
                    "original_url": url,
                    "status_code": None}
            except Exception as e:
                logger.error(f"{function_name}	{url}	{str(e)}")
                result = {
                    "error": True,
                    "message": "Error:" + str(e) if e else "Error",
                    "original_url": url,
                    "status_code": None}
        return result

    async def headers(url):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{url}	Start")
        user_agent = configurations.settings_network["user_agent"] or "Slixfeed/0.1"
        headers = {
            "User-Agent": user_agent}
        proxy = configurations.settings_network["http_proxy"] or None
        timeout = ClientTimeout(total=10)
        async with ClientSession(headers=headers) as session:
            async with session.get(
                url,
                proxy=proxy,
                # proxy_auth=(proxy_username, proxy_password),
                timeout=timeout) as response:
                headers = response.headers
                return headers
                # print("Headers for URL:", url)
                # for header_name, header_value in headers.items():
                #     print(f"{header_name}: {header_value}")

    def response(url):
        """
        Download response headers.
    
        Parameters
        ----------
        url : str
            URL.
    
        Returns
        -------
        response: requests.models.Response
            HTTP Header Response.
    
        Result would contain these:
            response.encoding
            response.headers
            response.history
            response.reason
            response.status_code
            response.url
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{url}	Start")
        user_agent = configurations.settings_network["user_agent"] or "Slixfeed/0.1"
        headers = {
            "User-Agent": user_agent}
        try:
            # Do not use HEAD request because it appears that too many sites would
            # deny it.
            # response = requests.head(url, headers=headers, allow_redirects=True)
            response = requests.get(
                url,
                headers=headers,
                allow_redirects=True)
        except Exception as e:
            logger.error(f"{function_name}	{url}	{str(e)}")
            response = None
        return response
