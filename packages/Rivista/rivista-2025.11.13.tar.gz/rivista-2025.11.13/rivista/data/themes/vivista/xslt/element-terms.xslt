<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template creates an element for terms. -->
    <xsl:template name="element-terms">
        <xsl:param name="text"/>
        <xsl:if test="string-length($text) &gt; 0">
            <xsl:comment>
                <xsl:text>Entry rights - BEGIN</xsl:text>
            </xsl:comment>
            <details>
                <summary>
                    <xsl:text>Terms</xsl:text>
                </summary>
                <section class="terms">
                    <xsl:value-of select="$text"/>
                </section>
            </details>
            <xsl:comment>
                <xsl:text>Entry rights - END</xsl:text>
            </xsl:comment>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
