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
   Returning a list of values doesn't' seem to be a good practice.

3) Special statistics for operator:
   * Size of database(s);
   * Amount of JIDs subscribed;
   * Amount of feeds of all JIDs;
   * Amount of entries of all JIDs.

"""

from slixfeed.configuration.singleton import configurations
from slixfeed.utility.logger import UtilityLogger
import sys
from urllib.parse import parse_qs, urlencode, urljoin, urlsplit, urlunsplit

logger = UtilityLogger(__name__)

"""

FIXME

1) Do not handle base64
   https://www.lilithsaintcrow.com/2024/02/love-anonymous/
   data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABaAAAAeAAQAAAAAQ6M16AAAAAnRSTlMAAHaTzTgAAAFmSURBVBgZ7cEBAQAAAIKg/q92SMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADgWE3LAAGyZmPPAAAAAElFTkSuQmCC
   https://www.lilithsaintcrow.com/2024/02/love-anonymous//image/png;base64,iVBORw0KGgoAAAANSUhEUgAABaAAAAeAAQAAAAAQ6M16AAAAAnRSTlMAAHaTzTgAAAFmSURBVBgZ7cEBAQAAAIKg/q92SMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADgWE3LAAGyZmPPAAAAAElFTkSuQmCC


"""

class UtilityUri:

    # TODO Move to UtilityText
    # TODO Change name to is_keyword_included_in_list
    def is_host(hostname: str, hosts: list) -> bool:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{hostname}	Start")
        for host in hosts:
            if hostname in host:
                logger.info(f"{function_name}	{hostname}	{host}")
                return True

    # TODO Move to UtilityText
    # TODO Change name to is_keyword_included_in_list_and_ends_with
    def is_tld(hostname: str, tlds: list) -> bool:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{hostname}	Start")
        for tld in tlds:
            if hostname.endswith(f".{tld}"):
                logger.info(f"{function_name}	{hostname}	{tld}")
                return True

    def remove_tracking_parameters(url: str) -> str:
        """
        Remove queries with tracking parameters.

        Parameters
        ----------
        trackers : list
            A list of queries.
        url : str
            A URL.

        Returns
        -------
        url : str
            A processed URL.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{url}	Start")
        parted_url = urlsplit(url)
        protocol = parted_url.scheme
        hostname = parted_url.netloc
        pathname = parted_url.path
        queries = parse_qs(parted_url.query)
        fragment = parted_url.fragment
        for tracker in configurations.trackers:
            if tracker in queries: del queries[tracker]
        queries_new = urlencode(queries, doseq=True)
        url = urlunsplit([protocol, hostname, pathname, queries_new, fragment])
        return url

    def feed_to_http(url: str) -> str:
        """
        Set scheme to HTTP.

        Parameters
        ----------
        url : str
            URL.

        Returns
        -------
        uri_new : str
            URL.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{url}	Start")
        uri_parted = urlsplit(url)
        uri_new = urlunsplit(["http", uri_parted.netloc, uri_parted.path,
                              uri_parted.query, uri_parted.fragment])
        return uri_new

    def trim_url(url: str) -> str:
        """
        Check URL pathname for double slash.

        Parameters
        ----------
        url : str
            URL.

        Returns
        -------
        url : str
            URL.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{url}	Start")
        if url.startswith("data:") and ";base64," in url:
            return url
        parted_url = urlsplit(url)
        protocol = parted_url.scheme
        hostname = parted_url.netloc
        pathname = parted_url.path
        queries = parted_url.query
        fragment = parted_url.fragment
        while "//" in pathname:
            pathname = pathname.replace("//", "/")
        url = urlunsplit([protocol, hostname, pathname, queries, fragment])
        return url

# TODO
# Feed https://www.ocaml.org/feed.xml
# Link %20https://frama-c.com/fc-versions/cobalt.html%20

# FIXME
# Feed https://cyber.dabamos.de/blog/feed.rss
# Link https://cyber.dabamos.de/blog/#article-2022-07-15

    def join_url(source: str, link: str) -> str:
        """
        Join base URL with given pathname.

        Parameters
        ----------
        source : str
            Feed URL.
        link : str
            Link URL or pathname.

        Returns
        -------
        new_link : str
            URL.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{source} {link}	Start")
        if link.startswith("data:") and ";base64," in link:
            return link
        elif link.startswith("www."):
            new_link = "http://" + link
        #elif link.startswith("gemini://"):
        #    new_link = link.replace("gemini://", "gopher://")
        elif link.startswith("%20") and link.endswith("%20"):
            old_link = link.split("%20")
            # Remove first instance of %20.
            del old_link[0]
            # Remove last instance of %20.
            old_link.pop()
            new_link = "".join(old_link)
        else:
            new_link = urljoin(source, link)
        return new_link
