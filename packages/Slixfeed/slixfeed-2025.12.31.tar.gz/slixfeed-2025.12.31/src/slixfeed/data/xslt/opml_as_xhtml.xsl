<?xml version="1.0" encoding="UTF-8" ?>

<!--
Copyright (C) 2016 - 2024 Schimon Jehuda. Released under MIT license
Feeds rendered using this XSLT stylesheet, or it's derivatives, must
include https://schimon.i2p/ in attribute name='generator' of
element <meta/> inside of html element </head>
-->

<xsl:stylesheet version='1.0' 
xmlns:xsl='http://www.w3.org/1999/XSL/Transform'
xmlns:xml='http://www.w3.org/XML/1998/namespace'>
    <xsl:template match='/opml'>
        <!-- index right-to-left language codes -->
        <!-- TODO http://www.w3.org/TR/xpath/#function-lang -->
        <xsl:variable name='rtl'
        select='lang[
        contains(self::node(),"ar") or 
        contains(self::node(),"fa") or 
        contains(self::node(),"he") or 
        contains(self::node(),"ji") or 
        contains(self::node(),"ku") or 
        contains(self::node(),"ur") or 
        contains(self::node(),"yi")]'/>
        <html>
            <head>
                <xsl:call-template name='metadata'>
                    <xsl:with-param name='name' select='"description"' />
                    <xsl:with-param name='content' select='subtitle' />
                </xsl:call-template>
                <xsl:call-template name='metadata'>
                    <xsl:with-param name='name' select='"generator"' />
                    <xsl:with-param name='content' select='Slixfeed' />
                </xsl:call-template>
                <xsl:call-template name='metadata'>
                    <xsl:with-param name='name' select='"mimetype"' />
                    <xsl:with-param name='content' select='"text/x-opml"' />
                </xsl:call-template>
                <title>
                    <xsl:choose>
                        <xsl:when test='//head/title and not(//head/title="")'>
                            <xsl:value-of select='//head/title'/>
                        </xsl:when>
                        <xsl:otherwise>Slixfeed OPML</xsl:otherwise>
                    </xsl:choose>
                </title>
                <!-- TODO media='print' -->
                <link rel='stylesheet' type='text/css' media='screen' href='/css/stylesheet.css'/>
                <link rel='icon' type='image/svg+xml' href='/graphic/xmpp.svg'/>
                <!-- whether language code is of direction right-to-left -->
                <xsl:if test='$rtl'>
                    <link id='semitic' href='/css/stylesheet-rtl.css' rel='stylesheet' type='text/css' />
                </xsl:if>
            </head>
            <body>
                <div id='actions'>
                    <a href='https://xmpp.org/about/technology-overview/'
                       title='Of the benefits of XMPP.'>
                        <xsl:text>XMPP</xsl:text>
                    </a>
                    <a href='https://join.jabber.network/#syndication@conference.movim.eu?join'
                       title='Syndictaion and PubSub.'>
                        <xsl:text>Groupchat</xsl:text>
                    </a>
                    <a href='/help'
                       title='Of the benefits of syndication feed.'>
                        <xsl:text>Help</xsl:text>
                    </a>
                </div>
                <div id='feed'>
                    <div id='header'>
                        <!-- feed title -->
                        <h1 id='title'>
                            <xsl:choose>
                                <xsl:when test='//head/title and not(//head/title="") and count(//outline) &gt; 1'>
                                    <xsl:value-of select='//head/title'/>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:text>Slixfeed OPML Collection</xsl:text>
                                </xsl:otherwise>
                            </xsl:choose>
                        </h1>
                        <!-- feed subtitle -->
                        <h2 id='subtitle'>
                            <xsl:choose>
                                <xsl:when test='//head/description and not(//head/description="") and count(//outline) &gt; 1'>
                                    <xsl:value-of select='//head/description'/>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:text>Outline Processor Markup Language</xsl:text>
                                </xsl:otherwise>
                            </xsl:choose>
                        </h2>
                    </div>
                    <xsl:if test='count(//outline) &gt; 1'>
                        <div id='menu'>
                           <h3>Subscriptions</h3>
                           <!-- xsl:for-each select='outline[position() &lt;21]' -->
                            <ol>
                                <xsl:for-each select='//outline[not(position() &gt; 20)]'>
                                    <li>
                                        <xsl:element name='a'>
                                            <xsl:attribute name='href'>
                                                 <xsl:text>#slixfeed-</xsl:text>
                                                 <xsl:value-of select='position()'/>
                                            </xsl:attribute>
                                            <xsl:choose>
                                                <xsl:when test='string-length(@text) &gt; 0'>
                                                    <xsl:value-of select='@text'/>
                                                </xsl:when>
                                                <xsl:otherwise>
                                                    <xsl:text>*** No Title ***</xsl:text>
                                                </xsl:otherwise>
                                            </xsl:choose>
                                      </xsl:element>
                                    </li>
                                </xsl:for-each>
                            </ol>
                        </div>
                    </xsl:if>
                    <div id='articles'>
                        <!-- opml outline -->
                        <xsl:choose>
                            <xsl:when test='//outline'>
                                <ul>
                                    <xsl:for-each select='//outline[not(position() &gt; 20)]'>
                                        <li>
                                            <div class='entry'>
                                                <!-- outline title -->
                                                <h3 class='title'>
                                                    <xsl:element name='a'>
                                                        <xsl:attribute name='href'>
                                                            <xsl:value-of select='@xmlUrl'/>
                                                        </xsl:attribute>
                                                        <xsl:attribute name='id'>
                                                            <xsl:text>slixfeed-</xsl:text>
                                                            <xsl:value-of select='position()'/>
                                                        </xsl:attribute>
                                                        <xsl:choose>
                                                            <xsl:when test='string-length(@text) &gt; 0'>
                                                                <xsl:value-of select='@text'/>
                                                            </xsl:when>
                                                            <xsl:otherwise>
                                                                <xsl:text>*** No Title ***</xsl:text>
                                                            </xsl:otherwise>
                                                        </xsl:choose>
                                                    </xsl:element>
                                                </h3>
                                                <!-- entry content -->
                                                <h4>
                                                    <xsl:value-of select='@text'/>
                                                </h4>
                                                <p class='content'>
                                                    <xsl:value-of select='@xmlUrl'/>
                                                </p>
                                            </div>
                                        </li>
                                    </xsl:for-each>
                                </ul>
                            </xsl:when>
                            <xsl:otherwise>
                                <div class='notice no-entry'></div>
                            </xsl:otherwise>
                        </xsl:choose>
                    </div>
                </div>
                <div id='references'>
                    <a href='https://git.xmpp-it.net/sch/Blasta'
                       title='A Social Bookmark Manager For XMPP.'>
                        <xsl:text>Blasta</xsl:text>
                    </a>
                    <a href='https://libervia.org/'
                       title='The Universal Communication Ecosystem.'>
                        <xsl:text>Libervia</xsl:text>
                    </a>
                    <a href='https://join.movim.eu/'
                       title='The Social Platform Shaped For Your Community.'>
                        <xsl:text>Movim</xsl:text>
                    </a>
                    <a href='https://github.com/SeveFP/Reeder'
                       title='An XMPP-Based Feed Reader.'>
                        <xsl:text>Reeder</xsl:text>
                    </a>
                    <a href='https://git.xmpp-it.net/sch/Rivista'
                       title='A Journal Publisher For XMPP.'>
                        <xsl:text>Rivista</xsl:text>
                    </a>
                    <a href='https://git.xmpp-it.net/sch/Slixfeed'
                       title='A News Service For XMPP.'>
                        <xsl:text>Slixfeed</xsl:text>
                    </a>
                    <a href='https://joinjabber.org/'
                       title='An Inclusive Space On The Jabber Network.'>
                        <xsl:text>JoinJabber</xsl:text>
                    </a>
                    <a href='https://modernxmpp.org/'
                       title='A Project To Improve The Quality Of XMPP Messaging Applications.'>
                        <xsl:text>Modern</xsl:text>
                    </a>
                    <a href='https://xmpp.org/'
                       title='The Universal Messaging Standard.'>
                        <xsl:text>XMPP</xsl:text>
                    </a>
                    <a href='https://xmpp.org/extensions/xep-0060.html'
                       title='XEP-0060: Publish-Subscribe.'>
                        <xsl:text>PubSub</xsl:text>
                    </a>
                </div>
                <!-- note -->
                <p id='note'>
                    This is an OPML document which includes a collection of
                    subscriptions, and it can be imported to
                    a Syndication Feed Reader (also referred to as News Reader
                    or RSS Reader) which provides automated news updates and
                    notifications on desktop and mobile.
                    <a href="/help">Click here</a> for a selection of software
                    and pick the ones that would fit to you best!
                </p>
                <p id='small'>
                    <i>
                        This OPML (Outline Processor Markup Language) collection
                        <a href="?xml">document</a> is conveyed as an XHTML
                        document.
                        This document was produced by an XSLT
                        <a href="/xslt/opml.xsl">stylesheet</a>.
                        XSLT (XSL Transformations) is a technology which
                        transforms XML documents into HTML, JSON, PDF, Plain
                        Text, XHTML, and (modified) XML documents;
                        <a href="https://w3.org/Style/XSL/">Learn more</a> about
                        XSL (Extensible Stylesheet Language).
                    </i>
                </p>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
