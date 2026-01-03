#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

FIXME

base64 https://www.lilithsaintcrow.com/2024/02/love-anonymous/

"""

from email.utils import parseaddr
from slixfeed.utility.logger import UtilityLogger
import sys
from urllib.parse import urlsplit

logger = UtilityLogger(__name__)

class ParserUri:

    # TODO Improve check.
    def check_xmpp_uri(uri: str) -> bool:
        """Check validity of an XMPP URI."""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{uri}	Start")
        jid = urlsplit(uri).path
        return True if parseaddr(jid)[1] == jid else False

    def hostname(uri: str) -> str:
        """Remove useless subdomain from a given URI."""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{uri}	Start")
        hostname = urlsplit(uri).netloc
        return hostname[4:] if hostname.startswith("www.") else hostname

    def scheme(uri: str) -> str:
        """Return scheme of a given URI."""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{uri}	Start")
#       return urlparse(uri).scheme
        return urlsplit(uri).scheme
