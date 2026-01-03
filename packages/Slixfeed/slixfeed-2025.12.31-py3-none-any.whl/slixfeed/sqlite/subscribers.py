#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
#from asyncio import Lock
from slixfeed.utility.logger import UtilityLogger
from sqlite3 import connect, Error, IntegrityError, Row
import sys

CURSORS = {}

# aiosqlite
DBLOCK = asyncio.Lock()

logger = UtilityLogger(__name__)

class SQLiteSubscribers:

    def create_connection(db_file):
        """
        Create a database connection to the SQLite database
        specified by db_file.

        Parameters
        ----------
        db_file : str
            Path to database file.

        Returns
        -------
        conn : object
            Connection object or None.
        """
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
        return conn

    def create_a_database_of_subscribers(db_file):
        """
        Create an SQLite database for an account.

        Parameters
        ----------
        db_file : str
            Path to database file.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteSubscribers.create_connection(db_file) as conn:
            addresses = (
                """
                CREATE TABLE IF NOT EXISTS addresses (
                    id INTEGER NOT NULL,
                    address TEXT UNIQUE,
                    PRIMARY KEY ("id")
                  );
                """
                )
            protocols = (
                """
                CREATE TABLE IF NOT EXISTS protocols (
                    id INTEGER NOT NULL,
                    protocol TEXT UNIQUE,
                    PRIMARY KEY ("id")
                  );
                """
                )
            kinds = (
                """
                CREATE TABLE IF NOT EXISTS kinds (
                    id INTEGER NOT NULL,
                    kind TEXT UNIQUE,
                    PRIMARY KEY ("id")
                  );
                """
                )
            linker = (
                """
                CREATE TABLE IF NOT EXISTS linker (
                    id INTEGER NOT NULL,
                    address_id INTEGER NOT NULL,
                    protocol_id INTEGER NOT NULL,
                    kind_id INTEGER NOT NULL,
                    FOREIGN KEY ("address_id") REFERENCES "addresses" ("id")
                      ON UPDATE CASCADE
                      ON DELETE CASCADE,
                    FOREIGN KEY ("protocol_id") REFERENCES "protocols" ("id"),
                    FOREIGN KEY ("kind_id") REFERENCES "kinds" ("id"),
                    PRIMARY KEY ("id")
                  );
                """
                )
            cur = conn.cursor()
            cur.execute(addresses)
            cur.execute(kinds)
            cur.execute(protocols)
            cur.execute(linker)

            for protocol in ("activitypub", "bitmessage", "email", "irc",
                             "lxmf", "mqtt", "nostr", "session", "sip", "tox",
                             "xmpp"):
                sql = (
                    """
                    INSERT
                    INTO protocols(
                        protocol)
                    VALUES(
                        ?)
                    """
                    )
                par = (protocol,)
                try:
                    cur.execute(sql, par)
                except IntegrityError as e:
                    logger.warning(f"{function_name}	{db_file}	Skipping: {str(protocol)}")
                    logger.error(e)

            for kind in ("mix", "muc", "private", "public"):
                sql = (
                    """
                    INSERT
                    INTO kinds(
                        kind)
                    VALUES(
                        ?)
                    """
                    )
                par = (kind,)
                try:
                    cur.execute(sql, par)
                except IntegrityError as e:
                    logger.warning(f"{function_name}	{db_file}	Skipping: {str(kind)}")
                    logger.error(e)

    def get_index_of_an_address(db_file, address):
        """
        Get an ID of given address.

        Parameters
        ----------
        db_file : str
            Path to database file.
        address : str
            An address.

        Returns
        -------
        ix : tuple
            Index.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteSubscribers.create_connection(db_file) as conn:
            cur = conn.cursor()
            sql = (
                """
                SELECT id
                FROM addresses
                WHERE address = ?
                """
                )
            par = (address,)
            result = cur.execute(sql, par).fetchone()
            return result[0] if result else None

    def get_index_of_a_protocol(db_file, protocol):
        """
        Get an ID of given protocol.

        Parameters
        ----------
        db_file : str
            Path to database file.
        protocol : str
            A protocol.

        Returns
        -------
        ix : tuple
            Index.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteSubscribers.create_connection(db_file) as conn:
            cur = conn.cursor()
            sql = (
                """
                SELECT id
                FROM protocols
                WHERE protocol = ?
                """
                )
            par = (protocol,)
            result = cur.execute(sql, par).fetchone()
            return result[0] if result else None

    def get_index_of_a_kind(db_file, kind):
        """
        Get an ID of given kind.

        Parameters
        ----------
        db_file : str
            Path to database file.
        kind : str
            A kind.

        Returns
        -------
        ix : tuple
            Index.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        with SQLiteSubscribers.create_connection(db_file) as conn:
            cur = conn.cursor()
            sql = (
                """
                SELECT id
                FROM kinds
                WHERE kind = ?
                """
                )
            par = (kind,)
            result = cur.execute(sql, par).fetchone()
            return result[0] if result else None

    async def insert_an_address(db_file, address):
        """
        Insert a new address.

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
            with SQLiteSubscribers.create_connection(db_file) as conn:
                cur = conn.cursor()
                sql = (
                    """
                    INSERT
                    INTO addresses(
                        address)
                    VALUES(
                        ?)
                    """
                    )
                par = (address,)
                try:
                    cur.execute(sql, par)
                except IntegrityError as e:
                    logger.warning(f"{function_name}	{db_file}	{str(e)}")
                    logger.error(e)

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
            with SQLiteSubscribers.create_connection(db_file) as conn:
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

    async def associate_kind_and_protocol_with_an_address(db_file, address_id,
                                                          kind_id, protocol_id):
        """
        Associate an address and kind and protocol.

        Parameters
        ----------
        db_file : str
            Path to database file.
        address_id : str
            Address ID.
        kind_id : str
            Kind ID.
        protocol_id : str
            Protocol ID.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{db_file}	Start")
        async with DBLOCK:
            with SQLiteSubscribers.create_connection(db_file) as conn:
                cur = conn.cursor()
                sql = (
                    """
                    INSERT
                    INTO linker(
                        address_id, kind_id, protocol_id)
                    VALUES(
                        ?, ?, ?)
                    """
                    )
                par = (address_id, kind_id, protocol_id)
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
        with SQLiteSubscribers.create_connection(db_file) as conn:
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
