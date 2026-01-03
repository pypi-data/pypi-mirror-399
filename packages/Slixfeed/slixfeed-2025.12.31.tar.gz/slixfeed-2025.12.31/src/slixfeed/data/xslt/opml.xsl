<?xml version="1.0" encoding="UTF-8" ?>

<!--
Copyright (C) 2016 - 2024 Schimon Jehuda. Released under MIT license
Feeds rendered using this XSLT stylesheet, or it's derivatives, must
include https://schimon.i2p/ in attribute name='generator' of
element <meta/> inside of html element </head>
-->

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output encoding = 'UTF-8'
                indent = 'yes'
                media-type = 'text/x-opml'
                method = 'html'
                version = '4.01' />
    <!-- Outline Processor Markup Language 1.0 -->
    <xsl:include href='opml_as_xhtml.xsl'/>
    <!-- set page metadata -->
    <xsl:include href='metadata.xsl'/>
</xsl:stylesheet>
