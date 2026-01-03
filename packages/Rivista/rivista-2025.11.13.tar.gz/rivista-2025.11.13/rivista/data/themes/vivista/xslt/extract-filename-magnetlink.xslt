<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This templates extracts filename from a given Magnet Link URI string. -->
    <xsl:template name="extract-filename-magnetlink">
        <xsl:param name="uri"/>
        <!--
        ISSUE

        Success
        magnet:?xt=urn:btih:a19bd084c09c0a3824d2449135dacc5589050ae0&dn=Kademlia.A.Peer-to-peer.Information.System.Based.on.the.XOR.Metric.pdf

        Failure
        magnet:?xt=urn:btih:a19bd084c09c0a3824d2449135dacc5589050ae0&dn=Kademlia.A.Peer-to-peer.Information.System.Based.on.the.XOR.Metric.pdf&xl=81047
        -->
        <!-- xsl:if test="contains($uri, 'dn=')" -->
            <xsl:variable name="uri" select="substring-after($uri,'&amp;dn=')"/>
        <!-- /xsl:if -->
        <xsl:choose>
            <xsl:when test="contains($uri,'&amp;')">
                <xsl:call-template name="extract-filename-magnetlink">
                    <xsl:with-param name="uri" select="substring-before($uri,'&amp;')"/>
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$uri"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>
