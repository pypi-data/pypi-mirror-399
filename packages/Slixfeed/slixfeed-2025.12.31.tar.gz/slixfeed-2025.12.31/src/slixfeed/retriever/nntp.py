#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from slixfeed.utility.logger import UtilityLogger

logger = UtilityLogger(__name__)

import sys

class RetrieverNntp:

    async def data(uri: str):
