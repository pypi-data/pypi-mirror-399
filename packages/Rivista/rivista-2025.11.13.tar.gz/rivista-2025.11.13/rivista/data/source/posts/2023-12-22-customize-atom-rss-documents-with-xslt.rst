.. author:
   name,uri
   Slatian, acct:slatian@pleroma.envs.net
.. contributor:
   name,uri
   Schimon Jehudah Zachary, xmpp:sch@pimux.de?message
.. category:
   label, term, scheme
   The Atom Syndication Format, atom, filetype
   Cascade Style Sheet, css, filetype
   Design, design, concern
   HTML, html, filetype
   RSS, rss, filetype
   Tutorial, tutorial, concern
   Usability, usability, concern
   XHTML, xhtml, filetype
   XPath, xpath, query-language
   XSLT, xslt, computer-language
   XML, xml, technology
.. id: 2023-12-22-customize-atom-rss-documents-with-xslt
.. links:
   title,href,rel
   Pretty Atom-Feed Previews with XSLT, https://slatecave.net/blog/atom-xslt/, related
   Serving and styling XML on the internet, https://blog.saxonica.com/norm/2025/08/21-styling-xml.html, related
.. published: 2023-12-22 00:00:00 UTC
.. summary:
   This is a concise tutorial for adding XSLT stylesheets to Atom Syndication
   Format documents in order for these to be visually usable and interactive by
   making them to behave as (X)HTML pages inside internet browsers.
.. link: 2023-12-22-customize-atom-rss-documents-with-xslt
.. rights: CC BY-NC-SA 4.0 International License
.. source-author:
   name,uri
   Slatian, acct:slatian@pleroma.envs.net
.. source-link: https://slatecave.net/blog/atom-xslt/
.. source-rights: CC BY-NC-SA 4.0 International License
.. source-title: Pretty Atom-Feed Previews with XSLT
.. title: Customize Atom (RSS) documents with XSLT
.. type: text

.. image:: /graphics/xml.svg
   :alt: XML
   :height: 150px
   :loading: lazy
   :target: /graphics/xml.svg
   :width: 150px

This is a tutorial with details about how to customize the appearance of your
Atom Syndication Format feeds.

Atom and XSLT
`````````````

I assume that you already know what Atom and XML  documents are, and that you
have knowledge in HTML.

As an Atom documents is simply an XML documents on the server, it is reasonable
to link to it; yet Atom or XML documents in internet browser are not displayed
as a gracefully readable document.

In order to make XML documents visually usable as HTML documents, XSLT
(Extensible Stylesheet Language Transformations) can be utilized to transform
XML documents into XHTML documents.

XSLT is a standard specification to transform an XML document into another, and
it is built into most internet browser, which means that XSLT stylesheets would
work perfectly well with any site setup.

In essence, XSLT is similar to PHP; yet, unlike PHP which interpretes over
server-side, XSLT can be interpreted by both client-side and server-side
software.

By this, it is possible to deliver a standard compliant Atom document which is
then rendered into an XHTML document to be viewed with an internet browser.

**Note:** If you have ever seen the message:

.. epigraph::

   This XML document does not appear to have any style information associated
   with it.  The document tree is shown below.

It means that no XSLT stylesheet was defined, not CSS stylesheet; albeit it is
possible to decorate XML documents with CSS, it can not transform XML documents.

Transforming an Atom document with an XSLT stylesheet
`````````````````````````````````````````````````````

For internet browsers to load an XSLT stylesheet, there must be a reference to
it in the subject Atom document:

.. code:: xml

   <!-- <?xml … header here -->
   <?xml-stylesheet type="text/xsl" href="/assets/site_slatecave/atom_to_html.xslt"?>
   <!-- Rest of feed here -->

For the "slatecave" I have added the line to my Atom document template
`atom_to_html.xslt <https://codeberg.org/slatian/site-source.slatecave-net/src/commit/a7ffd694630a425bec04c35b09adcd7461dc9929/templates/atom.xml#L2>`_
and, preferably, include a CSS stylesheet into the static files.

**Note:** I did not have this template before this project, so I slightly
customised
`Zola's builtin template <https://github.com/getzola/zola/blob/38199c125501e9ff0e700e96adaca72cc3f25d2b/components/templates/src/builtins/atom.xml>`_.

**Note:** If you want to utilize XSLT 2.0 functions (mainly `replace()` and
`tokenize()`), then you would have to set the value of `version` to `2.0` in the
`xsl:stylesheet` tag.

A very minimal XSLT stylesheet that results in a greet message.

.. code:: xml

   <?xml version="1.0" encoding="UTF-8"?>

   <xsl:stylesheet version="1.0"
   xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

   <xsl:output method="html" encoding="utf-8" indent="yes" />
     <xsl:template match="/">
       <html lang="en">
         <body>
           <p>Greetings from the XSLT stylesheet!</p>
         </body>
       </html>
     </xsl:template>
   </xsl:stylesheet>

Retrieving content from an Atom document
````````````````````````````````````````

Retrieval of content from an XML document is done with the XSL directive
`value-of`.

.. code:: xml

   <xsl:value-of select="/xpath/query" />

This directive replaces itself with the content of the first element which is
returned by the XPath query in the attribute `select`.

**What is XPath?** XPath is a specification which allows to select from elements
and query of elements of XML documents; it works in a similar fashion to Filepath
and CSS Selectors altogether.

`XPath Cheatsheet <(/notebook/xpath>`_

It is needed to specify the XML namespace (i.e. "`xmlns`) `atom` in the XSLT
stylesheet to be able to query Atom documents.

This minute detail has to be specified in order for the XPath directives to be
able to aim at the relevant elements of the subject Atom document.

The new `xsl:stylesheet` element of the XSLT stylesheet.

.. code:: xml

   <xsl:stylesheet version="1.0"
     xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
     xmlns:atom="http://www.w3.org/2005/Atom">

Elements of Atom documents can then be accessed with this directive:

.. code:: xml

   <xsl:value-of select="/atom:feed/atom:title" />

Please refer to the `XSLT Tutorial <https://w3schools.com/xml/xsl_intro.asp>`_
of W3Schools to create your own stylesheet.

`The slatecave.net Atom to HTML XSLT-Sheet <https://codeberg.org/slatian/site-source.slatecave-net/src/commit/a7ffd694630a425bec04c35b09adcd7461dc9929/static/assets/site_slatecave/atom_to_html.xslt>`_

Content Security Policy
```````````````````````

After uploading I noticed that it did not work. A quick observation at the
debugging console reveals that an XSLT stylesheet is treated as a script which
was disabled, because the slatecave does not utilize any ECMAScript (i.e.
JavaScript) scripting.

Setting `script-src 'self';` allows loading and executing the XSLT stylesheet
resulting in some beautifully XHTML rendered Atom documents.

Conclusion
``````````

XSLT is an efficient mean to manipulate and transform Atom Syndication Format,
and any other XML document into interactive XHTML documents that can be usable
with internet browsers.

As XSLT work over both client-side and server-side software, it is, in fact, the
safest mean to interactively manipulate and transform data which makes it the
best mean to convey information at efficient and at lower costs, and by that
XSLT enables a better internet by considering everyone, rich and poor over the
internet.

I hope that this information was useful or, at least, interesting to you!

~ Slatian
