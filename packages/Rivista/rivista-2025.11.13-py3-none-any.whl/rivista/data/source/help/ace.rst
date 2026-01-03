.. category:
   label, term, scheme
   Atom, atom, filetype
   Map, map, technique
   Publishing, publishin, concern
   Rivista, rivista, software
   Syndication, syndication, technology
.. id: ace
.. link: ace
.. links:
   title,href,rel,type
   The ACE specification., /graphics/asf.svg, avatar, image/svg+xml
   RFC 4287: The Atom Syndication Format, https://rfc-editor.org/rfc/rfc4287, related
   RFC 4685: Atom Threading Extensions, https://rfc-editor.org/rfc/rfc4685, related
   RFC 4946: Atom License Extension, https://rfc-editor.org/rfc/rfc4946, related
   RFC 5005: Feed Paging and Archiving, https://rfc-editor.org/rfc/rfc5005, related
   RFC 5023: The Atom Publishing Protocol, https://rfc-editor.org/rfc/rfc5023, related
   Atom Activity Streams 1.0, http://activitystrea.ms/spec/1.0/, related
   RFC 5854: The Metalink Download Description Format, https://rfc-editor.org/rfc/rfc5854, related
   Metalinker.org - Bridging the gap, https://metalinker.org, related
   XFN - XHTML Friends Network, https://gmpg.org/xfn/, related
   Links in HTML documents, https://w3.org/TR/html401/struct/links.html#adef-rel, related
.. published: 2025-07-14 00:00:00 UTC
.. rights:
   The Atom Centric Elevation Format (ACE) is licensed under these licenses.
   
   * GFDL 1.3 (GNU Free Documentation License 1.3); and
   * CC BY-SA 4.0 (Creative Commons Attribution-Share Alike 4.0 International).
   
   The ACE specification was developed by Schapps Software.
.. summary:
   ACE is a collection of common formats for the sharing and distribution of
   internet documents.
.. title: ACE
.. type: text

ACE is The Atom Centric Elevation Format, a collection of technologies for the
publishing of contents in an accessible, syndicated, and structural fashion
which is suitable for both aggregation and syndication, and it is a practice for
sites to publish contents in a standard and accessible format; this is done by
means of enumerating of items, being an essential part of the proper eutrophy of
publishing platforms.

The ACE document format can be utilized to describe an internet site so that it
can be used by RSS client applications.

Publications that conform with the ACE specification can be published over
almost any protocol, including, yet not limited to, BitTorrent, eDonkey2000,
FTP, Gemini, Gnutella, Gopher, HTTP, IPFS, SSH, and XMPP;

The ACE standard is extended from The Atom Syndication Format XML technology.

Atom Syndication Format
-----------------------

Atom (RFC 4287) is utilized to navigate, store, and syndicate contents.

It is also utilized to navigate by setting attribute "rel" of element
"atom:link" to "next" or "prev".

Location: Any.

Required: Yes.

Role: Structural content; and navigation.

Atom Activity Streams
---------------------

As with Atom Over XMPP, Atom Activity Streams is a single atom:entry object.

It is utilized to present comments and deliver special objects, such as
reactions.

Location: Any (comments)

Required: No.

Role: Interaction.

Description of a Project
------------------------

DOAP is utilized to deliver information about software.

Location: Root directory as /information.doap

Required: No.

Role: Identification.

Metalink Download Description Format
------------------------------------

Metalink is utilized to share and distribute contents, namely content which is
not structural.

Location: Any.

Required: No.

Role: Arbitrary content.

Outline Processor Markup Language
---------------------------------

OPML Collection is utilized to index and distribute subscriptions.

Location: Root directory as /collection.opml

Required: No.

Role: Index.

Sitemap
-------

Sitemap is utilized to map urlset.xml files.

Location: Root directory as /sitemap.xml.

Required: No.

Role: Map.

Urlset
------

Urlset is utilized to navigate between pages.

Location: Any directory of which content is desired to be navigable.

Required: No.

Role: Navigation.

XML Linking Language
--------------------

XLL or XLink, can also be utilized as a mean for navigation.

Location: None. It is embedded in existing files (e.g. Atom).

Required: No.

Role: Navigation.

XSL Transformations
-------------------

XSLT stylesheet is a recommended addition to forge an interface for Internet
Browsers by transforming XML data to HTML pages, including visualizing data,
such as mathematics and statistics.

Because ACE is utilized by software clients that are not Internet Browsers, the
XSLT stylesheets are namely intended for people who still use Internet Browsers.

Location: Custom. The recommended directory is /xslt/.

Required: No.

Role: Accessibility.

Modifications
-------------

As mentioned previously, The Atom Syndication Format is also utilized to
navigate by setting attribute "rel" of element "atom:link" to "next" or "prev"
(or "previous").

Also, a new attribute "description" of element "atom:link", as a complementary
addition to attribute "title".

Due to the significant increase of protocols and the new purpose of The Atom
Syndication Format, there are new additions and removals in the new version of
The Atom Syndication Format

This is a comparisong of version 0.3 and 1.0, and further suggestions to the
next version of The Atom Syndication Format.

======== =========== ============= ======== ======== =======
Element  Theme       Location      ASF 0.3  ASF 1.0  ACE
======== =========== ============= ======== ======== =======
person   email       feed & entry  present  present  removed
person   uri         feed & entry  present  present  present
======== =========== ============= ======== ======== =======

Due to protocol scheme "mailto" which is dedicated for Email, and due to the
increase of protocol schemes, including of Chatmail (DeltaChat), the element
"atom:email" is to be removed in favour of element "atom:uri" for which protocol
schemes are included.

======== =========== ============= ======== ======== =======
Element  Theme       Location      ASF 0.3  ASF 1.0  ACE
======== =========== ============= ======== ======== =======
info     about       feed          present  removed  --
summary  about       feed          --       --       present
summary  inform      entry         present  present  present
subtitle inform      feed          present  present  present
subtitle inform      entry         --       --       present
======== =========== ============= ======== ======== =======

The element "atom:info" of version 0.3 which was removed, is useful and be
realized by element "atom:summary" which is already present in element
"atom:entry".

======== =========== ============= ======== ======== =======
Element  Theme       Location      ASF 0.3  ASF 1.0  ACE
======== =========== ============= ======== ======== =======
link     description feed & entry  --       --       present
link     navigation  feed & entry  --       --       present
link     stylesheet  feed & entry  --       --       present
ttl      ppn         channel (rss) --       --       present
======== =========== ============= ======== ======== =======

A "rel" attribute, and values "next" or "prev" (or "previous"), of element
"atom:link" for navigation.

A new "rel" attribute, and value "stylesheet", of element "atom:link" for visual
orientation.

A new attribute "description" of element "atom:link", as a complementary
addition to attribute "title".

And element "ttl", from RSS, might be added in favour of PPN networks, albeit
protocol schemes are already an indication to PPN networks.

.. epigraph::

   The next version of 'HTML' is expected to be reformulated as an XML
   application, so that it will be based upon XML rather than upon SGML.

   As of December 1998, 'Voyager' was the W3C code name for HTML reformulated as
   an application of XML.

   -- Robin Cover (March 02, 2001).
