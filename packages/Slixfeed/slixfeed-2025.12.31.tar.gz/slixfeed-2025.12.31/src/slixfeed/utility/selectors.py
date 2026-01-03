#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

from slixfeed.configuration.singleton import configurations
from slixfeed.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

class UtilitySelectors:

    def is_approved(account, hostname):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{account}	Start")
        #breakpoint()
        # Selectors: Unless allowed, deny.
        if (configurations.settings_selectors_allow and
            configurations.settings_selectors_deny and
            not UtilitySelectors.is_whitelisted(account, hostname)):
            approved = False
            logger.info(f"{function_name}	{account}	Policy: Unless allowed, deny.")
        # Selectors: Only deny.
        elif (configurations.settings_selectors_deny and
              not configurations.settings_selectors_allow):
            logger.info(f"{function_name}	{account}	Policy: Only deny.")
            if (account in configurations.selectors_deny["address"] or
                hostname in configurations.selectors_deny["hostname"] or
                UtilitySelectors.is_tld_blacklisted(hostname)):
                approved = False
            else:
                approved = True
        # Selectors: Only allow.
        elif (configurations.settings_selectors_allow and
              not configurations.settings_selectors_deny):
            logger.info(f"{function_name}	{account}	Policy: Only allow.")
            if (account in configurations.selectors_allow["address"] or
                hostname in configurations.selectors_allow["hostname"] or
                UtilitySelectors.is_tld_whitelisted(hostname)):
                approved = True
            else:
                approved = False
        else:
            approved = True
            logger.info(f"{function_name}	{account}	Policy: All are allowed.")
        logger.info(f"{function_name}	Approved: {approved} ({account} {hostname})")
        return approved

    def is_whitelisted(account, hostname):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{account}	Start")
        for tld in configurations.selectors_deny["tld"]:
            if hostname.endswith(tld):
                if UtilitySelectors.is_hostname_whitelisted(hostname):
                    return True
                elif UtilitySelectors.is_account_whitelisted(account):
                    return True
                else:
                    return False
        if hostname in configurations.selectors_deny["hostname"]:
            if UtilitySelectors.is_account_whitelisted(account):
                return True
            else:
                return False

    def is_blacklisted(account, hostname):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{account}	Start")
        if (account in configurations.selectors_deny["address"] or
            hostname in configurations.selectors_deny["hostname"]):
            return True
        for tld in configurations.selectors_deny["tld"]:
            if hostname.endswith(tld): return True

    def is_account_blacklisted(account):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{account}	Start")
        if account in configurations.selectors_deny["address"]:
            return True

    def is_hostname_blacklisted(hostname):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{hostname}	Start")
        if hostname in configurations.selectors_deny["hostname"]:
            return True

    def is_tld_blacklisted(hostname):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{hostname}	Start")
        for tld in configurations.selectors_deny["tld"]:
            if hostname.endswith(tld): return True

    def is_whitelisted(account, hostname):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{account}	Start")
        if (account in configurations.selectors_allow["address"] or
            hostname in configurations.selectors_allow["hostname"]):
            return True
        for tld in configurations.selectors_allow["tld"]:
            if hostname.endswith(tld): return True

    def is_account_whitelisted(account):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{account}	Start")
        if account in configurations.selectors_allow["address"]:
            return True

    def is_hostname_whitelisted(hostname):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{hostname}	Start")
        if hostname in configurations.selectors_allow["hostname"]:
            return True

    def is_tld_whitelisted(hostname):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{hostname}	Start")
        for tld in configurations.selectors_allow["tld"]:
            if hostname.endswith(tld): return True
