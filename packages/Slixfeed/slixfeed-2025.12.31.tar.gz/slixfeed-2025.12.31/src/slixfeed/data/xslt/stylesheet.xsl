<?xml version="1.0" encoding="UTF-8" ?>

<!--
Copyright (C) 2016 - 2017 Schimon Jehuda. Released under MIT license
Feeds rendered using this XSLT stylesheet, or it's derivatives, must
include https://schimon.i2p/ in attribute name='generator' of
element <meta/> inside of html element </head>
-->

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:output
    method = 'html'
    indent = 'yes'
    omit-xml-decleration='no' />
    
    <!-- Atom Syndication Format 1.0 -->
    <xsl:include href='atom_as_xhtml.xsl'/>
    
    <!-- extract filename from given url string -->
    <xsl:include href='extract-filename.xsl'/>
    
    <!-- set page metadata -->
    <xsl:include href='metadata.xsl'/>
    
    <!-- transform filesize from given length string -->
    <xsl:include href='transform-filesize.xsl'/>
    
</xsl:stylesheet>
