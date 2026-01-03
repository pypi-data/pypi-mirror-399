<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template creates an element for links and subsequent elements. -->
    <xsl:template name="elements-a">
        <xsl:param name="elements"/>
        <xsl:param name="kind"/>
        <xsl:param name="kind-plural"/>
        <xsl:param name="name"/>
        <xsl:param name="name-plural"/>
        <xsl:param name="routine"/>
        <xsl:if test="$elements">
            <xsl:comment>
                <xsl:text>Entry link (</xsl:text>
                <xsl:value-of select="$name"/>
                <xsl:text>) - BEGIN</xsl:text>
            </xsl:comment>
            <section>
                <xsl:attribute name="class">
                    <xsl:value-of select="$kind-plural"/>
                </xsl:attribute>
                <details>
                    <summary>
                        <xsl:value-of select="$name-plural"/>
                        <xsl:text> (</xsl:text>
                        <xsl:value-of select="count($elements)"/>
                        <xsl:text>)</xsl:text>
                    </summary>
                    <xsl:for-each select="$elements">
                        <div>
                            <xsl:attribute name="class">
                                <xsl:value-of select="$kind"/>
                            </xsl:attribute>
                            <xsl:attribute name="type">
                                <xsl:value-of select="@type"/>
                            </xsl:attribute>
                            <xsl:element name="a">
                                <xsl:attribute name="href">
                                    <xsl:value-of select="@href"/>
                                </xsl:attribute>
                                <xsl:choose>
                                    <xsl:when test="string-length(@title) &gt; 0">
                                        <xsl:value-of select="@title"/>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:value-of select="$routine"/>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </xsl:element>
                        </div>
                    </xsl:for-each>
                </details>
            </section>
            <xsl:comment>
                <xsl:text>Entry link (</xsl:text>
                <xsl:value-of select="$name"/>
                <xsl:text>) - END</xsl:text>
            </xsl:comment>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
