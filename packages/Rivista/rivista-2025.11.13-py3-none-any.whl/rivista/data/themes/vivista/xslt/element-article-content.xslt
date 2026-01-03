<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:geo="http://www.w3.org/2003/01/geo/wgs84_pos#"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template creates an XHTML entry, based on properties, content, and related resources. -->
    <xsl:template name="element-article-content">
        <xsl:param name="atom"/>
        <xsl:comment>
            <xsl:text>Document entry - BEGIN</xsl:text>
        </xsl:comment>
        <article class="entry h-entry">
            <section class="metadata">
                <!-- Authors -->
                <xsl:call-template name="elements-name">
                    <xsl:with-param name="tag" select="'span'"/>
                    <xsl:with-param name="people" select="atom:author"/>
                    <xsl:with-param name="role" select="'author'"/>
                    <xsl:with-param name="preamble" select="'Written by'"/>
                </xsl:call-template>
                <!-- Dates -->
                <span class="dates">
                    <xsl:call-template name="element-published">
                        <xsl:with-param name="timestamp" select="atom:published"/>
                    </xsl:call-template>
                    <xsl:call-template name="element-updated">
                        <xsl:with-param name="timestamp" select="atom:updated"/>
                    </xsl:call-template>
                </span>
                <!-- Contributors -->
                <xsl:call-template name="elements-name">
                    <xsl:with-param name="tag" select="'div'"/>
                    <xsl:with-param name="people" select="atom:contributor"/>
                    <xsl:with-param name="role" select="'contributor'"/>
                    <xsl:with-param name="preamble" select="'In association with'"/>
                </xsl:call-template>
            </section>
            <!-- Graphics -->
            <table class="graphics">
                <tr>
                    <!-- Avatar -->
                    <xsl:variable name="link-avatar" select="atom:link[@rel='avatar']"/>
                    <xsl:if test="$link-avatar">
                        <td>
                            <xsl:comment>
                                <xsl:text>Entry link (avatar)</xsl:text>
                            </xsl:comment>
                            <xsl:call-template name="element-image">
                                <xsl:with-param name="alt" select="$link-avatar/@title"/>
                                <xsl:with-param name="class" select="'avatar'"/>
                                <xsl:with-param name="src" select="$link-avatar/@href"/>
                                <xsl:with-param name="title" select="$link-avatar/@title"/>
                                <xsl:with-param name="type" select="$link-avatar/@type"/>
                            </xsl:call-template>
                        </td>
                    </xsl:if>
                    <!-- Figure -->
                    <xsl:variable name="link-photo" select="atom:link[@rel='photo']"/>
                    <xsl:if test="$link-photo">
                        <td>
                            <xsl:comment>
                                <xsl:text>Entry link (photo)</xsl:text>
                            </xsl:comment>
                            <xsl:call-template name="element-figure">
                                <xsl:with-param name="alt" select="$link-photo/@title"/>
                                <xsl:with-param name="class" select="'photo'"/>
                                <xsl:with-param name="src" select="$link-photo/@href"/>
                                <xsl:with-param name="title" select="$link-photo/@title"/>
                                <xsl:with-param name="type" select="$link-photo/@type"/>
                            </xsl:call-template>
                        </td>
                    </xsl:if>
                </tr>
            </table>
            <!-- iframe -->
            <xsl:variable name="link-iframe" select="atom:link[@rel='iframe']"/>
            <xsl:if test="$link-iframe">
                <iframe>
                    <xsl:attribute name="title">
                        <xsl:value-of select="$link-iframe/@title"/>
                    </xsl:attribute>
                    <xsl:attribute name="src">
                        <xsl:value-of select="$link-iframe/@href"/>
                    </xsl:attribute>
                    <xsl:comment>
                        <xsl:text>Entry link (iframe)</xsl:text>
                    </xsl:comment>
                </iframe>
            </xsl:if>
            <!-- Content -->
            <xsl:if test="string-length(atom:content) &gt; 0">
                <xsl:comment>
                    <xsl:text>Entry content</xsl:text>
                </xsl:comment>
                <section class="content e-content">
                    <xsl:attribute name="type">
                        <xsl:value-of select="atom:content/@type"/>
                    </xsl:attribute>
                    <xsl:copy-of select="atom:content"/>
                </section>
            </xsl:if>
            <!-- Terms -->
            <xsl:call-template name="element-terms">
                <xsl:with-param name="text" select="atom:rights"/>
            </xsl:call-template>
            <!-- Tags -->
            <xsl:call-template name="element-tags">
                <xsl:with-param name="category" select="atom:category"/>
            </xsl:call-template>
            <!-- Enclosures -->
            <xsl:call-template name="elements-link-enclosure">
                <xsl:with-param name="links-enclosure" select="atom:link[@rel='enclosure']"/>
            </xsl:call-template>
            <!-- Microsummaries -->
            <xsl:call-template name="elements-a">
                <xsl:with-param name="elements" select="atom:link[@rel='microsummary']"/>
                <xsl:with-param name="kind" select="'microsummary'"/>
                <xsl:with-param name="kind-plural" select="'microsummaries'"/>
                <xsl:with-param name="name" select="'Microsummary'"/>
                <xsl:with-param name="name-plural" select="'Microsummaries'"/>
                <xsl:with-param name="routine" select="'Microsummary'"/>
            </xsl:call-template>
            <!-- Related -->
            <xsl:call-template name="elements-a">
                <xsl:with-param name="elements" select="atom:link[@rel='related']"/>
                <xsl:with-param name="kind" select="'related'"/>
                <xsl:with-param name="kind-plural" select="'relations'"/>
                <xsl:with-param name="name" select="'Related'"/>
                <xsl:with-param name="name-plural" select="'Related'"/>
                <xsl:with-param name="routine" select="'Related'"/>
            </xsl:call-template>
            <!-- Discussions -->
            <xsl:call-template name="elements-a">
                <xsl:with-param name="elements" select="atom:link[@rel='replies']"/>
                <xsl:with-param name="kind" select="'replies'"/>
                <xsl:with-param name="kind-plural" select="'discussions'"/>
                <xsl:with-param name="name" select="'Replies'"/>
                <xsl:with-param name="name-plural" select="'Discussions'"/>
                <xsl:with-param name="routine" select="'🗨️ Comments'"/>
            </xsl:call-template>
            <!-- Mediums -->
            <h4>Mediums</h4>
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
            <!-- Location -->
            <xsl:choose>
                <xsl:when test="geo:lat and geo:long">
                    <xsl:variable name="lat" select="geo:lat"/>
                    <xsl:variable name="lng" select="geo:long"/>
                    <span class="geolocation p-location">
                        <a href="geo:{$lat},{$lng}">📍</a>
                    </span>
                </xsl:when>
                <xsl:when test="geo:Point">
                    <xsl:variable name="lat" select="geo:Point/geo:lat"/>
                    <xsl:variable name="lng" select="geo:Point/geo:long"/>
                    <span class="geolocation p-location">
                        <a href="geo:{$lat},{$lng}">📍</a>
                    </span>
                </xsl:when>
            </xsl:choose>
        </article>
        <xsl:comment>
            <xsl:text>Document entry - END</xsl:text>
        </xsl:comment>
    </xsl:template>
</xsl:stylesheet>
