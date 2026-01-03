<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template extracts entry people. -->
    <xsl:template name="elements-name">
        <xsl:param name="tag"/>
        <xsl:param name="people"/>
        <xsl:param name="role"/>
        <xsl:param name="preamble"/>
        <xsl:if test="$people">
            <xsl:element name="{$tag}">
                <xsl:attribute name="class">
                    <xsl:value-of select="$role"/>
                    <xsl:text>s</xsl:text>
                </xsl:attribute>
                <xsl:comment>
                    <xsl:text>Entry $role</xsl:text>
                </xsl:comment>
                <xsl:value-of select="$preamble"/>
                <xsl:text> </xsl:text>
                <xsl:for-each select="$people">
                    <span>
                        <xsl:attribute name="class">
                            <xsl:value-of select="$role"/>
                            <xsl:text> p-</xsl:text>
                            <xsl:value-of select="$role"/>
                            <xsl:text> h-card</xsl:text>
                        </xsl:attribute>
                        <xsl:choose>
                            <xsl:when test="atom:email">
                                <xsl:element name="a">
                                    <xsl:attribute name="href">
                                        <xsl:text>mailto:</xsl:text>
                                            <xsl:value-of select="atom:email"/>
                                    </xsl:attribute>
                                    <xsl:attribute name="title">
                                        <xsl:text>Send an Email to </xsl:text>
                                        <xsl:value-of select="atom:email"/>
                                    </xsl:attribute>
                                    <xsl:value-of select="atom:name"/>
                                </xsl:element>
                            </xsl:when>
                            <xsl:when test="atom:uri">
                                <xsl:element name="a">
                                    <xsl:attribute name="href">
                                        <xsl:value-of select="atom:uri"/>
                                    </xsl:attribute>
                                    <xsl:attribute name="title">
                                        <xsl:value-of select="atom:summary"/>
                                    </xsl:attribute>
                                    <xsl:value-of select="atom:name"/>
                                </xsl:element>
                            </xsl:when>
                            <xsl:when test="atom:name">
                                <xsl:value-of select="atom:name"/>
                            </xsl:when>
                            <xsl:when test="atom:uri">
                                <xsl:value-of select="atom:uri"/>
                            </xsl:when>
                        </xsl:choose>
                    </span>
                </xsl:for-each>
            </xsl:element>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
