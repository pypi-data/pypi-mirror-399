#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Functions create_node and create_entry are derived from project atomtopubsub.

"""

import asyncio
import hashlib
from slixfeed.interface.xmpp.disco import XmppServiceDiscovery
from slixfeed.interface.xmpp.iq import XmppIQ
from slixfeed.syndication import Feed
from slixfeed.utility.account import accounts
from slixfeed.utility.atom import UtilityAtom
from slixfeed.utility.logger import UtilityLogger
from slixfeed.sqlite.general import SQLiteGeneral
from slixfeed.utility.task import UtilityTask
from slixfeed.utility.text import UtilityText
import slixmpp.plugins.xep_0060.stanza.pubsub as pubsub
from slixmpp.xmlstream import ET
import sys

logger = UtilityLogger(__name__)

class XmppPubsub:

    async def get_pubsub_services(xmpp_instance):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        results = []
        try:
            iq = await XmppServiceDiscovery.retrieve_items(xmpp_instance,
                                                           xmpp_instance.boundjid.domain)
        except Exception as e:
            iq = None
            print(xmpp_instance.boundjid.domain)
            print(e)
        if iq:
            items = iq["disco_items"]["items"]
            for item in items:
                try:
                    iq = await XmppServiceDiscovery.retrieve_information(
                        xmpp_instance, item[0])
                except Exception as e:
                    print(item[0])
                    print(e)
                identities = iq["disco_info"]["identities"]
                for identity in identities:
                    if identity[0] == "pubsub" and identity[1] == "service":
                        result = {}
                        result["jid"] = item[0]
                        if item[1]: result["name"] =  item[1]
                        elif item[2]: result["name"] = item[2]
                        else: result["name"] = item[0]
                        results.append(result)
        return results

    async def get_node_properties(xmpp_instance, jid_bare, node):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        logger.debug(f"{function_name}	{jid_bare}	{node}")
        config = await xmpp_instance.plugin["xep_0060"].get_node_config(jid_bare, node)
        subscriptions = await xmpp_instance.plugin["xep_0060"].get_node_subscriptions(jid_bare,
                                                                                      node)
        affiliations = await xmpp_instance.plugin["xep_0060"].get_node_affiliations(jid_bare,
                                                                                    node)
        properties = {
            "config": config,
            "subscriptions": subscriptions,
            "affiliations": affiliations}
        breakpoint()
        return properties

    async def get_node_configuration(xmpp_instance, jid_bare, node_id):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        logger.debug(f"{function_name}	{jid_bare}	Node ID {node_id}")
        node = await xmpp_instance.plugin["xep_0060"].get_node_config(jid_bare,
                                                                      node_id)
        return node

    async def get_nodes(xmpp_instance, jid_bare):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        nodes = await xmpp_instance.plugin["xep_0060"].get_nodes(jid_bare)
        # "xmpp_instance" would lead to slixmpp.jid.InvalidJID: idna validation failed:
        return nodes

    async def get_item(xmpp_instance, jid_bare, node, item_id):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        logger.debug(f"{function_name}	{jid_bare}	Node {node}; Item ID {item_id}")
        item = await xmpp_instance.plugin["xep_0060"].get_item(jid_bare, node,
                                                               item_id)
        return item

    async def get_items(xmpp_instance, jid_bare, node):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        logger.debug(f"{function_name}	{jid_bare}	Node {node}")
        items = await xmpp_instance.plugin["xep_0060"].get_items(jid_bare, node)
        return items

    def delete_node(xmpp_instance, jid_bare, node):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        logger.debug(f"{function_name}	{jid_bare}	Node {node}")
        jid_from = xmpp_instance.boundjid.bare if xmpp_instance.is_component else None
        xmpp_instance.plugin["xep_0060"].delete_node(jid_bare, node,
                                                     ifrom=jid_from)

    def purge_node(xmpp_instance, jid_bare, node):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        logger.debug(f"{function_name}	{jid_bare}	Node {node}")
        jid_from = xmpp_instance.boundjid.bare if xmpp_instance.is_component else None
        xmpp_instance.plugin["xep_0060"].purge(jid_bare, node, ifrom=jid_from)
        # iq = xmpp_instance.Iq(stype="set",
        #              sto=jid_bare,
        #              sfrom=jid_from)
        # iq["pubsub"]["purge"]["node"] = node
        # return iq

    def create_node(xmpp_instance, jid_bare, node, title=None, subtitle=None):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        logger.debug(f"{function_name}	{jid_bare}	Node {node}")
        jid_from = xmpp_instance.boundjid.bare if xmpp_instance.is_component else None
        iq = xmpp_instance.Iq(stype="set", sto=jid_bare, sfrom=jid_from)
        iq["pubsub"]["create"]["node"] = node
        form = iq["pubsub"]["configure"]["form"]
        form["type"] = "submit"
        form.addField("pubsub#title",
                      ftype="text-single",
                      value=title)
        form.addField("pubsub#description",
                      ftype="text-single",
                      value=subtitle)
        form.addField("pubsub#notify_retract",
                      ftype="boolean",
                      value=1)
        form.addField("pubsub#max_items",
                      ftype="text-single",
                      value="50")
        form.addField("pubsub#persist_items",
                      ftype="boolean",
                      value=1)
        form.addField("pubsub#send_last_published_item",
                      ftype="text-single",
                      value="never")
        form.addField("pubsub#deliver_payloads",
                      ftype="boolean",
                      value=0)
        form.addField("pubsub#type",
                      ftype="text-single",
                      value="http://www.w3.org/2005/Atom")
        return iq

    # TODO Consider to create a separate function called "create_atom_entry"
    # or "create_rfc4287_entry" for anything related to variable "node_entry".
    def create_entry(xmpp_instance, jid_bare, node_id, item_id, node_item):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        logger.debug(f"{function_name}	{jid_bare}	Node ID {node_id}; Item ID {item_id}")
        iq = xmpp_instance.Iq(stype="set", sto=jid_bare)
        iq["pubsub"]["publish"]["node"] = node_id

        item = pubsub.Item()

        # From atomtopubsub:
        # character / is causing a bug in movim. replacing : and , with - in id.
        # It provides nicer urls.
        
        # Respond to atomtopubsub:
        # I think it would be beneficial to use md5 checksum of Url as Id for
        # cross reference, and namely - in another project to utilize PubSub as
        # links sharing system (see del.icio.us) - to share node entries.

        item["id"] = item_id
        item["payload"] = node_item
        iq["pubsub"]["publish"].append(item)
        return iq

    def _create_entry(xmpp_instance, jid_bare, node, entry, version):
        iq = xmpp_instance.Iq(stype="set", sto=jid_bare)
        iq["pubsub"]["publish"]["node"] = node
        item = pubsub.Item()
        # From atomtopubsub:
        # character / is causing a bug in movim. replacing : and , with - in id.
        # It provides nicer urls.
        
        # Respond to atomtopubsub:
        # I think it would be beneficial to use md5 checksum of Url as Id for
        # cross reference, and namely - in another project to utilize PubSub as
        # links sharing system (see del.icio.us) - to share node entries.

        # NOTE Warning: Entry might not have a link
        # TODO Handle situation error
        url_encoded = entry.link.encode()
        url_hashed = hashlib.md5(url_encoded)
        url_digest = url_hashed.hexdigest()
        item["id"] = url_digest + "_html"
        node_entry = ET.Element("entry")
        node_entry.set("xmlns", "http://www.w3.org/2005/Atom")
        title = ET.SubElement(node_entry, "title")
        title.text = entry.title
        updated = ET.SubElement(node_entry, "updated")
        updated.text = entry.updated
        # Content
        if version == "atom03":
            if hasattr(entry.content[0], "type"):
                content = ET.SubElement(node_entry, "content")
                content.set("type", entry.content[0].type)
                content.text = entry.content[0].value
        elif version =="rss20" or "rss10" or "atom10":
            if hasattr(entry, "content"):
                content = ET.SubElement(node_entry, "content")
                content.set("type", "text/html")
                content.text = entry.content[0].value
            elif hasattr(entry, "description"):
                content = ET.SubElement(node_entry,"content")
                content.set("type", "text/html")
                content.text = entry.description
                print("In Description - PublishX")
        # Links
        if hasattr(entry, "links"):
            for l in entry.links:
                link = ET.SubElement(node_entry, "link")
                if hasattr(l, "href"):
                    link.set("href", l["href"])
                    link.set("type", l["type"])
                    link.set("rel", l["rel"])
                elif hasattr(entry, "link"):
                    link.set("href", entry["link"])
        # Tags
        if hasattr(entry, "tags"):
            for t in entry.tags:
                tag = ET.SubElement(node_entry, "category")
                tag.set("term", t.term)
        # Categories
        if hasattr(entry,"category"):
            for c in entry["category"]:
                cat = ET.SubElement(node_entry, "category")
                cat.set("category", entry.category[0])
        # Authors
        if version == "atom03":
            if hasattr(entry, "authors"):
                author = ET.SubElement(node_entry, "author")
                name = ET.SubElement(author, "name")
                name.text = entry.authors[0].name
                if hasattr(entry.authors[0], "href"):
                    uri = ET.SubElement(author, "uri")
                    uri.text = entry.authors[0].href
        elif version == "rss20" or "rss10" or "atom10":
            if hasattr(entry, "author"):
                author = ET.SubElement(node_entry, "author")
                name = ET.SubElement(node_entry, "author")
                name.text = entry.author
                if hasattr(entry.author, "href"):
                    uri = ET.SubElement(author, "uri")
                    uri.text = entry.authors[0].href
        item["payload"] = node_entry
        iq["pubsub"]["publish"].append(item)
        return iq

    # FIXME Do not declare node_id twice
    async def send_selected_entry(xmpp_instance, jid_bare, node_id, entry_id):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        logger.debug(f"{function_name}	{jid_bare}	Node ID {node_id}; Entry ID {entry_id}")
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        feed_id = SQLiteGeneral.get_feed_id_by_entry_index(db_file, entry_id)
        feed_id = feed_id[0]
        node_id, node_title, node_subtitle = SQLiteGeneral.get_feed_properties(db_file,
                                                                        feed_id)
        iq_create_node = XmppPubsub.create_node(xmpp_instance, jid_bare,
                                                node_id, node_title,
                                                node_subtitle)
        await XmppIQ.send(iq_create_node)
        entry = SQLiteGeneral.get_entry_properties(db_file, entry_id)
        entry_dict = Feed.pack_entry_into_dict(db_file, entry)
        node_item = UtilityAtom.create_rfc4287_entry(entry_dict)
        item_id = UtilityText.md5sum(entry_dict["link"])
        iq_create_entry = XmppPubsub.create_entry(
            xmpp_instance, jid_bare, node_id, item_id, node_item)
        await XmppIQ.send(iq_create_entry)
        await SQLiteGeneral.mark_as_read(db_file, entry_id)
        
        # NOTE This value is returned for the sake of testing
        return entry_dict["link"]

    async def publish_unread_items(xmpp_instance, jid_bare):
        """

        Parameters
        ----------
        jid_bare : str
            Bare Jabber ID.

        Returns
        -------
        None.

        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        config_account = accounts.retrieve(jid_bare)
        db_file = config_account.database
        subscriptions = SQLiteGeneral.get_active_feeds_url(db_file)
        # Iterate subscriptions.
        for subscription in subscriptions:
            url = subscription[0]
            # feed_id = SQLiteGeneral.get_feed_id(db_file, url)
            # feed_id = feed_id[0]
            # feed_properties = SQLiteGeneral.get_feed_properties(db_file, feed_id)
            feed_id = SQLiteGeneral.get_feed_id(db_file, url)
            feed_id = feed_id[0]
            # Publish to node based on feed identifier for PubSub service.
            # node_id = feed_properties[2]
            # node_title = feed_properties[3]
            # node_subtitle = feed_properties[5]
            node_id = SQLiteGeneral.get_feed_identifier(db_file, feed_id)
            # Set node name (i.e. node id) of given subscription.
            if not node_id:
                counter = 0
                while True:
                    identifier = UtilityText.identifier(url, counter)
                    if SQLiteGeneral.check_identifier_exist(db_file, identifier):
                        counter += 1
                    else:
                        break
                await SQLiteGeneral.update_feed_identifier(db_file, feed_id,
                                                           identifier)
                node_id = SQLiteGeneral.get_feed_identifier(db_file, feed_id)
            node_title = SQLiteGeneral.get_feed_title(db_file, feed_id)
            node_subtitle = SQLiteGeneral.get_feed_subtitle(db_file, feed_id)
            #node_exist = await XmppPubsub.get_node_configuration(xmpp_instance, jid_bare, node_id)
            nodes = await XmppPubsub.get_nodes(xmpp_instance, jid_bare)
            node_items = nodes["disco_items"]["items"]
            node_exist = False
            for node_item in node_items:
                if node_item[1] == node_id:
                    node_exist = True
                    break
            if not node_exist:
                try:
                    iq_create_node = XmppPubsub.create_node(xmpp_instance,
                                                            jid_bare, node_id,
                                                            node_title,
                                                            node_subtitle)
                    result = await XmppIQ.send(iq_create_node)
                except Exception as e:
                    print("Please do not close this console and contact the developer.")
                    print(e)
                    breakpoint()
                    result_condition = result.iq["error"]["condition"]
                    if result_condition in ("forbidden", "service-unavailable"):
                        reason = result.iq["error"]["text"]
                        logger.error(f"{function_name}	{jid_bare}	Creation of node {node_id} has failed: {reason}")
                        return
            # Iterate entries and publish them to the respective node.
            entries = SQLiteGeneral.get_unread_entries_of_feed(db_file, feed_id)
            for entry in entries:
                feed_entry = Feed.pack_entry_into_dict(db_file, entry)
                node_entry = UtilityAtom.create_rfc4287_entry(feed_entry)
                entry_url = feed_entry["link"]
                item_id = UtilityText.md5sum(entry_url)
                logger.info(f"{function_name}	{jid_bare}	PubSub node item was sent to Node ID {node_id}; Item ID: {item_id}; URL: {entry_url}")
                iq_create_entry = XmppPubsub.create_entry(xmpp_instance,
                                                          jid_bare, node_id,
                                                          item_id, node_entry)
                result = await XmppIQ.send(iq_create_entry)
                ix = entry[0]
                await SQLiteGeneral.mark_as_read(db_file, ix)
        logger.info(f"{function_name}	{jid_bare}	Finish")

class XmppPubsubTask:

    async def looper(xmpp_instance, jid_bare):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        while True:
            await XmppPubsub.publish_unread_items(xmpp_instance, jid_bare)
            await asyncio.sleep(60 * 120)

    def restart_task(xmpp_instance, jid_bare):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{jid_bare}	Start")
        config_account = accounts.retrieve(jid_bare)
        UtilityTask.stop(config_account.tasks_manager, "publish")
        config_account.tasks_manager["publish"] = asyncio.create_task(
            XmppPubsubTask.looper(xmpp_instance, jid_bare))
        logger.debug(f"{function_name}	{jid_bare}	Finish")
