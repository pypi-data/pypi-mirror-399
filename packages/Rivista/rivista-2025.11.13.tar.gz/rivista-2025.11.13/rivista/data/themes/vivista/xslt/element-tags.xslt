<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template creates an element for tags and subsequent elements. -->
    <xsl:template name="element-tags">
        <xsl:param name="category"/>
        <xsl:if test="$category">
            <xsl:comment>
                <xsl:text>Entry category - BEGIN</xsl:text>
            </xsl:comment>
            <section class="tags">
                <details open="">
                    <summary>
                        <xsl:text>Tags (</xsl:text>
                        <xsl:value-of select="count($category)"/>
                        <xsl:text>)</xsl:text>
                    </summary>
                    <div>
                        <xsl:for-each select="$category">
                            <xsl:if test="@term">
                                <a class="p-category">
                                    <xsl:if test="@scheme">
                                        <xsl:attribute name="href">
                                            <xsl:value-of select="@scheme"/>
                                            <xsl:text>/</xsl:text>
                                            <xsl:value-of select="@term"/>
                                        </xsl:attribute>
                                    </xsl:if>
                                    <xsl:choose>
                                        <xsl:when test="@label">
                                            <xsl:value-of select="@label"/>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <xsl:value-of select="@term"/>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </a>
                            </xsl:if>
                        </xsl:for-each>
                    </div>
                </details>
            </section>
            <xsl:comment>
                <xsl:text>Entry category - END</xsl:text>
            </xsl:comment>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
