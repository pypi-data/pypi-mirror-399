#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Schimon Jehudah <https://schapps.woodpeckersnest.eu/slixfeed/>
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

import bleach
from lxml import etree, html
from slixfeed.utility.logger import UtilityLogger
from slixfeed.utility.uri import UtilityUri
import sys

logger = UtilityLogger(__name__)

allowed_tags = [
    "a", "abbr", "addres", "articles", "aside", "b", "bdi", "bdo", "blockquote",
    "br", "code", "col", "colgroup", "dd", "del", "dfn", "div" ,"dl", "dt",
    "em", "figure", "figcaption", "footer", "h1", "h2", "h3", "h4", "h5", "h6",
    "header", "hr", "i", "img", "ins", "kbd", "li", "mark", "meter", "ol", "p",
    "pre", "rb", "rp", "rt", "rtc", "ruby", "s", "samp", "section", "strong",
    "span", "strong", "sub", "sup", "table", "tbody", "td" , "tfoot", "th",
    "thead", "tr", "track", "tt", "u", "ul", "var", "wbr"]

allowed_attributes = {
    "a": ["href", "title"],
    "abbr": ["title"],
    "article": ["dir"],
    "audio": ["src"],
    "bdo": ["dir"],
    "div": ["dir"],
    "img": ["alt", "src", "title"],
    "meter": ["high", "low", "max", "min", "optimum", "value"],
    "p": ["dir"],
    "source": ["src", "type"],
    "span": ["dir"],
    "video": ["poster", "src"]}

class UtilityHtml:

    def purify(data):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        return bleach.clean(
            data,
            tags=["sub", "sup"],
            strip=True,
            strip_comments=True)

    def sanitize(data):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        return bleach.clean(
            data,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=False,
            strip_comments=True)

    def complete_href_attributes(url, data):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        document = html.fromstring(data)
        for a in document.xpath("//a"):
            href = a.get("href")
            if href:
                complete_url = UtilityUri.join_url(url, href)
                a.set("href", complete_url)
        for tag in ("audio", "img", "source", "video"):
            for elm in document.xpath(f"//{tag}"):
                src = elm.get("src")
                if src:
                    complete_url = UtilityUri.join_url(url, src)
                    elm.set("src", complete_url)
        return html.tostring(document, encoding="unicode")

    def remove_html_tags(data: str) -> str:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        parser = etree.HTMLParser()
        tree = etree.fromstring(data, parser)
        cleared = etree.tostring(tree, encoding="unicode", method="text")
        result = cleared.replace("\n\n", "\n")
        return result

    # /questions/9662346/python-code-to-remove-html-tags-from-a-string
    def _remove_html_tags(text):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        import xml.etree.ElementTree
        logger.debug(f"{function_name}		Finish")
        data = "".join(xml.etree.ElementTree.fromstring(text).itertext())
        return data

    def __remove_html_tags(data):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        from bs4 import BeautifulSoup
        data = BeautifulSoup(data, "lxml").text
        data = data.replace("\n\n", "\n")
        logger.debug(f"{function_name}		Finish")
        return data

    def parse(data: str):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        tree = html.fromstring(data)
        formatted_text = []
        links = []
        for element in tree.iter():
            text_parts = []
            for sub_element in element.iterchildren():
                if sub_element.tag == "a":
                    link_text = sub_element.text_content().strip()
                    link_href = sub_element.get("href", "").strip()
                    text_parts.append(f"{link_text}({len(links) + 1})")
                    links.append(f"{len(links) + 1}. {link_href}")
                elif isinstance(sub_element, html.HtmlElement):
                    text_parts.append(sub_element.text_content().strip())
            if text_parts: formatted_text.append(' '.join(text_parts))
        return "\n".join(formatted_text) + "\n\n" + "\n".join(links)
