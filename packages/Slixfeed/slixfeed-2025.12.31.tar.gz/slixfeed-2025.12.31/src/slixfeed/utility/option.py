#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from slixfeed.utility.account import accounts
from slixfeed.utility.logger import UtilityLogger
from slixfeed.sqlite.general import SQLiteGeneral
import sys

logger = UtilityLogger(__name__)

    # for task in main_task:
    #     task.cancel()

    # Deprecated in favour of event "presence_available"
    # if not main_task:
    #     await select_file()

class UtilityOption:

    # FIXME
    async def restore_default(jid_bare: str, key=None):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        if key == "all":
            #del config_account.settings
            #await SQLiteGeneral.delete_settings(db_file)
            message = "Routine settings have been restored."
        else:
            #config_account.settings[key] = None
            #await SQLiteGeneral.delete_setting(db_file, key)
            message = f"Setting {key} has been set to routine value."
        return message

    async def clear_filter(jid_bare, key):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        await SQLiteGeneral.delete_filter(db_file, key)
        message = f"Filter {key} has been purged."
        return message

    async def set_status(jid_bare, key, value):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        status_key = "status_" + key
        await SQLiteGeneral.update_setting_value(db_file, status_key,
                                                 value)
        config_account.settings[key] = value
        state = "enabled" if value else "disabled"
        message = f"Updates are {state} for status \"{key}\"."
        return message

    def get_amount(jid_bare):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        key = "amount"
        config_account = accounts.retrieve(jid_bare)
        result = config_account.settings[key]
        message = str(result)
        return message

    def get_archive(jid_bare):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        key = "archive"
        config_account = accounts.retrieve(jid_bare)
        result = config_account.settings[key]
        message = str(result)
        return message

    def get_interval(jid_bare):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        key = "interval"
        config_account = accounts.retrieve(jid_bare)
        result = config_account.settings[key]
        message = str(result)
        return message

    def get_length(jid_bare):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        key = "length"
        config_account = accounts.retrieve(jid_bare)
        result = config_account.settings[key]
        result = str(result)
        return result

    async def set_amount(jid_bare, value):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        try:
            key = "amount"
            val_new = int(value)
            if val_new > 7:
                message = "Value may not be greater than 7."
            else:
                config_account = accounts.retrieve(jid_bare)
                val_old = config_account.settings[key]
                db_file = config_account.database
                await SQLiteGeneral.update_setting_value(db_file, key, val_new)
                config_account.settings[key] = val_new
                message = f"Next update will contain {val_new} news items (was: {val_old})."
        except:
            message = "Enter a numeric value only."
        return message

    async def set_archive(jid_bare, val):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        try:
            val_new = int(val)
            if val_new > 500:
                message = "Value may not be greater than 500."
            else:
                key = "archive"
                config_account = accounts.retrieve(jid_bare)
                val_old = config_account.settings[key]
                db_file = config_account.database
                await SQLiteGeneral.update_setting_value(db_file, key, val_new)
                config_account.settings[key] = val_new
                message = (f"Maximum archived items has been set to {val_new} "
                           f"(was: {val_old}).")
        except:
            message = "Enter a numeric value only."
        return message

    async def set_filter_allow(jid_bare, val, axis):
        """

        Parameters
        ----------
        db_file : str
            Database filename.
        val : str
            Keyword (word or phrase).
        axis : boolean
            True for + (plus) and False for - (minus).

        Returns
        -------
        None.

        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        keywords = SQLiteGeneral.get_filter_value(db_file, "allow")
        if keywords: keywords = str(keywords)
        if axis:
            val = config.add_to_list(val, keywords)
        else:
            val = config.remove_from_list(val, keywords)
        if SQLiteGeneral.is_filter_key(db_file, "allow"):
            await SQLiteGeneral.update_filter_value(db_file, ["allow", val])
        else:
            await SQLiteGeneral.set_filter_value(db_file, ["allow", val])

    async def set_filter_deny(jid_bare, val, axis):
        """

        Parameters
        ----------
        key : str
            deny.
        val : str
            keyword (word or phrase).
        axis : boolean
            True for + (plus) and False for - (minus).

        Returns
        -------
        None.

        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        keywords = SQLiteGeneral.get_filter_value(db_file, "deny")
        if keywords: keywords = str(keywords)
        if axis:
            val = config.add_to_list(val, keywords)
        else:
            val = config.remove_from_list(val, keywords)
        if SQLiteGeneral.is_filter_key(db_file, "deny"):
            await SQLiteGeneral.update_filter_value(db_file, ["deny", val])
        else:
            await SQLiteGeneral.set_filter_value(db_file, ["deny", val])

    async def set_interval(jid_bare, val):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        try:
            key = "interval"
            val_new = int(val)
            config_account = accounts.retrieve(jid_bare)
            val_old = config_account.settings[key]
            db_file = config_account.database
            await SQLiteGeneral.update_setting_value(db_file, key, val_new)
            config_account.settings[key] = val_new
            message = (f"Updates will be sent every {val_new} minutes "
                       f"(was: {val_old}).")
        except Exception as e:
            logger.error(str(e))
            message = "Enter a numeric value only."
        return message

    async def set_length(jid_bare, val):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        try:
            key = "length"
            val_new = int(val)
            config_account = accounts.retrieve(jid_bare)
            val_old = config_account.settings[key]
            db_file = config_account.database
            await SQLiteGeneral.update_setting_value(db_file, key, val_new)
            config_account.settings[key] = val_new
            if not val_new: # i.e. val_new == 0
                # TODO Add action to disable limit
                message = ("Summary length limit is disabled "
                           f"(was: {val_old}).")
            else:
                message = ("Summary maximum length is set to "
                           f"{val_new} characters (was: {val_old}).")
        except:
            message = "Enter a numeric value only."
        return message

    async def set_media_off(jid_bare):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        key = "media"
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        await SQLiteGeneral.update_setting_value(db_file, key, 0)
        config_account.settings[key] = 0
        message = "Media is disabled."
        return message

    async def set_media_on(jid_bare):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        key = "media"
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        await SQLiteGeneral.update_setting_value(db_file, key, 1)
        config_account.settings[key] = 1
        message = "Media is enabled."
        return message

    async def set_old_off(jid_bare):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        key = "old"
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        await SQLiteGeneral.update_setting_value(db_file, key, 0)
        config_account.settings[key] = 0
        message = "Only new items of newly added subscriptions be delivered."
        return message

    async def set_old_on(jid_bare):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        key = "old"
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        await SQLiteGeneral.update_setting_value(db_file, key, 1)
        config_account.settings[key] = 1
        message = "All items of newly added subscriptions be delivered."
        return message

    async def set_omemo_off(jid_bare):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        key = "omemo"
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        await SQLiteGeneral.update_setting_value(db_file, key, 0)
        config_account.settings[key] = 0
        message = "OMEMO is disabled."
        return message

    async def set_omemo_on(jid_bare):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        key = "omemo"
        config_account = accounts.retrieve(jid_bare)
        config_account = accounts.retrieve(jid_bare)
        await SQLiteGeneral.update_setting_value(db_file, key, 1)
        config_account.settings[key] = 1
        message = "OMEMO is enabled."
        return message

    def set_order_normal(jid_bare):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        # TODO /questions/2279706/select-random-row-from-a-sqlite-table
        # NOTE sqlitehandler.get_entry_unread
        message = "Updates will be sent by normal order."
        return message

    # TODO
    def set_order_random(jid_bare):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        # TODO /questions/2279706/select-random-row-from-a-sqlite-table
        # NOTE sqlitehandler.get_entry_unread
        message = "Updates will be sent by random order."
        return message

    async def feed_disable(jid_bare, feed_id):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        try:
            config_account = accounts.retrieve(jid_bare)
            db_file = config_account.database
            await SQLiteGeneral.set_enabled_status(db_file, feed_id, 0)
            await SQLiteGeneral.mark_feed_as_read(db_file, feed_id)
            name = SQLiteGeneral.get_feed_title(db_file, feed_id)
            addr = SQLiteGeneral.get_feed_url(db_file, feed_id)
            message = ("Updates are now disabled for subscription."
                       f"\n{addr}\n*{name}*")
        except:
            message = f"No subscription with index {feed_id} was found."
        return message

    async def feed_enable(jid_bare, feed_id):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	{feed_id}")
        try:
            config_account = accounts.retrieve(jid_bare)
            db_file = config_account.database
            await SQLiteGeneral.set_enabled_status(db_file, feed_id, 1)
            name = SQLiteGeneral.get_feed_title(db_file, feed_id)
            addr = SQLiteGeneral.get_feed_url(db_file, feed_id)
            message = ("Updates are now enabled for subscription."
                       f"\n{addr}\n*{name}*")
        except:
            message = f"No subscription with index {feed_id} was found."
        return message
