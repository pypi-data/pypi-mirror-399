<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template extracts entry link enclosure. -->
    <xsl:include href="extract-filename.xslt"/>
    <xsl:include href="extract-filename-ed2k.xslt"/>
    <xsl:include href="extract-filename-magnetlink.xslt"/>
    <xsl:include href="transform-filesize.xslt"/>
    <xsl:template name="elements-link-enclosure">
        <xsl:param name="links-enclosure"/>
        <xsl:if test="$links-enclosure">
            <xsl:comment>
                <xsl:text>Entry link (enclosure) - BEGIN</xsl:text>
            </xsl:comment>
            <section class="enclosures">
                <details>
                    <summary>
                        <xsl:text>Enclosures (</xsl:text>
                        <xsl:value-of select="count($links-enclosure)"/>
                        <xsl:text>)</xsl:text>
                    </summary>
                    <div>
                        <xsl:for-each select="$links-enclosure">
                            <div class="enclosure">
                                <xsl:attribute name="type">
                                    <xsl:value-of select="@type"/>
                                </xsl:attribute>
                                <xsl:element name="a">
                                    <xsl:attribute name="download">
                                        <xsl:choose>
                                            <xsl:when test="starts-with(@href, 'magnet:')">
                                                <xsl:call-template name="extract-filename-magnetlink">
                                                    <xsl:with-param name="uri" select="@href"/>
                                                </xsl:call-template>
                                            </xsl:when>
                                            <xsl:when test="starts-with(@href, 'ed2k:')">
                                                <xsl:call-template name="extract-filename-ed2k">
                                                    <xsl:with-param name="uri" select="@href"/>
                                                </xsl:call-template>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:call-template name="extract-filename">
                                                    <xsl:with-param name="uri" select="@href"/>
                                                </xsl:call-template>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </xsl:attribute>
                                    <xsl:attribute name="href">
                                        <xsl:value-of select="@href"/>
                                    </xsl:attribute>
                                    <xsl:choose>
                                        <xsl:when test="string-length(@title) &gt; 0">
                                            <xsl:value-of select="@title"/>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <xsl:choose>
                                                <xsl:when test="starts-with(@href, 'magnet:')">
                                                    <xsl:call-template name="extract-filename-magnetlink">
                                                        <xsl:with-param name="uri" select="@href"/>
                                                    </xsl:call-template>
                                                </xsl:when>
                                                <xsl:when test="starts-with(@href, 'ed2k:')">
                                                    <xsl:call-template name="extract-filename-ed2k">
                                                        <xsl:with-param name="uri" select="@href"/>
                                                    </xsl:call-template>
                                                </xsl:when>
                                                <xsl:otherwise>
                                                    <xsl:call-template name="extract-filename">
                                                        <xsl:with-param name="uri" select="@href"/>
                                                    </xsl:call-template>
                                                </xsl:otherwise>
                                            </xsl:choose>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </xsl:element>
                                <xsl:if test="@length &gt; 0">
                                    <xsl:call-template name="transform-filesize">
                                        <xsl:with-param name="length" select="@length"/>
                                    </xsl:call-template>
                                </xsl:if>
                            </div>
                        </xsl:for-each>
                    </div>
                </details>
            </section>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
