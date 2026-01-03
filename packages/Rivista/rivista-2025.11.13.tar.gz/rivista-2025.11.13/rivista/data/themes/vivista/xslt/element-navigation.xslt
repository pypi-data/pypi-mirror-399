<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template creates an element for navigation. -->
    <xsl:template name="element-navigation">
        <xsl:param name="entry-count"/>
        <xsl:param name="previous"/>
        <xsl:param name="proceed"/>
        <nav class="navigation-posts">
            <xsl:if test="$previous">
                <span class="navigation-previous">
                    <xsl:element name="a" rel="prev">
                        <xsl:attribute name="href">
                            <xsl:value-of select="$previous/@href"/>
                        </xsl:attribute>
                        <xsl:attribute name="title">
                            <xsl:value-of select="$previous/@title"/>
                        </xsl:attribute>
                        <xsl:text>&lt; Previous</xsl:text>
                    </xsl:element>
                </span>
            </xsl:if>
            <xsl:if test="$proceed">
                <span class="navigation-proceed">
                    <xsl:element name="a" rel="next">
                        <xsl:attribute name="href">
                            <xsl:value-of select="$proceed/@href"/>
                        </xsl:attribute>
                        <xsl:attribute name="title">
                            <xsl:value-of select="$proceed/@title"/>
                        </xsl:attribute>
                        <xsl:text>Proceed &gt;</xsl:text>
                    </xsl:element>
                </span>
            </xsl:if>
        </nav>
    </xsl:template>
</xsl:stylesheet>
