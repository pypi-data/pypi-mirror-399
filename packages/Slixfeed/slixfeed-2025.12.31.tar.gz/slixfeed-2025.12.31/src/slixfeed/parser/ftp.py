#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from slixfeed.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

class ParserFtp:

    def ftp(content: str) -> dict:
