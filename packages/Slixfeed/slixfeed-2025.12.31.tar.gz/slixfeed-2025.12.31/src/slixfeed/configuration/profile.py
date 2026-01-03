#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

import os
from pythonvCard4.vcard import Contact
from slixfeed.config import Cache, Config, Data, Settings
from slixfeed.utility.logger import UtilityLogger
from slixfeed.utility.toml import UtilityToml
import sys

logger = UtilityLogger(__name__)

class Profile:

    #def __init__(self, interface: str):
    def __init__(self):
        function_name = sys._getframe().f_code.co_name
        #logger.debug(f"{function_name}	{interface}	Start")
        logger.debug(f"{function_name}		Start")
        # A handler for operators.
        directory_config = Config.get_directory()
        filename_accounts = os.path.join(directory_config, "accounts.toml")
        self.data_accounts = UtilityToml.open_file(filename_accounts)
        #self.data_accounts_interface = self.data_accounts[interface]
        self.data_accounts_interface = self.data_accounts["xmpp"]
        filename_operators = os.path.join(directory_config, "operators.toml")
        self.operators = UtilityToml.open_file(filename_operators)
        directory_data = Data.get_directory()
        filename_profile = os.path.join(directory_data, "profile.vcf")
        vcf_data = open(filename_profile, "r", encoding="utf-8").read()
        self.vcard = Contact.from_vcard(vcf_data)
        self.alias = self.vcard.fn

profile = Profile()
