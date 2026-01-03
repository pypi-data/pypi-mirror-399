#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

import glob
import os
import random
from slixfeed.configuration.singleton import configurations
from slixfeed.utility.logger import UtilityLogger
from slixfeed.utility.toml import UtilityToml
import sys

logger = UtilityLogger(__name__)

class UtilityMiscellaneous:

    def pick_a_feed(lang=None):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	,Start")
        logger.debug(f"{function_name}	,Lang: {lang}")
        filename_feeds = os.path.join(configurations.directory_data, "info", "feeds.toml")
        urls = UtilityToml.open_file(filename_feeds)
        url = random.choice(urls["feeds"])
        return url

    def get_photo(config_dir):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	,Start")
        filename = glob.glob(config_dir + "/image.*")
        if not filename and os.path.isdir("/usr/share/slixfeed/"):
            # filename = "/usr/share/slixfeed/image.svg"
            filename = glob.glob("/usr/share/slixfeed/image.*")
        if not filename:
            config_dir = os.path.dirname(__file__)
            config_dir = config_dir.split("/")
            config_dir.pop()
            config_dir = "/".join(config_dir)
            filename = glob.glob(config_dir + "/assets/image.*")
        if len(filename):
            filename = filename[0]
            image_file = os.path.join(config_dir, filename)
            with open(image_file, "rb") as photo_file:
                photo = photo_file.read()
                return photo
