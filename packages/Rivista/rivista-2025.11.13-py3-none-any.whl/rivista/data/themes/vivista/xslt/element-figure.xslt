<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template creates element figure. -->
    <xsl:template name="element-figure">
        <xsl:param name="alt"/>
        <xsl:param name="class"/>
        <xsl:param name="id"/>
        <xsl:param name="src"/>
        <xsl:param name="title"/>
        <xsl:param name="type"/>
        <figure>
            <xsl:attribute name="class">
                <xsl:value-of select="$class"/>
            </xsl:attribute>
            <xsl:attribute name="id">
                <xsl:value-of select="$id"/>
            </xsl:attribute>
            <xsl:element name="img">
                <xsl:attribute name="alt">
                    <xsl:value-of select="$alt"/>
                </xsl:attribute>
                <xsl:attribute name="src">
                    <xsl:value-of select="$src"/>
                </xsl:attribute>
                <!-- xsl:attribute name="title">
                    <xsl:value-of select="$title"/>
                </xsl:attribute -->
                <xsl:attribute name="type">
                    <xsl:value-of select="$type"/>
                </xsl:attribute>
            </xsl:element>
            <figcaption>
                <p>
                    <xsl:value-of select="$title"/>
                </p>
            </figcaption>
        </figure>
    </xsl:template>
</xsl:stylesheet>
