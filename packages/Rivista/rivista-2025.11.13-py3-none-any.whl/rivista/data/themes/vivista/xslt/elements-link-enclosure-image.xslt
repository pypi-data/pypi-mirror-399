<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template realizes graphical enclosure as image. -->
    <xsl:template name="elements-link-enclosure-image">
        <xsl:param name="atom"/>
        <xsl:param name="links-enclosure"/>
        <xsl:if test="$links-enclosure">
            <xsl:comment>
                <xsl:text>Entry link (enclosure) - BEGIN</xsl:text>
            </xsl:comment>
            <div class="images">
                <xsl:for-each select="$links-enclosure">
                    <xsl:variable name="title" select="@title"/>
                    <xsl:if test="//atom:link[@rel='related' and @title=$title]">
                        <div class="image">
                            <xsl:element name="a">
                                <xsl:attribute name="href">
                                    <xsl:value-of select="//atom:link[@rel='related' and @title=$title]/@href"/>
                                </xsl:attribute>
                                <xsl:element name="img">
                                    <xsl:attribute name="alt">
                                        <xsl:value-of select="$title"/>
                                    </xsl:attribute>
                                    <xsl:attribute name="src">
                                        <xsl:value-of select="@href"/>
                                    </xsl:attribute>
                                </xsl:element>
                                <span>
                                    <xsl:value-of select="$title"/>
                                </span>
                            </xsl:element>
                        </div>
                    </xsl:if>
                </xsl:for-each>
            </div>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
