<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This templates creates an XHTML entry based on its title and summary. -->
    <xsl:template name="element-article-summary">
        <xsl:param name="atom"/>
        <xsl:comment>
            <xsl:text>Document entry - BEGIN</xsl:text>
        </xsl:comment>
        <article class="entry h-entry">
            <xsl:attribute name="id">
                <xsl:value-of select="atom:id"/>
            </xsl:attribute>
            <!-- Entry title -->
            <xsl:element name="a">
                <xsl:attribute name="href">
                    <xsl:choose>
                        <xsl:when test="atom:link[@rel='self']">
                            <xsl:value-of select="atom:link[@rel='self']/@href"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="atom:link/@href"/>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:attribute>
                <xsl:call-template name="element-text">
                    <xsl:with-param name="class" select="'title p-name'"/>
                    <xsl:with-param name="name" select="'title'"/>
                    <xsl:with-param name="routine" select="'Untitled'"/>
                    <xsl:with-param name="tag" select="'h3'"/>
                    <xsl:with-param name="text" select="atom:title"/>
                </xsl:call-template>
            </xsl:element>
            <!-- Date -->
            <span>📅 </span>
            <xsl:call-template name="element-published">
                 <xsl:with-param name="timestamp" select="atom:published"/>
            </xsl:call-template>
            <!-- Summary -->
            <xsl:if test="string-length(atom:summary) &gt; 0">
                <xsl:comment>
                    <xsl:text>Entry summary</xsl:text>
                </xsl:comment>
                <section class="summary p-summary">
                    <xsl:attribute name="type">
                        <xsl:value-of select="atom:summary/@type"/>
                    </xsl:attribute>
                    <xsl:copy-of select="atom:summary"/>
                </section>
            </xsl:if>
            <!-- Mediums -->
            <section class="mediums">
                <!-- TODO Send a message to author -->
                <!-- TODO Print article -->
                <!-- TODO Send article by Email-->
                <xsl:if test="atom:link[@rel='replies' and contains(@type, 'html')]">
                    <xsl:comment>
                        <xsl:text>Entry link (replies)</xsl:text>
                    </xsl:comment>
                    <xsl:for-each select="atom:link[@rel='replies' and contains(@type, 'html')]">
                        <xsl:call-template name="entry-link-replies">
                            <xsl:with-param name="link" select="atom:link"/>
                            <xsl:with-param name="title" select="'🗨️ Comments'"/>
                        </xsl:call-template>
                    </xsl:for-each>
                </xsl:if>
                <xsl:call-template name="entry-alternate-scheme">
                    <xsl:with-param name="atom" select="atom"/>
                    <xsl:with-param name="scheme" select="'ed2k:'"/>
                    <xsl:with-param name="title" select="'🐴 eD2k'"/>
                </xsl:call-template>
                <xsl:call-template name="entry-alternate-scheme">
                    <xsl:with-param name="atom" select="atom"/>
                    <xsl:with-param name="scheme" select="'ftp:'"/>
                    <xsl:with-param name="title" select="'🗄 FTP'"/>
                </xsl:call-template>
                <xsl:call-template name="entry-alternate-scheme">
                    <xsl:with-param name="atom" select="atom"/>
                    <xsl:with-param name="scheme" select="'gemini:'"/>
                    <xsl:with-param name="title" select="'♊ Gemini'"/>
                </xsl:call-template>
                <xsl:call-template name="entry-alternate-scheme">
                    <xsl:with-param name="atom" select="atom"/>
                    <xsl:with-param name="scheme" select="'gopher:'"/>
                    <xsl:with-param name="title" select="'🦦 Gopher'"/>
                </xsl:call-template>
                <xsl:call-template name="entry-alternate-scheme">
                    <xsl:with-param name="atom" select="atom"/>
                    <xsl:with-param name="scheme" select="'magnet:'"/>
                    <xsl:with-param name="title" select="'🧲 Magnet'"/>
                </xsl:call-template>
                <xsl:call-template name="entry-alternate-type">
                    <xsl:with-param name="atom" select="atom"/>
                    <xsl:with-param name="type" select="'atom'"/>
                    <xsl:with-param name="title" select="'📶 RSS'"/>
                </xsl:call-template>
                <xsl:call-template name="entry-alternate-scheme">
                    <xsl:with-param name="atom" select="atom"/>
                    <xsl:with-param name="scheme" select="'xmpp:'"/>
                    <xsl:with-param name="title" select="'💡 XMPP'"/>
                </xsl:call-template>
            </section>
        </article>
        <xsl:comment>
            <xsl:text>Document entry - END</xsl:text>
        </xsl:comment>
    </xsl:template>
</xsl:stylesheet>
