# Slixfeed - Syndication service of open and standard networks

Slixfeed is a news aggregation service (i.e. "bot", so called) of open and
standard telecommunication networks (OSTN);

It provides a convenient and immediate access to journals, publications, torrent
indexers, and otherwise syndicated contents.

The purpose of this service is to be ubiquitous and easy to operate with chat
software.

Slixfeed is primarily designed to XMPP, yet it is built to be extended to other
networks and protocols.

Supported networks are DeltaChat, Gemini, HTTP, and the XMPP communication
network.

# Sponsorship

This project is sponsored by Stichting NLnet.

<img alt="Stichting NLnet" src="https://nlnet.nl/logo/banner.svg" width="200px"/>

Stichting NLnet

<img alt="NGI Zero Core" src="https://nlnet.nl/image/logos/NGI0Core_tag.svg" width="200px"/>

NGI Zero Core

# Features

* Automatic detection of syndication feeds by scanning a given URL;
* Messages are encrypted by the standard encryption system OMEMO;
* Articles may be downloaded as EPUB, Markdown, and (X)HTML;
* The Atom Syndication Format (RFC 4287) as a universal document format;
* Other formats (Gemini, JSON, RDF, RSS, Twtxt, et cetera) are supported by Focuscript;
* Filtering of news items by utilizing lists of allow and deny;
* Displaying enclosures (audio, document, picture, and video files) inline;
* Exporting and importing of feeds with OPML or XBEL;
* Forwarding of publications as Atomsub (Atom Over XMPP);
* Simultaneous management of multiple accounts, including group chats; and
* An interactive visual interface (XMPP).

# Preview

monocles chat

<img alt="Chat: Add URL" src="slixfeed/documentation/screenshots/chat_add_url.png" width="200px"/>
<img alt="Ad-Hoc: Commands" src="slixfeed/documentation/screenshots/adhoc_commands.png" width="200px"/>

<!-- ![Chat: Add URL](slixfeed/documentation/screenshots/chat_add_url.png) ![Ad-Hoc: Commands](slixfeed/documentation/screenshots/adhoc_commands.png) -->

Cheogram

<img alt="Ad-Hoc: Add URL" src="slixfeed/documentation/screenshots/adhoc_add_url.png" width="200px"/>
<img alt="Ad-Hoc: Settings" width="200px" src="slixfeed/documentation/screenshots/adhoc_settings.png"/>

<!-- ![Ad-Hoc: Add URL](slixfeed/documentation/screenshots/adhoc_add_url.png) ![Ad-Hoc: Preview URL](slixfeed/documentation/screenshots/adhoc_preview_url.png) ![Ad-Hoc: Settings](slixfeed/documentation/screenshots/adhoc_settings.png) -->

# Instructions

## Install

It is possible to install Slixfeed with pip or pipx.

### pip (inside a container)

Create a virtual environment.

```
$ python3 -m venv .venv
$ source .venv/bin/activate
```

Install.

```
$ pip install git+https://git.xmpp-it.net/sch/Slixfeed
```

Install Slixfeed with support of OMEMO.

```
$ pip install git+https://git.xmpp-it.net/sch/Slixfeed[omemo]
```

### pipx

Install.

```
$ pipx install git+https://git.xmpp-it.net/sch/Slixfeed
```

Update.

```
$ pipx uninstall slixfeed
$ pipx install git+https://git.xmpp-it.net/sch/Slixfeed
```

# Slixfeed

Configure an account of the service.

```
$ slixfeed-setup --interface xmpp --address <ADDRESS> --password <PASSWORD>
```

Set policy to allow all interactions.

```
$ slixfeed-setup --policy allow
```

Start service.

```
$ slixfeed-server
```

# Usage

* Add the contact to your roster and follow its instructions.
* Send command `help` for a list of commands.

# Appproval mechanism

The approval mechanism allows to allow or deny services to specified addresses,
hostnames, and TLDs.

## Allow

Allow any account.

## Deny

Deny account by specified values, unless subject account is allowed.

## Blacklist

Deny accounts by specified values.

## Whitelist

Allow accounts by specified values.

# Focuscript

Automated.

```
$ slixfeed-focuscript auto <URI of a document>
```

Manual.

```
$ slixfeed-focuscript <Pathname of a Focuscript or XSLT stylesheet> <URI of a document>
```

# Recommended chat clients

Slixfeed works with any XMPP chat client; if you want to utilize the visual
interface of Slixfeed, then you are advised to install software which support
XEP-0050: Ad-Hoc Commands.

* [Cheogram](https://cheogram.com)
* [Converse](https://conversejs.org)
* [Gajim](https://gajim.org)
* [LeechCraft](https://leechcraft.org/plugins-azoth-xoox)
* [monocles chat](https://monocles.chat)
* [Movim](https://mov.im)
* [Poezio](https://poez.io)
* [Psi](https://psi-im.org)

# Support

Please join to our group chats, whether you want to discuss of new features,
need help, or just greet us.

* [Main Group Chat](xmpp:slixfeed@chat.woodpeckersnest.space?join) (International)
* [Deutsche Chat Gruppe](xmpp:slixfeed@conference.miharu.dedyn.io?join) (German)

# Authors

* [Schimon](xmpp:sch@pimux.de?message) (Author).
* [Laura](xmpp:lauranna@404.city?message) (Co-Author, Instructor and Mentor).

# Contributors

Mr. Stephen Paul Weber from Sopranica who has provided code for Data Forms to be
used as visual interface with Ad-Hoc Commands, and who has taught me about Data
Forms.

* [Stephen Paul Weber](https://singpolyma.net)
* [Sopranica](https://soprani.ca)

# Thanks

Mr. Guus der Kinderen from Ignite Realtime who has provided Openfire servers of
GoodBytes.

* [GoodBytes](http://goodbytes.nl)
* [Ignite Realtime](https://igniterealtime.org)
* [Openfire](https://igniterealtime.org/projects/openfire/)

Mr. Simone "roughnecks" Canaletti from "Wood Peckers Nest" who has provided a
Movim instance.

* gemini://woodpeckersnest.space
* https://woodpeckersnest.space

# Acknowledgment

Special thank you to Mrs. Lapina who instructed me during months to complete
this, in addition to significant code fixes.

Laura, I thank you greatly for your encouragement, time and help.
This software would not have existed without you.

May this software be a life changing factor to people the world over.

# Licenses

MIT license.

Some XMPP modules are licensed under AGPL3 license.

# Copyright

Schimon Zackary (2022 - 2026)

Laura Lapina (2022 - 2025)

# Similar Projects

Please visit our friends who offer different approaches to convey syndication
feeds to XMPP.

## AtomToPubsub

Syndication feeds as XMPP Pubsub Nodes.

* https://github.com/edhelas/atomtopubsub
* https://github.com/imattau/atomtopubsub

## err-rssreader

A port of old Brutal's RSS Reader to Errbot.

* https://github.com/errbotters/err-rssreader

## feed-to-muc

An XMPP service which posts to a group chat if there is an update in newsfeeds.

* https://salsa.debian.org/mdosch/feed-to-muc

## Jabber RSS Transport

Syndication feeds as contacts.

* https://jabberworld.info/Jabber_RSS_Transport

## Fun With Jabber: Headline Delivery with RSS

This is probably the first news service software of XMPP.

* http://pipetree.com/jabber/headlines.html

## JabRSS

Never miss a headline again! JabRSS is a simple syndication headline
notification service of Jabber/XMPP.

* http://www.jotwewe.de/de/xmpp/jabrss/jabrss_en.htm
* https://dev.cmeerw.org/Projects/jabrss

## Janchor

Janchor Headline Service. It was originally inspired by DJ Adam's headline
Delivery service, as written in his series of Articles Fun With Jabber.

* http://janchor.jabberstudio.org

## Mimír

Mimír is a Jabber enabled news service. It collects news from various sources
and notifies its users when new news items have been found or holds them for
later reading, based on their presence. With Mimír you can be kept up-to-date to
the latest news from several sources.

* http://mimir.ik.nu

## Morbot

Morbo is a simple Slixmpp service that will take new articles from listed
syndication feeds and send them to assigned XMPP group chats.

* https://codeberg.org/TheCoffeMaker/Morbot

## XMPP Bot

An XMPP service for making the link between XMPP conversations and webhooks.

* https://github.com/nioc/xmpp-bot
