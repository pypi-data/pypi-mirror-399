#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Catch IqError
  ERROR:slixmpp.basexmpp:internal-server-error: Database failure
  WARNING:slixmpp.basexmpp:You should catch IqError exceptions
"""

from slixfeed.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

class XmppVCard:

    async def set_vcard(xmpp_instance, profile) -> None:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        vcard = xmpp_instance.plugin["xep_0054"].make_vcard()
        vcard["FN"] = profile.fn
        vcard["BDAY"] = profile.bday.strftime("%d %B %Y")
        vcard["NICKNAME"] = profile.nickname
        vcard["NOTE"] = profile.note
        vcard["URL"] = profile.url[0] if profile.url else ""
        await xmpp_instance.plugin["xep_0054"].publish_vcard(vcard)
        iq = await xmpp_instance.plugin["xep_0292"].publish_vcard(
           birthday=profile.bday,
#           email=None,
#           country=None,
            full_name=profile.fn,
#           given=None,
#           impp=None,
#           locality=None,
            nickname=profile.nickname,
            note=profile.note,
#           phone=None,
#           surname=None,
            url=profile.url[0] if profile.url else "")
