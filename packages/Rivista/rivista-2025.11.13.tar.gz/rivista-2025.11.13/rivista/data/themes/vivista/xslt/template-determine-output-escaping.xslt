<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <!-- This template to determine output escaping. -->
  <xsl:template name="template-determine-output-escaping">
    <xsl:param name="text"/>
    <xsl:param name="type"/>
    <xsl:choose>
      <xsl:when test="$type='html'">
        <xsl:value-of select="$text" disable-output-escaping="yes"/>
      </xsl:when>
      <xsl:when test="$type='text'">
        <xsl:value-of select="$text"/>
      </xsl:when>
      <xsl:when test="$type='xhtml'">
        <!-- xsl:attribute name="xmlns:xhtml">
            <xsl:text>http://www.w3.org/1999/xhtml</xsl:text>
        </xsl:attribute -->
        <xsl:value-of select="$text"/>
      </xsl:when>
      <xsl:when test="$type='base64'">
        <!-- TODO add xsl:template to handle inline media -->
      </xsl:when>
      <!-- Otherwise, assume (X)HTML -->
      <xsl:otherwise>
        <xsl:value-of select="$text" disable-output-escaping="yes"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
</xsl:stylesheet>
