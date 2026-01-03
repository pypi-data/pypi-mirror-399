<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template creates an element for navigation menu (table of contents). -->
    <xsl:template name="element-menu">
        <xsl:param name="links"/>
        <xsl:param name="type"/>
        <xsl:if test="count($links) &gt; 1">
            <xsl:comment>
                <xsl:text>Table of contents - BEGIN</xsl:text>
            </xsl:comment>
            <section id="menu">
                <details>
                    <summary>
                        <xsl:text>Listing </xsl:text>
                        <xsl:value-of select="count($links)"/>
                        <xsl:value-of select="$type"/>
                    </summary>
                    <ol>
                        <xsl:for-each select="$links">
                            <li>
                                <a>
                                    <xsl:attribute name="href">
                                        <xsl:text>#</xsl:text>
                                        <xsl:value-of select="atom:id"/>
                                    </xsl:attribute>
                                    <xsl:choose>
                                        <xsl:when test="string-length(atom:title) &gt; 0">
                                            <xsl:value-of select="atom:title"/>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <xsl:text>*** No Title ***</xsl:text>
                                        </xsl:otherwise>
                                    </xsl:choose>
                              </a>
                            </li>
                        </xsl:for-each>
                    </ol>
                </details>
            </section>
            <xsl:comment>
                <xsl:text>Table of contents - END</xsl:text>
            </xsl:comment>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
