#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
#from asyncio import Lock
from slixfeed.configuration.singleton import configurations
from slixfeed.utility.logger import UtilityLogger
from sqlite3 import connect, Error, IntegrityError, Row
import sys
import time

# from eliot import start_action, to_file
# # with start_action(action_type="list_feeds()", db=db_file):
# # with start_action(action_type="last_entries()", num=num):
# # with start_action(action_type="get_feeds()"):
# # with start_action(action_type="remove_entry()", source=source):
# # with start_action(action_type="search_entries()", query=query):
# # with start_action(action_type="check_entry()", link=link):

CURSORS = {}

# aiosqlite
DBLOCK = asyncio.Lock()

db_file = configurations.database_focuscript

logger = UtilityLogger(__name__)

class SQLiteFocuscript:

    def create_connection(db_file):
        """
        Create a database connection to a given SQLite database.

        :param db_file: Path to a database file.
        :type db_file: str.

        :return conn: Connection object or None.
        :rtype:
        """
        time_begin = time.time()
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        message_log = "{}"
        logger.debug(message_log.format(function_name))
        conn = None
        try:
            conn = connect(db_file)
            conn.execute("PRAGMA foreign_keys = ON")
            # return conn
        except Error as e:
            logger.error(f"{function_name}	{db_file}	{str(e)}")
        time_end = time.time()
        difference = time_end - time_begin
        if difference > 1:
            logger.warning(f"{function_name}	{db_file}	Duration: {difference}")
        return conn

    def create_database(db_file):
        """
        Create an SQLite database.

        :param db_file: Path to a database file.
        :type db_file: str.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            table_uri = (
                """
                CREATE TABLE IF NOT EXISTS uri (
                    id INTEGER NOT NULL,
                    base TEXT NOT NULL UNIQUE,
                    PRIMARY KEY ("id")
                );
                """
            )
            table_condition = (
                """
                CREATE TABLE IF NOT EXISTS condition (
                    id INTEGER NOT NULL,
                    query TEXT NOT NULL UNIQUE,
                    PRIMARY KEY ("id")
                );
                """
            )
            table_exclude_pathname = (
                """
                CREATE TABLE IF NOT EXISTS exclude_pathname (
                    id INTEGER NOT NULL,
                    pathname TEXT NOT NULL UNIQUE,
                    PRIMARY KEY ("id")
                );
                """
            )
            table_exclude_protocol = (
                """
                CREATE TABLE IF NOT EXISTS exclude_protocol (
                    id INTEGER NOT NULL,
                    protocol TEXT NOT NULL UNIQUE,
                    PRIMARY KEY ("id")
                );
                """
            )
            table_exclude_hostname = (
                """
                CREATE TABLE IF NOT EXISTS exclude_hostname (
                    id INTEGER NOT NULL,
                    hostname TEXT NOT NULL UNIQUE,
                    PRIMARY KEY ("id")
                );
                """
            )
            table_execution = (
                """
                CREATE TABLE IF NOT EXISTS execution (
                    id INTEGER NOT NULL,
                    moment TEXT NOT NULL UNIQUE,
                    PRIMARY KEY ("id")
                );
                """
            )
            table_interval = (
                """
                CREATE TABLE IF NOT EXISTS interval (
                    id INTEGER NOT NULL,
                    seconds TEXT NOT NULL UNIQUE,
                    PRIMARY KEY ("id")
                );
                """
            )
            table_match_pathname = (
                """
                CREATE TABLE IF NOT EXISTS match_pathname (
                    id INTEGER NOT NULL,
                    pathname TEXT NOT NULL UNIQUE,
                    PRIMARY KEY ("id")
                );
                """
            )
            table_match_protocol = (
                """
                CREATE TABLE IF NOT EXISTS match_protocol (
                    id INTEGER NOT NULL,
                    protocol TEXT NOT NULL UNIQUE,
                    PRIMARY KEY ("id")
                );
                """
            )
            table_match_hostname = (
                """
                CREATE TABLE IF NOT EXISTS match_hostname (
                    id INTEGER NOT NULL,
                    hostname TEXT NOT NULL UNIQUE,
                    PRIMARY KEY ("id")
                );
                """
            )
            table_namespace = (
                """
                CREATE TABLE IF NOT EXISTS namespace (
                    id INTEGER NOT NULL,
                    xmlns TEXT NOT NULL UNIQUE,
                    PRIMARY KEY ("id")
                );
                """
            )
            table_prefix = (
                """
                CREATE TABLE IF NOT EXISTS prefix (
                    id INTEGER NOT NULL,
                    prefix TEXT NOT NULL UNIQUE,
                    PRIMARY KEY ("id")
                );
                """
            )
            table_focuscript = (
                """
                CREATE TABLE IF NOT EXISTS focuscript (
                    id INTEGER NOT NULL,
                    identifier TEXT NOT NULL UNIQUE,
                    filename TEXT UNIQUE,
                    condition_id INTEGER,
                    interval_id INTEGER,
                    uri_id INTEGER,
                    version_id INTEGER,
                    FOREIGN KEY ("condition_id") REFERENCES "condition" ("id"),
                    FOREIGN KEY ("interval_id") REFERENCES "interval" ("id"),
                    FOREIGN KEY ("uri_id") REFERENCES "uri" ("id"),
                    FOREIGN KEY ("version_id") REFERENCES "version" ("id"),
                    PRIMARY KEY ("id")
                );
                """
            )
            table_utility = (
                """
                CREATE TABLE IF NOT EXISTS utility (
                    id INTEGER NOT NULL,
                    utility TEXT NOT NULL UNIQUE,
                    PRIMARY KEY ("id")
                );
                """
            )
            table_version = (
                """
                CREATE TABLE IF NOT EXISTS version (
                    id INTEGER NOT NULL,
                    version TEXT NOT NULL UNIQUE,
                    PRIMARY KEY ("id")
                );
                """
            )
            table_aff_focus_exclude = (
                """
                CREATE TABLE IF NOT EXISTS aff_focus_exclude (
                    id INTEGER NOT NULL,
                    focus_id INTEGER,
                    hostname_id INTEGER,
                    pathname_id INTEGER,
                    protocol_id INTEGER,
                    FOREIGN KEY ("focus_id") REFERENCES "focuscript" ("id"),
                    FOREIGN KEY ("hostname_id") REFERENCES "exclude_hostname" ("id"),
                    FOREIGN KEY ("pathname_id") REFERENCES "exclude_pathname" ("id"),
                    FOREIGN KEY ("protocol_id") REFERENCES "exclude_protocol" ("id"),
                    PRIMARY KEY ("id")
                );
                """
            )
            table_aff_focus_execute = (
                """
                CREATE TABLE IF NOT EXISTS aff_focus_execute (
                    id INTEGER NOT NULL,
                    focus_id INTEGER,
                    utility_id INTEGER,
                    moment_id INTEGER,
                    FOREIGN KEY ("focus_id") REFERENCES "focuscript" ("id"),
                    FOREIGN KEY ("utility_id") REFERENCES "utility" ("id"),
                    FOREIGN KEY ("moment_id") REFERENCES "execute" ("id"),
                    PRIMARY KEY ("id")
                );
                """
            )
            table_aff_focus_match = (
                """
                CREATE TABLE IF NOT EXISTS aff_focus_match (
                    id INTEGER NOT NULL,
                    focus_id INTEGER,
                    hostname_id INTEGER,
                    pathname_id INTEGER,
                    protocol_id INTEGER,
                    FOREIGN KEY ("focus_id") REFERENCES "focuscript" ("id"),
                    FOREIGN KEY ("hostname_id") REFERENCES "match_hostname" ("id"),
                    FOREIGN KEY ("pathname_id") REFERENCES "match_pathname" ("id"),
                    FOREIGN KEY ("protocol_id") REFERENCES "match_protocol" ("id"),
                    PRIMARY KEY ("id")
                );
                """
            )
            table_aff_focus_namespace = (
                """
                CREATE TABLE IF NOT EXISTS aff_focus_namespace (
                    id INTEGER NOT NULL,
                    focus_id INTEGER,
                    xmlns_id INTEGER,
                    prefix_id INTEGER,
                    FOREIGN KEY ("focus_id") REFERENCES "focuscript" ("id"),
                    FOREIGN KEY ("xmlns_id") REFERENCES "namespace" ("id"),
                    FOREIGN KEY ("prefix_id") REFERENCES "prefix" ("id"),
                    PRIMARY KEY ("id")
                );
                """
            )
            table_aff_focus_namespace_append = (
                """
                CREATE TABLE IF NOT EXISTS aff_focus_namespace_append (
                    id INTEGER NOT NULL,
                    focus_id INTEGER,
                    xmlns_id INTEGER,
                    prefix_id INTEGER,
                    FOREIGN KEY ("focus_id") REFERENCES "focuscript" ("id"),
                    FOREIGN KEY ("xmlns_id") REFERENCES "namespace" ("id"),
                    FOREIGN KEY ("prefix_id") REFERENCES "prefix" ("id"),
                    PRIMARY KEY ("id")
                );
                """
            )
            table_aff_focus_namespace_dismiss = (
                """
                CREATE TABLE IF NOT EXISTS aff_focus_namespace_dismiss (
                    id INTEGER NOT NULL,
                    focus_id INTEGER,
                    xmlns_id INTEGER,
                    FOREIGN KEY ("focus_id") REFERENCES "focuscript" ("id"),
                    FOREIGN KEY ("xmlns_id") REFERENCES "namespace" ("id"),
                    PRIMARY KEY ("id")
                );
                """
            )
            cur = conn.cursor()
            cur.execute(table_aff_focus_exclude)
            cur.execute(table_aff_focus_execute)
            cur.execute(table_aff_focus_match)
            cur.execute(table_aff_focus_namespace)
            cur.execute(table_aff_focus_namespace_append)
            cur.execute(table_aff_focus_namespace_dismiss)
            cur.execute(table_condition)
            cur.execute(table_exclude_hostname)
            cur.execute(table_exclude_pathname)
            cur.execute(table_exclude_protocol)
            cur.execute(table_execution)
            cur.execute(table_focuscript)
            cur.execute(table_interval)
            cur.execute(table_match_hostname)
            cur.execute(table_match_pathname)
            cur.execute(table_match_protocol)
            cur.execute(table_namespace)
            cur.execute(table_prefix)
            cur.execute(table_uri)
            cur.execute(table_utility)
            cur.execute(table_version)

    def select_id_by_xmlns(db_file: str, xmlns: str) -> int:
        """
        Select an id of a given xmlns by a given value.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param xmlns: XML Namespace.
        :type xmlns: str.

        :return ix: Index.
        :rtype int:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            cur = conn.cursor()
            cur.row_factory = Row
            sql = (
                """
                SELECT id
                FROM namespace
                WHERE xmlns = ?
                """
                )
            par = (xmlns,)
            ix = cur.execute(sql, par).fetchone()
        return ix["id"] if ix else None

    async def insert_xmlns_to_namespace(db_file: str, xmlns: str) -> int:
        """
        Insert value xmlns to table namespace.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param xmlns: XML Namespace.
        :type xmlns: str.

        :return ix: Index.
        :rtype int:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        async with DBLOCK:
            with SQLiteFocuscript.create_connection(db_file) as conn:
                cur = conn.cursor()
                sql = (
                    """
                    INSERT
                    INTO namespace(
                        xmlns)
                    VALUES(
                        ?)
                    """
                    )
                par = (xmlns,)
                try:
                    cur.execute(sql, par)
                    return cur.lastrowid
                except IntegrityError as e:
                    logger.error(f"{function_name}	{db_file}	{str(e)}")

    def select_id_by_version(db_file: str, version: str) -> int:
        """
        Select an id of a given version by a given value.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param version: Version.
        :type version: str.

        :return ix: Index.
        :rtype int:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            cur = conn.cursor()
            cur.row_factory = Row
            sql = (
                """
                SELECT id
                FROM version
                WHERE version = ?
                """
                )
            par = (version,)
            ix = cur.execute(sql, par).fetchone()
        return ix["id"] if ix else None

    async def insert_version_to_version(db_file: str, version: str) -> int:
        """
        Insert value version to table version.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param version: Version.
        :type version: str.

        :return ix: Index.
        :rtype int:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        async with DBLOCK:
            with SQLiteFocuscript.create_connection(db_file) as conn:
                cur = conn.cursor()
                sql = (
                    """
                    INSERT
                    INTO version(
                        version)
                    VALUES(
                        ?)
                    """
                    )
                par = (version,)
                try:
                    cur.execute(sql, par)
                    return cur.lastrowid
                except IntegrityError as e:
                    logger.error(f"{function_name}	{db_file}	{str(e)}")

    def select_id_by_prefix(db_file: str, prefix: str) -> int:
        """
        Select an id of a given prefix by a given value.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param prefix: XML Namespace prefix.
        :type prefix: str.

        :return ix: Index.
        :rtype int:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            cur = conn.cursor()
            cur.row_factory = Row
            sql = (
                """
                SELECT id
                FROM prefix
                WHERE prefix = ?
                """
                )
            par = (prefix,)
            ix = cur.execute(sql, par).fetchone()
        return ix["id"] if ix else None

    async def insert_prefix_to_prefix(db_file: str, prefix: str) -> int:
        """
        Insert value prefix to table prefix.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param prefix: XML Namespace prefix.
        :type prefix: str.

        :return ix: Index.
        :rtype int:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        async with DBLOCK:
            with SQLiteFocuscript.create_connection(db_file) as conn:
                cur = conn.cursor()
                sql = (
                    """
                    INSERT
                    INTO prefix(
                        prefix)
                    VALUES(
                        ?)
                    """
                    )
                par = (prefix,)
                try:
                    cur.execute(sql, par)
                    return cur.lastrowid
                except IntegrityError as e:
                    logger.error(f"{function_name}	{db_file}	{str(e)}")

    async def insert_focus_id_and_xmlns_id_and_prefix_id_to_aff_focus_namespace(
        db_file: str, focus_id: int, xmlns_id: int, prefix_id: int) -> int:
        """
        Insert values focus_id and xmlns_id and prefix_id to table aff_focus_namespace.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param focus_id: ID of Focuscript.
        :type focus_id: int.

        :param xmlns_id: ID of XML Namespace.
        :type xmlns_id: int.

        :param prefix_id: ID of XML Namespace prefix.
        :type prefix_id: int.

        :return ix: Index.
        :rtype int:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        async with DBLOCK:
            with SQLiteFocuscript.create_connection(db_file) as conn:
                cur = conn.cursor()
                sql = (
                    """
                    INSERT
                    INTO aff_focus_namespace(
                         focus_id, xmlns_id, prefix_id)
                    VALUES(
                        ?, ?, ?)
                    """
                    )
                par = (focus_id, xmlns_id, prefix_id)
                try:
                    cur.execute(sql, par)
                    return cur.lastrowid
                except IntegrityError as e:
                    logger.error(f"{function_name}	{db_file}	{str(e)}")

    def select_namespaces_by_focus_id(db_file: str, focus_id: int) -> list:
        """
        Select rows of IDs of xmlns and prefix.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param focus_id: ID of a Focuscript.
        :type focus_id: int.

        :return rows: Rows.
        :rtype list:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            cur = conn.cursor()
            cur.row_factory = Row
            sql = (
                """
                SELECT xmlns_id, prefix_id
                FROM aff_focus_namespace
                WHERE focus_id = ?
                """
                )
            par = (focus_id,)
            ix = cur.execute(sql, par).fetchall()
        return ix

    def select_id_by_seconds(db_file: str, seconds: int) -> int:
        """
        Select an id of a given interval by a given value.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param seconds: Seconds.
        :type seconds: int.

        :return ix: Index.
        :rtype int:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            cur = conn.cursor()
            cur.row_factory = Row
            sql = (
                """
                SELECT id
                FROM interval
                WHERE seconds = ?
                """
                )
            par = (seconds,)
            ix = cur.execute(sql, par).fetchone()
        return ix["id"] if ix else None

    def select_id_by_identifier(db_file: str, identifier: str) -> int:
        """
        Select an id of a Focuscript identifier by a given identifier.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param identifier: Identifier.
        :type identifier: str.

        :return ix: Index.
        :rtype int:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            cur = conn.cursor()
            cur.row_factory = Row
            sql = (
                """
                SELECT id
                FROM focuscript
                WHERE identifier = ?
                """
                )
            par = (identifier,)
            ix = cur.execute(sql, par).fetchone()
        return ix["id"] if ix else None

    def select_version_by_focus_id(db_file: str, focus_id: int) -> str:
        """
        Select a version of a Focuscript by a given focus_id.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param focus_id: ID of a Focuscript.
        :type focus_id: int.

        :return version: Version.
        :rtype str:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            cur = conn.cursor()
            sql = (
                """
                SELECT version
                FROM version
                INNER JOIN focuscript ON
                           version.id = focuscript.version_id
                WHERE focuscript.id = ?
                """
                )
            par = (focus_id,)
            ix = cur.execute(sql, par).fetchone()
        return ix[0] if ix else None

    def select_focus_id_by_condition_id(db_file: str, condition_id: int) -> str:
        """
        Select an ID of a Focuscript by a given condition_id.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param condition_id: ID of a Focuscript.
        :type condition_id: int.

        :return ix: ID of a Focuscript.
        :rtype int:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            cur = conn.cursor()
            sql = (
                """
                SELECT id
                FROM focuscript
                WHERE condition_id = ?
                """
                )
            par = (condition_id,)
            ix = cur.execute(sql, par).fetchone()
        return ix[0] if ix else None

    def select_filename_by_id(db_file: str, focus_id: int) -> str:
        """
        Select a filename of a Focuscript by a given id.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param focus_id: ID of a Focuscript.
        :type focus_id: int.

        :return filename: Filename.
        :rtype str:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            cur = conn.cursor()
            sql = (
                """
                SELECT filename
                FROM focuscript
                WHERE id = ?
                """
                )
            par = (focus_id,)
            ix = cur.execute(sql, par).fetchone()
        return ix[0] if ix else None

    def select_prefix_by_id(db_file: str, prefix_id: int) -> str:
        """
        Select an XML Namespace of a Focuscript by a given id.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param prefix_id: ID of an XML Namespace prefix.
        :type prefix_id: int.

        :return prefix: XML Namespace prefix.
        :rtype str:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            cur = conn.cursor()
            sql = (
                """
                SELECT prefix
                FROM prefix
                WHERE id = ?
                """
                )
            par = (prefix_id,)
            ix = cur.execute(sql, par).fetchone()
        return ix[0] if ix else None

    def select_xmlns_by_id(db_file: str, xmlns_id: int) -> str:
        """
        Select an XML Namespace of a Focuscript by a given id.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param xmlns_id: ID of an XML Namespace.
        :type xmlns_id: int.

        :return xmlns: XML Namespace.
        :rtype str:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            cur = conn.cursor()
            sql = (
                """
                SELECT xmlns
                FROM namespace
                WHERE id = ?
                """
                )
            par = (xmlns_id,)
            ix = cur.execute(sql, par).fetchone()
        return ix[0] if ix else None

    def select_condition_id_by_id(db_file: str, focus_id: int) -> int:
        """
        Select a condition_id of a Focuscript by a given focus_id.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param focus_id: ID of a Focuscript.
        :type focus_id: int.

        :return ix: Index.
        :rtype int:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            cur = conn.cursor()
            sql = (
                """
                SELECT condition_id
                FROM focuscript
                WHERE id = ?
                """
                )
            par = (focus_id,)
            ix = cur.execute(sql, par).fetchone()
        return ix[0] if ix else None

    def select_query_by_id(db_file: str, condition_id: int) -> str:
        """
        Select a query of a Focuscript by a given condition_id.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param condition_id: ID of a condition.
        :type condition_id: int.

        :return query: An XPath Query.
        :rtype str:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            cur = conn.cursor()
            sql = (
                """
                SELECT query
                FROM condition
                WHERE id = ?
                """
                )
            par = (condition_id,)
            ix = cur.execute(sql, par).fetchone()
        return ix[0] if ix else None

    async def insert_properties_to_focuscript(
        db_file: str, identifier: str, filename, condition_id=None, interval_id=None, uri_id=None, version_id=None) -> int:
        """
        Insert property references of a Focuscript.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param identifier: Identifier.
        :type identifier: str.

        :param filename: Filename.
        :type filename: str.

        :param condition_id: ID of Condition.
        :type condition_id: int.

        :param interval_id: ID of Interval.
        :type interval_id: int.

        :param uri_id: ID of URI.
        :type uri_id: int.

        :param version_id: ID of Version.
        :type version_id: int.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        async with DBLOCK:
            with SQLiteFocuscript.create_connection(db_file) as conn:
                cur = conn.cursor()
                cur.row_factory = Row
                sql = (
                    """
                    INSERT
                    INTO focuscript(
                        identifier, filename, condition_id, interval_id, uri_id, version_id)
                    VALUES(
                        ?, ?, ?, ?, ?, ?)
                    """
                    )
                par = (identifier, filename, condition_id, interval_id, uri_id, version_id)
                try:
                    cur.execute(sql, par)
                    return cur.lastrowid
                except IntegrityError as e:
                    logger.error(f"{function_name}	{db_file}	{str(e)}")

    async def insert_seconds_to_interval(db_file: str, seconds: int) -> int:
        """
        Insert value seconds to table interval.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param seconds: Seconds.
        :type seconds: int.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        async with DBLOCK:
            with SQLiteFocuscript.create_connection(db_file) as conn:
                cur = conn.cursor()
                sql = (
                    """
                    INSERT
                    INTO interval(
                        seconds)
                    VALUES(
                        ?)
                    """
                    )
                par = (seconds,)
                try:
                    cur.execute(sql, par)
                    return cur.lastrowid
                except IntegrityError as e:
                    logger.error(f"{function_name}	{db_file}	{str(e)}")

    def select_id_by_match_pathname(db_file: str, pathname: str) -> int:
        """
        Select an id of a given pathname by a given value.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param pathname: Match rule of pathname.
        :type pathname: str.

        :return ix: Index.
        :rtype int:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            cur = conn.cursor()
            cur.row_factory = Row
            sql = (
                """
                SELECT id
                FROM match_pathname
                WHERE pathname = ?
                """
                )
            par = (pathname,)
            ix = cur.execute(sql, par).fetchone()
        return ix["id"] if ix else None

    def select_rows_match_protocol(db_file: str) -> list:
        """
        Select rows of match protocol rule.

        :param db_file: Path to a database file.
        :type db_file: str.

        :return protocol: Match rule of protocol.
        :rtype list:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            cur = conn.cursor()
            cur.row_factory = Row
            sql = (
                """
                SELECT *
                FROM match_protocol
                """
                )
            ix = cur.execute(sql).fetchall()
        return ix

    def select_rows_match_hostname(db_file: str) -> list:
        """
        Select rows of match hostname rule.

        :param db_file: Path to a database file.
        :type db_file: str.

        :return hostname: Match rule of hostname.
        :rtype list:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            cur = conn.cursor()
            cur.row_factory = Row
            sql = (
                """
                SELECT *
                FROM match_hostname
                """
                )
            ix = cur.execute(sql).fetchall()
        return ix

    def select_rows_match_pathname(db_file: str) -> list:
        """
        Select rows of match pathname rule.

        :param db_file: Path to a database file.
        :type db_file: str.

        :return pathname: Match rule of pathname.
        :rtype list:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            cur = conn.cursor()
            cur.row_factory = Row
            sql = (
                """
                SELECT *
                FROM match_pathname
                """
                )
            ix = cur.execute(sql).fetchall()
        return ix

    def select_match_pathname_by_id(db_file: str, id: int) -> str:
        """
        Select a match pathname rule by a given id.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param ix: Index.
        :type ix: int

        :return pathname: Match rule of pathname.
        :rtype str:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            cur = conn.cursor()
            cur.row_factory = Row
            sql = (
                """
                SELECT pathname
                FROM match_pathname
                WHERE id = ?
                """
                )
            par = (pathname,)
            ix = cur.execute(sql, par).fetchone()
        return ix["pathname"] if ix else None

    def select_focus_ids_by_match_ids(
        db_file: str, protocol_id: int, hostname_id: int, pathname_id: int) -> int:
        """
        Select IDs of a Focuscripts by given match ids.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param protocol_id: Index.
        :type protocol_id: int

        :param hostname_id: Index.
        :type hostname_id: int

        :param pathname_id: Index.
        :type pathname_id: int

        :return focus_ids: IDs of Focuscripts.
        :rtype list:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            cur = conn.cursor()
            cur.row_factory = Row
            sql = (
                """
                SELECT focus_id
                FROM aff_focus_match
                WHERE protocol_id = :protocol_id AND
                      hostname_id = :hostname_id AND
                      pathname_id = :pathname_id
                """
                )
            par = {
                "protocol_id": protocol_id,
                "hostname_id": hostname_id,
                "pathname_id": pathname_id
                }
            ix = cur.execute(sql, par).fetchall()
        return ix

    def select_match_protocol_by_id(db_file: str, id: int) -> str:
        """
        Select a match protocol rule by a given id.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param ix: Index.
        :type ix: int

        :return protocol: Match rule of protocol.
        :rtype str:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            cur = conn.cursor()
            cur.row_factory = Row
            sql = (
                """
                SELECT protocol
                FROM match_protocol
                WHERE id = ?
                """
                )
            par = (protocol,)
            ix = cur.execute(sql, par).fetchone()
        return ix["protocol"] if ix else None

    def select_match_hostname_by_id(db_file: str, id: int) -> str:
        """
        Select a match hostname rule by a given id.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param ix: Index.
        :type ix: int

        :return hostname: Match rule of hostname.
        :rtype str:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            cur = conn.cursor()
            cur.row_factory = Row
            sql = (
                """
                SELECT hostname
                FROM match_hostname
                WHERE id = ?
                """
                )
            par = (hostname,)
            ix = cur.execute(sql, par).fetchone()
        return ix["hostname"] if ix else None

    async def insert_pathname_to_match_pathname(db_file: str, pathname: str) -> int:
        """
        Insert value pathname to table match_pathname.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param pathname: Match rule of pathname.
        :type pathname: str.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        async with DBLOCK:
            with SQLiteFocuscript.create_connection(db_file) as conn:
                cur = conn.cursor()
                sql = (
                    """
                    INSERT
                    INTO match_pathname(
                        pathname)
                    VALUES(
                        ?)
                    """
                    )
                par = (pathname,)
                try:
                    cur.execute(sql, par)
                    return cur.lastrowid
                except IntegrityError as e:
                    logger.error(f"{function_name}	{db_file}	{str(e)}")

    def select_id_by_match_hostname(db_file: str, hostname: str) -> int:
        """
        Select an id of a given hostname by a given value.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param hostname: Match rule of hostname.
        :type hostname: str.

        :return ix: Index.
        :rtype int:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            cur = conn.cursor()
            cur.row_factory = Row
            sql = (
                """
                SELECT id
                FROM match_hostname
                WHERE hostname = ?
                """
                )
            par = (hostname,)
            ix = cur.execute(sql, par).fetchone()
        return ix["id"] if ix else None

    async def insert_hostname_to_match_hostname(db_file: str, hostname: str) -> int:
        """
        Insert value hostname to table match_hostnames.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param hostname: Match rule of hostname.
        :type hostname: str.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        async with DBLOCK:
            with SQLiteFocuscript.create_connection(db_file) as conn:
                cur = conn.cursor()
                sql = (
                    """
                    INSERT
                    INTO match_hostname(
                        hostname)
                    VALUES(
                        ?)
                    """
                    )
                par = (hostname,)
                try:
                    cur.execute(sql, par)
                    return cur.lastrowid
                except IntegrityError as e:
                    logger.error(f"{function_name}	{db_file}	{str(e)}")

    def select_id_by_match_protocol(db_file: str, protocol: str) -> int:
        """
        Select an id of a given protocol by a given value.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param protocol: Match rule of protocol.
        :type protocol: str.

        :return ix: Index.
        :rtype int:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            cur = conn.cursor()
            cur.row_factory = Row
            sql = (
                """
                SELECT id
                FROM match_protocol
                WHERE protocol = ?
                """
                )
            par = (protocol,)
            ix = cur.execute(sql, par).fetchone()
        return ix["id"] if ix else None

    async def insert_protocol_to_match_protocol(db_file: str, protocol: str) -> int:
        """
        Insert value protocol to table match_protocols.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param protocol: Match rule of protocol.
        :type protocol: str.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        async with DBLOCK:
            with SQLiteFocuscript.create_connection(db_file) as conn:
                cur = conn.cursor()
                sql = (
                    """
                    INSERT
                    INTO match_protocol(
                        protocol)
                    VALUES(
                        ?)
                    """
                    )
                par = (protocol,)
                try:
                    cur.execute(sql, par)
                    return cur.lastrowid
                except IntegrityError as e:
                    logger.error(f"{function_name}	{db_file}	{str(e)}")

    async def insert_focus_id_and_match_id_to_aff_focus_match(
        db_file: str, focus_id: int, hostname_id: int, pathname_id: int, protocol_id: int) -> int:
        """
        Insert values focus_id and condition_id to table aff_focus_condition.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param focus_id: ID of Focuscript.
        :type focus_id: int.

        :param protocol_id: ID of match rule of protocol.
        :type protocol_id: int.

        :param hostname_id: ID of match rule of hostname.
        :type hostname_id: int.

        :param pathname_id: ID of match rule of pathname.
        :type pathname_id: int.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        async with DBLOCK:
            with SQLiteFocuscript.create_connection(db_file) as conn:
                cur = conn.cursor()
                sql = (
                    """
                    INSERT
                    INTO aff_focus_match(
                         focus_id, hostname_id, pathname_id, protocol_id)
                    VALUES(
                        ?, ?, ?, ?)
                    """
                    )
                par = (focus_id, hostname_id, pathname_id, protocol_id)
                try:
                    cur.execute(sql, par)
                    return cur.lastrowid
                except IntegrityError as e:
                    logger.error(f"{function_name}	{db_file}	{str(e)}")

    def select_id_by_condition(db_file: str, query: str) -> int:
        """
        Select an id of a given condition by a given value.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param query: Xpath condition rule.
        :type query: str.

        :return ix: Index.
        :rtype int:
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            cur = conn.cursor()
            cur.row_factory = Row
            sql = (
                """
                SELECT id
                FROM condition
                WHERE query = ?
                """
                )
            par = (query,)
            ix = cur.execute(sql, par).fetchone()
        return ix["id"] if ix else None

    async def insert_query_to_condition(db_file: str, query: str) -> int:
        """
        Insert value query to table condition.

        :param db_file: Path to a database file.
        :type db_file: str.

        :param query: Xpath condition rule.
        :type query: str.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        async with DBLOCK:
            with SQLiteFocuscript.create_connection(db_file) as conn:
                cur = conn.cursor()
                sql = (
                    """
                    INSERT
                    INTO condition(
                        query)
                    VALUES(
                        ?)
                    """
                    )
                par = (query,)
                try:
                    cur.execute(sql, par)
                    return cur.lastrowid
                except IntegrityError as e:
                    logger.error(f"{function_name}	{db_file}	{str(e)}")

    async def delete_an_address(db_file, address):
        """
        Delete an address.

        Parameters
        ----------
        db_file : str
            Path to database file.
        jid : tuple
            An address.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        async with DBLOCK:
            with SQLiteFocuscript.create_connection(db_file) as conn:
                cur = conn.cursor()
                sql = (
                    """
                    DELETE
                    FROM addresses
                    WHERE address = ?
                    """
                    )
                par = (address,)
                try:
                    cur.execute(sql, par)
                except IntegrityError as e:
                    logger.warning(f"{function_name}	{db_file}	{str(e)}")
                    logger.error(e)

    def get_addresses_of_kind_and_protocol(db_file, akind, aprotocol):
        """
        Get addresses of given type.

        Parameters
        ----------
        db_file : str
            Path to database file.

        Returns
        -------
        jids : tuple
            A list of addresses.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteFocuscript.create_connection(db_file) as conn:
            cur = conn.cursor()
            sql = (
                """
                SELECT a.address
                FROM addresses a
                JOIN linker l ON l.address_id = a.id
                JOIN kinds k ON l.kind_id = k.id
                JOIN protocols p ON l.protocol_id = p.id
                WHERE k.kind = :kind
                  AND p.protocol = :protocol;
                """
                )
            par = {
                "kind": akind,
                "protocol": aprotocol
                }
            addresses = cur.execute(sql, par).fetchall()
        return addresses
