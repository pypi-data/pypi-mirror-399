#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

"""

TODO

1) Function scan at "for entry in entries"
   Suppress directly calling function "add_entry" (accept db_file)
   Pass a list of valid entries to a new function "add_entries"
   (accept db_file) which would call function "add_entry" (accept cur).
   * accelerate adding of large set of entries at once.
   * prevent (or mitigate halt of consequent actions).
   * reduce I/O.

2) Call sqlite function from function statistics.
   Returning a list of values does not seem to be a good practice.

3) Special statistics for operator:
   * Size of database(s);
   * Amount of JIDs subscribed;
   * Amount of feeds of all JIDs;
   * Amount of entries of all JIDs.

"""

from slixfeed.utility.logger import UtilityLogger
from slixfeed.utility.toml import UtilityToml
import sys

logger = UtilityLogger(__name__)

class UtilityDocumentation:

    def manual(filename, section=None, command=None):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        cmds = UtilityToml.open_file(filename)
        if section == "all":
            cmd_list = ""
            for cmd in cmds:
                for i in cmds[cmd]:
                    cmd_list += cmds[cmd][i] + "\n"
        elif command and section:
            try:
                cmd_list = cmds[section][command]
            except KeyError as e:
                logger.error(f"{function_name}		KeyError: {str(e)}")
                cmd_list = None
        elif section:
            try:
                cmd_list = []
                for cmd in cmds[section]:
                    cmd_list.extend([cmd])
            except KeyError as e:
                logger.error(f"{function_name}		KeyError: {str(e)}")
                cmd_list = None
        else:
            cmd_list = []
            for cmd in cmds:
                cmd_list.extend([cmd])
        return cmd_list
