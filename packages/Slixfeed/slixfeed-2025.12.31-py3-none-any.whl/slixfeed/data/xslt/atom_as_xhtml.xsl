<?xml version="1.0" encoding="UTF-8" ?>

<!--
Copyright (C) 2016 - 2024 Schimon Jehuda. Released under MIT license
Feeds rendered using this XSLT stylesheet, or it's derivatives, must
include https://schimon.i2p/ in attribute name='generator' of
element <meta/> inside of html element </head>
-->

<xsl:stylesheet version='1.0' 
xmlns:xsl='http://www.w3.org/1999/XSL/Transform'
xmlns:xml='http://www.w3.org/XML/1998/namespace'
xmlns:media='http://search.yahoo.com/mrss/'
xmlns:georss='http://www.georss.org/georss'
xmlns:geo='http://www.w3.org/2003/01/geo/wgs84_pos#'
xmlns:atom10='http://www.w3.org/2005/Atom'
xmlns:atom='http://www.w3.org/2005/Atom'>
    <xsl:template match='/atom:feed'>
        <!-- index right-to-left language codes -->
        <!-- TODO http://www.w3.org/TR/xpath/#function-lang -->
        <xsl:variable name='rtl'
        select='@xml:lang[
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
                    <xsl:with-param name='content' select='atom:subtitle' />
                </xsl:call-template>
                <xsl:call-template name='metadata'>
                    <xsl:with-param name='name' select='"generator"' />
                    <xsl:with-param name='content' select='Slixfeed' />
                </xsl:call-template>
                <xsl:call-template name='metadata'>
                    <xsl:with-param name='name' select='"mimetype"' />
                    <xsl:with-param name='content' select='"application/atom+xml"' />
                </xsl:call-template>
                <title>
                    <xsl:choose>
                        <xsl:when test='atom:title and not(atom:title="") and count(atom:entry) &gt; 1'>
                            <xsl:value-of select='atom:title'/>
                        </xsl:when>
                        <xsl:when test='atom:entry'>
                            <xsl:value-of select='atom:entry/atom:title'/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:text>Slixfeed</xsl:text>
                        </xsl:otherwise>
                    </xsl:choose>
                </title>
                <!-- xsl:element name='base'>
                    <xsl:attribute name='href'>
                        <xsl:choose>
                            <xsl:when test='atom:link[@rel="self"]'>
                                <xsl:value-of select='atom:link[@rel="self"]/@href'/>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of select='atom:link/@href'/>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:attribute>
                </xsl:element -->
                <link href='?xml' rel='alternate' title='Atom Syndication Feed' type='application/atom+xml' />
                <link href='/graphic/xmpp.svg' rel='icon' type='image/svg+xml' />
                <!-- TODO media='print' -->
                <link href='/css/stylesheet.css' media='screen' rel='stylesheet' type='text/css' />
                <!-- whether language code is of direction right-to-left -->
                <xsl:if test='$rtl'>
                    <link href='/css/stylesheet-rtl.css' id='semitic' rel='stylesheet' type='text/css' />
                </xsl:if>
            </head>
            <body>
                <div id='actions'>
                    <a id='follow' title='Subscribe the latest updates and news.'
                       onclick='window.open(location.href.replace(/^https?:/, "feed:"), "_self")'>
                        <!-- xsl:attribute name="href">
                            feed:<xsl:value-of select="atom:link[@rel='self']/@href" />
                        </xsl:attribute -->
                        Follow
                    </a>
                    <a id='subtome' title='Subscribe via SubToMe.'>
                        <xsl:attribute name='href'>
                            javascript:location.href='https://www.subtome.com/#/subscribe?feeds='+location.href;
                        </xsl:attribute>
                        <xsl:attribute name='onclick'>
                            (
                                function(btn){
                                    var z=document.createElement('script');
                                    document.subtomeBtn=btn;
                                    z.src='https://www.subtome.com/load.js';document.body.appendChild(z);
                                }
                            )(this);
                            return false;
                        </xsl:attribute>
                        <xsl:text>SubToMe</xsl:text>
                    </a>
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
                                <xsl:when test='atom:title and not(atom:title="") and count(atom:entry) &gt; 1'>
                                    <xsl:value-of select='atom:title'/>
                                </xsl:when>
                                <xsl:when test='atom:entry'>
                                    <xsl:value-of select='atom:entry/atom:title'/>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:text>No title</xsl:text>
                                </xsl:otherwise>
                            </xsl:choose>
                        </h1>
                        <!-- feed subtitle -->
                        <h2 id='subtitle'>
                            <xsl:choose>
                                <xsl:when test='atom:title and not(atom:title="") and count(atom:entry) &gt; 1'>
                                    <xsl:value-of select='atom:subtitle'/>
                                </xsl:when>
                                <xsl:when test='atom:entry'>
                                    <xsl:attribute name='class'>
                                        <xsl:text>date</xsl:text>
                                    </xsl:attribute>
                                    <xsl:value-of select='atom:entry/atom:updated'/>
                                </xsl:when>
                                <xsl:when test='atom:entry'>
                                    <xsl:attribute name='class'>
                                        <xsl:text>date</xsl:text>
                                    </xsl:attribute>
                                    <xsl:value-of select='atom:entry/atom:published'/>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:text>Slixfeed World News Service</xsl:text>
                                </xsl:otherwise>
                            </xsl:choose>
                        </h2>
                    </div>
                    <xsl:if test='count(atom:entry) &gt; 1'>
                        <div id='menu'>
                           <h3>Latest Posts</h3>
                           <!-- xsl:for-each select='atom:entry[position() &lt;21]' -->
                            <ol>
                                <xsl:for-each select='atom:entry[not(position() &gt; 20)]'>
                                    <li>
                                        <xsl:element name='a'>
                                            <xsl:attribute name='href'>
                                                 <xsl:text>#slixfeed-</xsl:text>
                                                 <xsl:value-of select='position()'/>
                                            </xsl:attribute>
                                            <xsl:choose>
                                                <xsl:when test='string-length(atom:title) &gt; 0'>
                                                    <xsl:value-of select='atom:title'/>
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
                        <!-- feed entry -->
                        <xsl:choose>
                            <xsl:when test='atom:entry'>
                                <ul>
                                    <xsl:for-each select='atom:entry[not(position() >20)]'>
                                        <li>
                                            <div class='entry h-entry'>
                                                <!-- entry title -->
                                                <h3 class='title p-name'>
                                                    <xsl:element name='a'>
                                                        <xsl:attribute name='href'>
                                                            <xsl:choose>
                                                                <xsl:when test='atom:link[@rel="self"]'>
                                                                    <xsl:value-of select='atom:link[@rel="self"]/@href'/>
                                                                </xsl:when>
                                                                <xsl:otherwise>
                                                                    <xsl:value-of select='atom:link/@href'/>
                                                                </xsl:otherwise>
                                                            </xsl:choose>
                                                        </xsl:attribute>
                                                        <xsl:attribute name='id'>
                                                            <xsl:text>slixfeed-</xsl:text>
                                                            <xsl:value-of select='position()'/>
                                                        </xsl:attribute>
                                                        <xsl:choose>
                                                            <xsl:when test='string-length(atom:title) &gt; 0'>
                                                                <xsl:value-of select='atom:title'/>
                                                            </xsl:when>
                                                            <xsl:otherwise>
                                                                <xsl:text>*** No Title ***</xsl:text>
                                                            </xsl:otherwise>
                                                        </xsl:choose>
                                                    </xsl:element>
                                                </h3>
                                                <!-- geographic location -->
                                                <xsl:choose>
                                                    <xsl:when test='geo:lat and geo:long'>
                                                        <xsl:variable name='lat' select='geo:lat'/>
                                                        <xsl:variable name='lng' select='geo:long'/>
                                                        <span class='geolocation p-location'>
                                                            <a href='geo:{$lat},{$lng}'>📍</a>
                                                        </span>
                                                    </xsl:when>
                                                    <xsl:when test='geo:Point'>
                                                        <xsl:variable name='lat' select='geo:Point/geo:lat'/>
                                                        <xsl:variable name='lng' select='geo:Point/geo:long'/>
                                                        <span class='geolocation p-location'>
                                                            <a href='geo:{$lat},{$lng}'>📍</a>
                                                        </span>
                                                    </xsl:when>
                                                    <xsl:when test='georss:point'>
                                                        <xsl:variable name='lat' select='substring-before(georss:point, " ")'/>
                                                        <xsl:variable name='lng' select='substring-after(georss:point, " ")'/>
                                                        <xsl:variable name='name' select='georss:featurename'/>
                                                        <span class='geolocation p-location'>
                                                            <a href='geo:{$lat},{$lng}' title='{$name}'>📍</a>
                                                        </span>
                                                    </xsl:when>
                                                </xsl:choose>
                                                <!-- entry date -->
                                                <xsl:element name='h4'>
                                                    <xsl:choose>
                                                        <xsl:when test='atom:updated'>
                                                            <xsl:attribute name='class'>
                                                                <xsl:text>updated dt-updated</xsl:text>
                                                            </xsl:attribute>
                                                            <xsl:value-of select='atom:updated'/>
                                                        </xsl:when>
                                                        <xsl:when test='atom:published'>
                                                            <xsl:attribute name='class'>
                                                                <xsl:text>published dt-published</xsl:text>
                                                            </xsl:attribute>
                                                            <xsl:value-of select='atom:published'/>
                                                        </xsl:when>
                                                        <xsl:otherwise>
                                                            <h4 class='warning atom1 published'></h4>
                                                        </xsl:otherwise>
                                                    </xsl:choose>
                                                </xsl:element>
                                                <!-- entry author -->
                                                <xsl:if test='atom:author'>
                                                    <h4 class='author h-card p-author'>
                                                        <xsl:text>By </xsl:text>
                                                        <xsl:choose>
                                                            <xsl:when test='atom:author/atom:email'>
                                                                <xsl:element name='a'>
                                                                    <xsl:attribute name='href'>
                                                                        <xsl:text>mailto:</xsl:text>
                                                                           <xsl:value-of select='atom:author/atom:email'/>
                                                                    </xsl:attribute>
                                                                    <xsl:attribute name='title'>
                                                                        <xsl:text>Send an Email to </xsl:text>
                                                                        <xsl:value-of select='atom:author/atom:email'/>
                                                                    </xsl:attribute>
                                                                    <xsl:value-of select='atom:author/atom:name'/>
                                                                </xsl:element>
                                                            </xsl:when>
                                                            <xsl:when test='atom:author/atom:uri'>
                                                                <xsl:element name='a'>
                                                                    <xsl:attribute name='href'>
                                                                        <xsl:value-of select='atom:author/atom:uri'/>
                                                                    </xsl:attribute>
                                                                    <xsl:attribute name='title'>
                                                                        <xsl:value-of select='atom:author/atom:summary'/>
                                                                    </xsl:attribute>
                                                                    <xsl:value-of select='atom:author/atom:name'/>
                                                                </xsl:element>
                                                            </xsl:when>
                                                            <xsl:when test='atom:author/atom:name'>
                                                                <xsl:value-of select='atom:author/atom:name'/>
                                                            </xsl:when>
                                                            <xsl:when test='atom:uri'>
                                                                <xsl:value-of select='atom:uri'/>
                                                            </xsl:when>
                                                        </xsl:choose>
                                                    </h4>
                                                </xsl:if>
                                                <h5 class='related'>
                                                    <xsl:if test='atom:link[@rel="alternate" and @type="x-scheme-handler/xmpp"]'>
                                                        <xsl:element name='a'>
                                                            <xsl:attribute name='href'>
                                                                <xsl:value-of select='atom:link[@rel="alternate" and @type="x-scheme-handler/xmpp"]/@href'/>
                                                            </xsl:attribute>
                                                            <xsl:attribute name='class'>
                                                                <xsl:text>slixfeed-jabber</xsl:text>
                                                            </xsl:attribute>
                                                            <xsl:text>💡️ Source</xsl:text>
                                                        </xsl:element>
                                                        <xsl:element name='a'>
                                                            <xsl:attribute name='href'>
                                                                <xsl:value-of select='atom:link[@rel="alternate" and @type="x-scheme-handler/xmpp"]/@href'/>
                                                            </xsl:attribute>
                                                            <xsl:text>(XMPP)</xsl:text>
                                                        </xsl:element>
                                                    </xsl:if>
                                                    <xsl:if test='atom:link[@rel="contact"]'>
                                                        <xsl:element name='a'>
                                                            <xsl:attribute name='href'>
                                                                <xsl:value-of select='atom:link[@rel="contact"]/@href'/>
                                                            </xsl:attribute>
                                                            <xsl:attribute name='class'>
                                                                <xsl:text>contact-uri</xsl:text>
                                                            </xsl:attribute>
                                                            <xsl:text>🪪️ Contact</xsl:text>
                                                        </xsl:element>
                                                    </xsl:if>
                                                    <xsl:if test='atom:link[@rel="replies"]'>
                                                        <xsl:element name='a'>
                                                            <xsl:attribute name='href'>
                                                                <xsl:value-of select='atom:link[@rel="replies"]/@href'/>
                                                            </xsl:attribute>
                                                            <xsl:attribute name='class'>
                                                                <xsl:text>slixfeed-replies</xsl:text>
                                                            </xsl:attribute>
                                                            <xsl:text>💬 Discussion</xsl:text>
                                                        </xsl:element>
                                                        <xsl:element name='a'>
                                                            <xsl:attribute name='href'>
                                                                <xsl:value-of select='atom:link[@rel="replies"]/@href'/>
                                                            </xsl:attribute>
                                                            <xsl:text>(XMPP)</xsl:text>
                                                        </xsl:element>
                                                    </xsl:if>
                                                    <xsl:if test='atom:link[@rel="alternate" and @type="text/html"]'>
                                                        <xsl:element name='a'>
                                                            <xsl:attribute name='href'>
                                                                <xsl:value-of select='atom:link[@rel="alternate" and @type="text/html"]/@href'/>
                                                            </xsl:attribute>
                                                            <xsl:text>📜 HTML</xsl:text>
                                                        </xsl:element>
                                                    </xsl:if>
                                                    <xsl:if test='atom:link[@rel="related" and @type="text/html"]'>
                                                        <xsl:element name='a'>
                                                            <xsl:attribute name='href'>
                                                                <xsl:value-of select='atom:link[@rel="related" and @type="text/html"]/@href'/>
                                                            </xsl:attribute>
                                                            <xsl:text>📜 HTML (Related)</xsl:text>
                                                        </xsl:element>
                                                    </xsl:if>
                                                </h5>
                                                <!-- entry summary -->
                                                <xsl:if test='string-length(atom:summary) &gt; 0'>
                                                    <h4>Summary</h4>
                                                    <div class='summary p-summary'>
                                                        <xsl:choose>
                                                            <xsl:when test='atom:summary[contains(@type,"html")]'>
                                                                <xsl:attribute name='type'>
                                                                    <xsl:value-of select='atom:summary/@type'/>
                                                                </xsl:attribute>
                                                                <xsl:value-of select='atom:summary' disable-output-escaping='yes'/>
                                                            </xsl:when>
                                                            <xsl:when test='atom:summary[contains(@type,"text")]'>
                                                                <xsl:attribute name='type'>
                                                                    <xsl:value-of select='atom:summary/@type'/>
                                                                </xsl:attribute>
                                                                <xsl:value-of select='atom:summary'/>
                                                            </xsl:when>
                                                            <xsl:when test='atom:summary[contains(@type,"base64")]'>
                                                                <!-- TODO add xsl:template to handle inline media -->
                                                            </xsl:when>
                                                            <xsl:otherwise>
                                                                <xsl:value-of select='atom:summary' disable-output-escaping='yes'/>
                                                            </xsl:otherwise>
                                                        </xsl:choose>
                                                    </div>
                                                </xsl:if>
                                                <!-- entry content -->
                                                <xsl:if test='string-length(atom:content) &gt; 0'>
                                                    <h4>Content</h4>
                                                    <div class='content e-content'>
                                                        <xsl:choose>
                                                            <xsl:when test='atom:content[contains(@type,"html")]'>
                                                                <xsl:attribute name='type'>
                                                                    <xsl:value-of select='atom:content/@type'/>
                                                                </xsl:attribute>
                                                                <xsl:value-of select='atom:content' disable-output-escaping='yes'/>
                                                            </xsl:when>
                                                            <xsl:when test='atom:content[contains(@type,"text")]'>
                                                                <xsl:attribute name='type'>
                                                                    <xsl:value-of select='atom:content/@type'/>
                                                                </xsl:attribute>
                                                                <xsl:value-of select='atom:content'/>
                                                            </xsl:when>
                                                            <xsl:when test='atom:content[contains(@type,"base64")]'>
                                                                <!-- TODO add xsl:template to handle inline media -->
                                                            </xsl:when>
                                                            <xsl:otherwise>
                                                                <xsl:value-of select='atom:content' disable-output-escaping='yes'/>
                                                            </xsl:otherwise>
                                                        </xsl:choose>
                                                    </div>
                                                </xsl:if>
                                                <!-- entry tags -->
                                                <xsl:if test='atom:category/@term'>
                                                    <h4>Tags</h4>
                                                    <span class='tags'>
                                                        <xsl:for-each select='atom:category'>
                                                            <xsl:element name='div'>
                                                                <xsl:attribute name='p-category'>
                                                                    <xsl:value-of select='@term'/>
                                                                </xsl:attribute>
                                                            </xsl:element>
                                                        </xsl:for-each>
                                                    </span>
                                                </xsl:if>
                                                <!-- entry enclosure -->
                                                <xsl:if test='atom:link[@rel="enclosure"]'>
                                                    <h4>Media</h4>
                                                    <span class='enclosures' title='Right-click and Save link as…'>
                                                        <xsl:for-each select='atom:link[@rel="enclosure"]'>
                                                            <div class='enclosure' title='Right-click and Save link as…'>
                                                                <xsl:element name='span'>
                                                                    <xsl:attribute name='icon'>
                                                                        <xsl:value-of select='substring-before(@type,"/")'/>
                                                                    </xsl:attribute>
                                                                </xsl:element>
                                                                <xsl:element name='a'>
                                                                    <xsl:attribute name='href'>
                                                                        <xsl:value-of select='@href'/>
                                                                    </xsl:attribute>
                                                                    <xsl:attribute name='download'/>
                                                                    <xsl:call-template name='extract-filename'>
                                                                        <xsl:with-param name='url' select='@href' />
                                                                    </xsl:call-template>
                                                                </xsl:element>
                                                                <xsl:element name='span'>
                                                                    <xsl:attribute name='class'>
                                                                        <xsl:value-of select='substring-before(@type,"/")'/>
                                                                    </xsl:attribute>
                                                                </xsl:element>
                                                                <xsl:if test='@length &gt; 0'>
                                                                    <xsl:call-template name='transform-filesize'>
                                                                        <xsl:with-param name='length' select='@length' />
                                                                    </xsl:call-template>
                                                                </xsl:if>
                                                                <br/>
                                                            </div>
                                                        </xsl:for-each>
                                                    </span>
                                                </xsl:if>
                                            </div>
                                            <!-- entry id -->
                                            <!-- TODO add ID for Microformat u-uid -->
                                            <xsl:if test='not(atom:id)'>
                                                <div class='warning atom1 id'>No entry ID</div>
                                            </xsl:if>
                                        </li>
                                    </xsl:for-each>
                                </ul>
                            </xsl:when>
                            <xsl:otherwise>
                              <ul>
                                <li>
                                  <div class='entry'>
                                    <h3 class='title'>
                                      <a href='javascript:alert("Please check that the mother PubSub node is populated with content.")'>
                                        <xsl:text>No content</xsl:text>
                                      </a>
                                    </h3>
                                    <h4>This entry is empty</h4>
                                    <div class='content'>Please check that the mother PubSub node is populated with content.</div>
                                  </div>
                                </li>
                              </ul>
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
                    This an Atom document which can also be viewed with
                    a Syndication Feed Reader (also referred to as News Reader
                    or RSS Reader) which provides automated news updates and
                    notifications on desktop and mobile.
                    <a href="/help">Click here</a> for a selection of software
                    and pick the ones that would fit to you best!
                </p>
                <p id='small'>
                    <i>
                        This Atom Syndication Format <a href="?xml">document</a>
                        is conveyed as an XHTML document.
                        This document was produced by an XSLT
                        <a href="/xslt/atom.xsl">stylesheet</a>.
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
