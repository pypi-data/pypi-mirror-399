.. category:
   label, term, scheme
   ACE, ace, specification
   Atom, atom, filetype
   Feed, feed, technology
   Gemini, gemini, protocol
   News, news, concern
   RDF, rdf, filetype
   Rivista, rivista, software
   RSS, rss, filetype
   Syndication, syndication, technology
   XMPP, xmpp, protocol
.. id: rivista
.. link: rivista
.. links:
   ACE, ace, related
   The logo of Rivista Voyager, /graphics/rivista.svg, avatar, image/svg+xml
   XEP-0277: Journaling Over XMPP, https://xmpp.org/extensions/xep-0277.xml, related
   XEP-0472: PubSub Social Feed, https://xmpp.org/extensions/xep-0472.xml, related
   Numen - Voice control for handsfree computing, /posts/2022-10-20-numen-voice-control-for-handsfree-computing, related
   Numen Voice Control, https://numenvoice.org, related
   Nerd Dictation, https://codeberg.org/ideasman42/nerd-dictation, related
   Sayboard, https://codeberg.org/ElishaAz/Sayboard, related
.. published: 2025-07-14 00:00:00 UTC
.. summary:
   Rivista Voyager is a decentralized and multi-protocol publishing system for
   ActivityPub, Gemini, HTTP, and XMPP, which utilizes the publishing
   capabilities of the federated XMPP communications network.
   It is both private and public publishing platform, and it can either act as a
   journaling (i.e. blogging) platform, or content management system.
.. title: Rivista
.. type: text

Rivista Voyager is a decentralized and multi-protocol publishing system for
ActivityPub, Gemini, HTTP, and XMPP, which utilizes the publishing capabilities
of the federated XMPP communications network.

It complies with the PubSub technology which is known as Atom Over XMPP or
Atomsub, and which is specified in XEP-0277 and XEP-0472, a standard was
introduced during the early years of the millennium 2000.

It is able to interacts with the XMPP network, and, consequently, to further
interact with other XMPP platforms such as Blasta, Libervia, Movim, Pelican, and
also with XMPP desktop software, such as LeechCraft.

It is both a private and public publishing platform, and it can act as a
journaling (i.e. blogging) platform or content management system.

Introduction
````````````

* RSS as first-class.

* Every page is a standard RSS document (The Atom Syndication Format).

* Accessibility from every device; internet browsers are not necessary.

* Browsable with standard RSS readers.

Features
````````

Syndicated, accessible, portable, and agreeable.

Ace
---

The specification "Atom Centric Elevation" is a uniform and universal document
format for navigability and portability accross any content delivery protocol,
be it centralized (e.g. Gemini) or decentralized (e.g. Gnutella).

Atom
----

Content documents are uniformly made of the syndication standard document Atom
Syndication Format.

Gemini
------

Posts are automatically published as Gemtext, including syndicated Gemini feeds.

HTTP
----

Posts are automatically published as XHTML, including syndicated RSS feeds.

Microformat
-----------

The specification microformat "h-entry" is realized by XSLT stylesheets in order
for XHTML pages to be usable as RSS feeds.

* In comparison to RSS, the specification "h-entry" is inferior, yet "h-entry"
  is utilized as a preemptive and substitute measure, if some organization would
  dare to try to sabotage RSS communications.

Microsummary
------------

Regularly updated short summaries that provide current and helpful information
about site or each page.

Modes
-----

Journals can be published as static or dynamic internet site; that is, to
either function as a CMS (content management system), or an SSG (static site
generator).

PubSub
------

Posts are automatically published on a the automated Publish-Subscribe system of
XMPP as "Atom Over XMPP".

RSS
---

Every page can be monitored for changes or updates with a typical RSS reader.

Theme
-----

The theming system is entirely made of standard CSS and XSLT stylesheets.

XMPP
----

A seamless interaction over the federated XMPP communication network.

Principles
``````````

Principle values, moral commitments, and subsequent benefits.

Accessibility
-------------

As every page is syndicatable, every page is accessible by automated means (i.e.
"machine-readable"), so it is possible to equally access to contents with any
device which can communicate with Gemini, HTTP, or XMPP, and parse XML data;
and, with interactive audible system, such as Nerd Dictation, Numen Voice
Control, or Sayboard, it is possible to browse contents without a graphical
display monitor.

Controllability
---------------

Whereas the Gemini and HTTP interfaces are designed to form a traditional
internet journal, it is not required to be bound to any of each, as each content
page is made of the standard document Atom Syndication Format; thus, it is
possible to choose any software (e.g. an XMPP client, or RSS reader) to browse
contents with, and further interactions.

Customizability
---------------

The theming system is made of standard CSS and XML (Atom, DOAP, OPML, Sitemap,
and XSLT), which means that your themes will always remain consistent for many
years, as all themes are made of well established standard XML documents which
retain their uniform structures.

Navigability
------------

The navigation mechanism is structured, and can be customized.

Custom navigation from one document to another, could be done it two fashions.

* Indexing of documents by setting classification to "related"; and

* Classifying a document as "next", or "previous" page of a given document.

It is further possible to navigate documents from one protocol to another (e.g.
from XMPP, to FTP, to RSYNC, to Gemini, to eDonkey2000).

Portability
-----------

Rivista Voyager is built upon standards, and has no software-specific features
of its own; therefore, it is portable to any protocol or system, including ADC,
BitTorrent, DC++, eDonkey2000, FTP, Gemini, Gnutella, Gopher, HTTP, Hypercore,
IPFS, RSYNC, SSH, Telnet, XMPP, or otherwise.

Properability
-------------

Rivista treats to each element differently and respects the peculiarity of each
element, such as having different contents for elements `atom:summary` and
`atom:content`, as should.
