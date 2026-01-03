#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# NOTE elektito/ih2torrent

from slixfeed.utility.logger import UtilityLogger

logger = UtilityLogger(__name__)

try:
    from magnet2torrent import Magnet2Torrent, FailedToFetchException
except:
    logger.info("Package magnet2torrent was not found. BitTorrent is disabled.")

import sys

class RetrieverBitTorrent:

    async def data(uri: str):
        m2t = Magnet2Torrent(uri)
        try:
            filename, torrent_data = await m2t.retrieve_torrent()
        except FailedToFetchException:
            logger.debug("Failed")
