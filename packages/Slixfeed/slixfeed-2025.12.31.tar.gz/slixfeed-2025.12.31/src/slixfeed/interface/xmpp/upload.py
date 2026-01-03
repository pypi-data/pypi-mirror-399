#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Based on http_upload.py example from project slixmpp
https://codeberg.org/poezio/slixmpp/src/branch/master/examples/http_upload.py
"""

from pathlib import Path
from slixfeed.utility.logger import UtilityLogger
from slixmpp.exceptions import IqTimeout, IqError
from slixmpp.jid import JID
from slixmpp.plugins.xep_0363.http_upload import HTTPError
import sys
from typing import Optional

logger = UtilityLogger(__name__)
# import sys

class XmppUpload:

    async def start(xmpp_instance, jid, filename: Path, size: Optional[int] = None,
                    encrypted: bool = False, domain: Optional[JID] = None):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        logger.info(f"{function_name}		Uploading file {filename}...")
        url = None
        try:
            upload_file = xmpp_instance["xep_0363"].upload_file
            if encrypted and not xmpp_instance["xep_0454"]:
                print(
                    "The xep_0454 module is not available. "
                    "Ensure you have \"cryptography\" "
                    "from extras_require installed.",
                    file=sys.stderr,
                )
            elif encrypted:
                upload_file = xmpp_instance["xep_0454"].upload_file
            try:
                url = await upload_file(filename, size, domain, timeout=10,)
                logger.info(f"{function_name}		Upload successful!")
                logger.info(f"{function_name}		Sending file to {jid}")
            except HTTPError:
                logger.error(
                    f"{function_name}		It appears that this server does not "
                    "support HTTP File Upload.")
                # raise HTTPError(
                #     "This server doesn"t appear to support HTTP File Upload"
                #     )
        except IqError as e:
            logger.error(f"{function_name}		Could not send message")
            logger.error(f"{function_name}		{str(e)}")
        except IqTimeout as e:
            # raise TimeoutError("Could not send message in time")
            logger.error(f"{function_name}		Could not send message in time")
            logger.error(f"{function_name}		{str(e)}")
        return url
