#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from slixfeed.utility.logger import UtilityLogger

logger = UtilityLogger(__name__)

import sys

class RetrieverFinger:

    async def data(uri: str):
