#!/usr/bin/python
# -*- coding: utf-8 -*-

import asyncio
import datetime
from slixmpp.stanza.iq import Iq
from slixfeed.utility.logger import UtilityLogger
from slixfeed.version import __version__
import sys
#import xml.etree.ElementTree as ET
import lxml.etree as ET

logger = UtilityLogger(__name__)

xmlns = {
    "atom" : "{http://www.w3.org/2005/Atom}",
    "xml"  : "{http://www.w3.org/XML/1998/namespace}"}

class ParserAtom:

    #def activity_stream(data):
    #    """Extract data from an Atom Activity Stream document."""

    # TODO atom:source
    # NOTE Rename "atom_to_dict"
    async def syndication_format(data: ET._ElementTree | ET._XSLTResultTree) -> dict:
        """Extract data from an Atom Syndication Format (RFC 4287) document."""
        #
        #jid = iq["from"].bare
        #node = iq["pubsub"]["items"]["node"]
        #title = jid
        #subtitle = node
        #language = iq["pubsub"]["items"]["lang"]
        #items = iq["pubsub"]["items"]
        # Directive [::-1] reverses the order of the list.
        #for item in list(items)[::-1]:
        #data = item["payload"]
        #

        atom = {}

        atom["feed"] = {}

        root_elem = data.getroot()

        # Extract feed base URI (xml:base)
        atom["feed"]["base"] = root_elem.attrib.get(xmlns["xml"] + "base", "")

        # Extract feed language (xml:lang)
        atom["feed"]["language"] = root_elem.attrib.get(xmlns["xml"] + "lang", "")

        for cont in ("title", "subtitle"):
            elem_cont = data.find(xmlns["atom"] + cont)
            atom["feed"][cont] = {"lang" : "", "text" : "", "type" : ""}
            if elem_cont is not None:
                atom["feed"][cont]["text"] = elem_cont.text
                for attrib in ("base", "lang", "type"):
                    if attrib in elem_cont.attrib:
                        atom["feed"][cont][attrib] = elem_cont.attrib[attrib]

        elem_links = data.findall(xmlns["atom"] + "link")
        atom["feed"]["links"] = []
        for elem_link in elem_links:
            link = {"href" : "", "hreflang" : "", "length" : "", "rel" : "", "title" : "", "type" : ""}
            for attrib in ("href", "hreflang", "length", "rel", "title", "type"):
                if attrib in elem_link.attrib:
                    link[attrib] = elem_link.attrib[attrib]
            atom["feed"]["links"].append(link)

        for graphics in ("icon", "logo"):
            atom["feed"][graphics] = ""
            elem_graphics = data.find(xmlns["atom"] + graphics)
            if elem_graphics is not None:
                atom["feed"][graphics] = elem_graphics.text

        for date in ("published", "updated"):
            atom["feed"][date] = ""
            elem_date = data.find(xmlns["atom"] + date)
            if elem_date is not None:
                atom["feed"][date] = elem_date.text

        elem_categories = data.findall(xmlns["atom"] + "category")
        atom["feed"]["categories"] = []
        for elem_category in elem_categories:
            category = {"label" : "", "scheme" : "", "term" : ""}
            for attrib in ("label", "scheme", "term"):
                if attrib in elem_category.attrib and elem_category.attrib[attrib]:
                    category["term"] = elem_category.attrib[attrib]
                    atom["feed"]["categories"].append(category)

        for people in ("author", "contributor"):
            peoples = f"{people}s"
            atom["feed"][peoples] = []
            elem_peoples = data.findall(xmlns["atom"] + people)
            for elem_people in elem_peoples:
                people = {"email" : "", "name" : "", "uri" : ""}
                for prop in ("email", "name", "uri"):
                    elem_prop = elem_people.find(xmlns["atom"] + prop)
                    if elem_prop is not None:
                        people[prop] = elem_prop.text
                atom["feed"][peoples].append(people)

        atom["entries"] = []

        for elem_entry in data.findall(xmlns["atom"] + "entry"):

            entry = {}

            #elem_title = elem_entry.find(xmlns["atom"] + "title")
            #entry["title"] = "No title" if elem_title == None else elem_title.text
            #entry["title"] = "No title" if elem_title is None else elem_title.text
            #entry["title"] = elem_title.text if elem_title is not None else "No title"

            elem_titl = elem_entry.find(xmlns["atom"] + "title")
            entry["title"] = {"lang" : "", "text" : "", "type" : ""}
            if elem_titl is not None:
                entry["title"]["text"] = elem_titl.text
                for attrib in ("lang", "type"):
                    if attrib in elem_titl.attrib:
                        entry["title"][attrib] = elem_titl.attrib[attrib]

            for cont in ("content", "summary"):
                elem_cont = elem_entry.find(xmlns["atom"] + cont)
                entry[cont] = {"base" : "", "lang" : "", "text" : "", "type" : ""}
                if elem_cont is not None:
                    entry[cont]["text"] = elem_cont.text
                    for attrib in ("base", "lang", "type"):
                        if attrib in elem_cont.attrib:
                            entry[cont][attrib] = elem_cont.attrib[attrib]
                            if cont == "content" and "src" in elem_cont.attrib:
                                entry[cont][attrib] = elem_cont.attrib[attrib]

            elem_links = elem_entry.findall(xmlns["atom"] + "link")
            entry["links"] = []
            for elem_link in elem_links:
                link = {"href" : "", "hreflang" : "", "length" : "", "rel" : "", "title" : "", "type" : ""}
                for attrib in ("href", "hreflang", "length", "rel", "title", "type"):
                    if attrib in elem_link.attrib:
                        link[attrib] = elem_link.attrib[attrib]
                entry["links"].append(link)

            for date in ("published", "updated"):
                entry[date] = ""
                elem_date = elem_entry.find(xmlns["atom"] + date)
                if elem_date is not None:
                    entry[date] = elem_date.text

            for people in ("author", "contributor"):
                peoples = f"{people}s"
                entry[peoples] = []
                elem_peoples = elem_entry.findall(xmlns["atom"] + people)
                for elem_people in elem_peoples:
                    people = {"email" : "", "name" : "", "uri" : ""}
                    for prop in ("email", "name", "uri"):
                        elem_prop = elem_people.find(xmlns["atom"] + prop)
                        if elem_prop is not None:
                            people[prop] = elem_prop.text
                    entry[peoples].append(people)

            elem_categories = elem_entry.findall(xmlns["atom"] + "category")
            entry["categories"] = []
            for elem_category in elem_categories:
                category = {"label" : "", "scheme" : "", "term" : ""}
                for attrib in ("label", "scheme", "term"):
                    if attrib in elem_category.attrib and elem_category.attrib[attrib]:
                        category["term"] = elem_category.attrib[attrib]
                        entry["categories"].append(category)

            elem_id = elem_entry.find(xmlns["atom"] + "id")
            if elem_id is not None:
                entry["id"] = elem_id.text

            atom["entries"].append(entry)

            if len(atom["entries"]) > 9: break

            await asyncio.sleep(0)

        return atom

    # generate_rfc_4287
    def document(atom: dict, link=None):
        """Generate an Atom Syndication Format (RFC 4287) from a Publish-Subscribe (XEP-0060) node items."""
        # link = XmppUtilities.form_a_node_link(pubsub, node)
        # subtitle = "XMPP PubSub Syndication Feed"
        description = ("This is a syndication feed generated with Slixfeed, an "
                       "automated publishing system for XMPP.")
        e_feed = ET.Element("feed")
        e_feed.set("xmlns", "http://www.w3.org/2005/Atom")
        ET.SubElement(e_feed, "icon").text = atom["icon"]
        ET.SubElement(e_feed, "title", {"type": "text"}).text = atom["title"]
        ET.SubElement(e_feed, "subtitle", {"type": "text"}).text = atom["subtitle"]
        for link in atom["links"]:
            ET.SubElement(e_feed, "link", {"type": link["type"],
                                           "rel": link["rel"],
                                           "href": link["href"]})
        ET.SubElement(e_feed, "generator", {"uri": "https://git.xmpp-it.net/sch/Slixfeed",
                                            "version": f"{__version__}"}).text = "Slixfeed"
        ET.SubElement(e_feed, "updated").text = datetime.datetime.now(datetime.UTC).isoformat()
        for item in atom["items"]:
            e_entry = ET.SubElement(e_feed, "entry")
            ET.SubElement(e_entry, "title").text = item["title"]
            links = item["links"] if "links" in item else None
            if links:
                for item_link in links:
                    linkd = {"href" : item_link[2],
                             "rel"  : item_link[4],
                             "type" : item_link[3]} # Perhaps it is index #5
                    ET.SubElement(e_entry, "link", {"href" : linkd["href"],
                                                    "rel"  : linkd["rel"],
                                                    "type" : linkd["type"]})
            #link_xmpp = XmppUtilities.form_an_item_link(pubsub, node, item["id"])
            #ET.SubElement(e_entry, "link", {"href": link_xmpp,
            #                                "rel": "alternate",
            #                                "type": "x-scheme-handler/xmpp"})
            contents = item["contents"] if "contents" in item else None
            if contents:
                for content in contents:
                    contentd = {"type" : content[3],
                                "text" : content[2],
                                "link" : content[4]}
                    ET.SubElement(e_entry, "content", {"type": contentd["type"]}).text = contentd["text"]
            summary = item["summary"]
            if summary:
                summaryd = {"type" : "", # TODO
                            "text" : item["summary"],
                            "link" : ""}
                ET.SubElement(e_entry, "summary", {"type": summaryd["type"]}).text = summaryd["text"]
            ET.SubElement(e_entry, "published").text = item["published"]
            ET.SubElement(e_entry, "updated").text = item["updated"]
            authors = item["authors"] if "authors" in item else None
            if authors:
                for author in authors:
                    authord = {"email" : author[4],
                               "name"  : author[2],
                               "uri"   : author[3]}
                    e_author = ET.SubElement(e_entry, "author")
                    if authord["email"]:
                        ET.SubElement(e_author, "email").text = authord["email"]
                    if authord["uri"]:
                        ET.SubElement(e_entry, "uri").text = authord["uri"]
                        ET.SubElement(e_author, "uri").text = authord["uri"]
                    ET.SubElement(e_author, "name").text = authord["name"] or authord["uri"] or authord["email"]
            categories = item["categories"]
            if categories:
                for category in categories:
                    ET.SubElement(e_entry, "category", {"term": category[2]})

            ET.SubElement(e_entry, "id").text = item["id"]
        xslt_reference = ET.ProcessingInstruction(
            "xml-stylesheet",
            "type=\"text/xml\" href=\"/xslt/atom.xsl\"")
        e_feed.addprevious(xslt_reference)
        xml_data = ET.ElementTree(e_feed)
        xml_data_bytes = ET.tostring(xml_data, pretty_print=True,
                                     xml_declaration=True, encoding="utf-8")
        xml_data_str = xml_data_bytes.decode("utf-8")
        return xml_data_str

    def transform(filename_atom, filename_xslt):
        dom = ET.parse(filename_atom)
        xslt_stylesheet = ET.parse(filename_xslt)
        xslt_transform = ET.XSLT(xslt_stylesheet)
        newdom = xslt_transform(dom)
        xml_data_bytes = ET.tostring(newdom, pretty_print=True)
        xml_data_str = xml_data_bytes.decode("utf-8")
        return xml_data_str
