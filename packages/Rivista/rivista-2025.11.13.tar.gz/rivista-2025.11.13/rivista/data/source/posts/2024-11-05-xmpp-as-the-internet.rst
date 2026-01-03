.. author:
   name,uri
   Schimon Jehudah Zachary, xmpp:sch@pimux.de?message
.. category: HTML, Internet, Publishing, PubSub, XHTML, XMPP
.. id: 2025-10-24-xmpp-as-the-internet
.. link: 2025-10-24-xmpp-as-the-internet
.. links:
   title,href,rel,type
   The motto of XMPP, /graphics/xmpp_motto.svg, photo, image/svg+xml
   The logo of the protocol XMPP, /graphics/xmpp.svg, avatar, image/svg+xml
   Recommended XMPP mobile chat clients, /posts/2026-01-01-recommended-xmpp-mobile-chat-clients, related
   Recommended XMPP desktop chat clients, /posts/2026-01-01-recommended-xmpp-desktop-chat-clients, related
   The logo of the XMPP internet protocol., /graphics/xmpp.svg, enclosure, image/svg+xml
   Atom Over XMPP - IETF 66, magnet:?xt=urn:ed2k:8ee1b0d1de2cbf1bd10a7c6a0366c483&xt=urn:ed2khash:8ee1b0d1de2cbf1bd10a7c6a0366c483&xl=119034&xt=urn:btih:b276894ff2c7c0d4f71661022986fd7c0f800412&xt=urn:btmh:12201d1d48fe4b10008a8fbfd4d3d7143cbcb1098f8dd2adcbdba6cdf399ca3765df&dn=atom-over-xmpp-draft-saintadndre-atompub-notify-peter-saint-andre-jabber-software-foundation-ietf-66.pdf&xl=119034&ws=https://datatracker.ietf.org/meeting/66/materials/slides-66-atompub-1.pdf&ws=https://web.archive.org/web/20240425080106if_/https://datatracker.ietf.org/meeting/66/materials/slides-66-atompub-1.pdf, enclosure
   Atom Over XMPP - IETF 66, https://datatracker.ietf.org/meeting/66/materials/slides-66-atompub-1.pdf, enclosure
   Atomsub: Transporting Atom Notifications over PubSub to XMPP, https://datatracker.ietf.org/doc/draft-saintandre-atompub-notify/, related
   XEP-0060: Publish-Subscribe, https://xmpp.org/extensions/xep-0060.xml, related
   RFC 4287: The Atom Syndication Format, https://rfc-editor.org/rfc/rfc4287, related
   XEP-0277: Publishing Over XMPP, https://xmpp.org/extensions/xep-0277.xml, related
   XEP-0472: Pubsub Social Feed, https://xmpp.org/extensions/xep-0472.xml, related
   XEP-0496: Pubsub Node Relationships, https://xmpp.org/extensions/xep-0496.xml, related
   Servers are obsolete, http://gldialtone.com/ServersObsolete.htm, related
   A universal and stable API to everything: XMPP, https://fosdem.org/2025/schedule/event/fosdem-2025-5721-a-universal-and-stable-api-to-everything-xmpp/, related
   “XMPP: The Definitive Guide” Code Examples, https://mko.re/blog/xmpp-tdg-code/, related
   We Do not Need HTTP Frameworks, https://metajack.im/2009/01/25/we-dont-need-no-stinkin-web-frameworks/, related
   Filtering the Real Time Web, https://metajack.im/2009/01/22/filtering-the-real-time-web/, related
   Real Time Is Completely Different, https://metajack.im/2008/09/11/real-time-is-completely-different/, related
   XMPP Microblogging Thoughts, https://metajack.im/2008/09/10/xmpp-microblogging-thoughts/, related
   xmpp and microblogging - let’s do it!, http://blog.jwchat.org/2008/09/09/xmpp-and-microblogging-lets-do-it/, related
   Practical Transparency - Distributing financials using XMPP..., https://ralphm.net/blog/2006/10/05/telexng, related
   nothing new… some areas that are under exploited by xmpp, http://blogs.openaether.org/?p=111, related
   Jabber/XMPP/IM Protocols and Digital Identity (etc.), http://netmesh.info/jernst/2005/06/15, related
   XMPP and CMS, http://halr9000.com/ideas/xmpp-and-cms/, related
   How Jabberzilla Improves Mozilla Projects, http://jabberzilla.jabberstudio.org/wifm/mozbene.shtml, related
   Atom Over XMPP for news readers, 2024-12-09-atom-over-xmpp-for-news-readers.gmi, related
   Atom Over XMPP for publication platforms, 2024-12-07-atom-over-xmpp-for-publication-platforms.gmi, related
   Publishing over XMPP, 2024-05-30-publishing-over-xmpp.gmi, related
   The benefits of XMPP, 2024-06-22-the-benefits-of-xmpp.gmi, related
   Comments section powered by XMPP, 2024-08-06-comments-section-powered-by-xmpp.gmi, related
   The campaign for HTML5 was a war against XML and interoperability, 2024-06-10-the-campaign-for-html5-was-a-war-against-xml-and-interoperability.gmi, related
   The p2p-configs manifesto, 2016-03-18-the-p2p-configs-manifesto.gmi, related
.. published: 2025-10-24 0:00:00 UTC
.. summary: Atom Over XMPP to replace the HTTP realm.
   If you are principled; value independence; add to life; believe in a future
   which is built upon open software and protocols; experiment with new ideas,
   and do not worry about being different; and you also build software that
   others rely on; then you should read this article.
.. title: XMPP as the internet
.. type: text

In the recent six months, thanks to friends from Austria, Canada, France,
Germany, Italy, Russia and Sweden, I have been involved with the technology of
XMPP PubSub (i.e. XEP-0060: Publish-Subscribe).

XEP-0060: Publish-Subscribe
---------------------------

XEP-0060: Publish-Subscribe (PubSub) is an XMPP specification which is utilized
to enable features that require consistent storage.

It is utilized for Contact Activity, Contact Mood, OMEMO, Server Status, and
more.

It was approved by the XSF on november 2002.

The Atom Syndication Format (RFC 4287)
--------------------------------------

RFC-4287: The Atom Syndication Format (Atom) is a syndication standard to convey
syndicated content over XML files.

It supersedes the specifications RDF and RSS.

It was approved by the IETF on december 2005.

Atom Over XMPP
--------------

During the years 2004 to 2008, Mr. Bob Wyman, Mr. Joe Hildebrand, and Mr. Peter
Saint-Andre have proposed a new specification to which they have called Atom
Over XMPP (AtomPub and AtomSub), an incorporation of The Atom Syndication Format
and XMPP.

The general idea was to embed Atom syndication feeds to PubSub node items of
XMPP; both, Atom and XMPP are made of XML.

The idea of Atom Over XMPP was quickly censored and hidden from the public, by
flooding the internet with other falsified shiny distractions, and overwhelm the
public with nonsensical information about HTML and a phoney competition of HTML
standards ("browser war", so called), APNG (animated PNG), animated CSS, and
even more information of no true significance nor relevance, that only created
further problems.

`Atom Over XMPP <magnet:?xt=urn:btih:b276894ff2c7c0d4f71661022986fd7c0f800412&xt=urn:btmh:12201d1d48fe4b10008a8fbfd4d3d7143cbcb1098f8dd2adcbdba6cdf399ca3765df&dn=atom-over-xmpp-draft-saintadndre-atompub-notify-peter-saint-andre-jabber-software-foundation-ietf-66.pdf&xl=119034&ws=https://datatracker.ietf.org/meeting/66/materials/slides-66-atompub-1.pdf&ws=https://web.archive.org/web/20240425080106if_/https://datatracker.ietf.org/meeting/66/materials/slides-66-atompub-1.pdf>`_

Gemini
------

Roughly thirty years later, the shenanigans of HTML standards, from unnecesary
CSS animations, to useless 3D effects, to native multimedia playback, to
arbitrary code execution from within HTML browsers, to further operate video
games and operating systems, have caused to people to create a new protocol for
publishing and linking to internet resources, which is called Gemini.

The name should probably be changed to a name which is not generic, and be
registered as a trademark, because companies already attempt to censor it by
branding their products and services with "Gemini".

Albeit, the usefulness of the protocol Gemini, and the markup language of the
filetype GMI, we might have skipped an essential and vital structural system,
which is PubSub of the protocol XMPP, which might already have most of the
features that Gemini already intends to provide.

`Project Gemini <gemini://geminiprotocol.net>`_

Implementation
--------------

In 2008, the XMPP Standards Foundation (XSF) has published an XMPP specification
for Atom Over XMPP by the title "Microblogging over XMPP" (henceforth,
"Publishing Over XMPP"), which is XEP-0277.

XEP-0277 allows to publish content over XMPP, as was suggested to the IETF since
2004, and XEP-0472 is meant to extend the publishing abilities as implemented in
the Movim platform.

It is said, that XEP-0277 and XEP-0472 should be harmonized.

Practice
--------

A quote from the article "We do not need HTTP frameworks":

XMPP provides pubsub, presence, discovery, and much more.

* Communication is done via XMPP through Strophe instead of polling a database or using work queues. This is more efficient.

* Configuration is stored in pubsub nodes instead of relational databases. One good consequence of this is that all subscribers get instant notification of configuration changes, similarly to a broadcast SIGHUP.

* Front end apps, administrative code, and internal utilities are all just ECMAScript (i.e. JavaScript). This makes them trivial to develop and test locally, and we do not need any special deployment code.

* The whole system is mostly decoupled because there is no middle interfacing layer. The backend speaks XMPP, the frontend speaks XMPP, and they both use standard XMPP layer protocols to do work.

-- Jack Moffitt

Projects
--------

XMPP projects that convey XMPP to XHTML over HTTP.

Libervia
````````

The Libervia platform of Mr. Jérôme Poisson provides a content management system
(CMS) platform which currently focuses on private sites.

Movim
`````

The Movim platform of Mr. Timothée Jaussoin has extended the span of publishing
content in a more general sense which embodies a social network.

Rivista
```````

The Rivista Voyager is a personal publishing platform which forms of a journal
site over Gemini, HTTP, and XMPP.

Note
````

It is important to mention, that content which is published in the method of
Atom Over XMPP is of a different type, as it is federated by design, and is also
autonomous, in the sense that contents are actually stored in and controlled by
the account of the publisher, and systems such as Libervia and Movim are only
aggregating that data and have no control over it.

Hierarchy
---------

Each PubSub service is organized in a uniform hierarchical structure.

Each PubSub service encapsules nodes.

Each node encapsules items.

Unlike HTML content over HTTP, the structure of HTML over XMPP does not change.

A fixed structural system assures a swift system to browse and find information.

The hierarchical structure is one of the greatest benefits that XMPP PubSub has
over HTTP, because the PubSub system solves two major issues, to save bandwidth,
and to deliver tens of thousand of entries at a fraction of a cost in comparison
to HTTP.

Advantages
----------

* Bandwidth efficient;

* Entries are segmented into (node) items;

* Extensible;

* Immediate updates (polling is optional);

* Media attachments;

* Standard format (including rich text); and

* Structural information.

Portability
-----------

In contrast to HTTP, content which is hosted over XMPP can be automatically
forwarded to HTTP, and thereby is considered portable.

Blasta, JabberCard, Libervia, Movim, and Rivista XJP are, essentially, HTTP
gateways to XMPP.

Status
------

Movim is currently the platform which implements Atom Over XMPP at its best.

Libervia, in addition to its current publishing capabilities as CMS (content
management system), will provide a forum management system which would also be
based on Atom Over XMPP.

JabberCard or Rivista will offer a private site builder to each XMPP account,
based on Atom Over XMPP.

Example
-------

This is a proposed structure for an XMPP based publication.

The JID (Jabber ID) journal.schapps.i2p represents a PubSub service.

.. code::

   journal.schapps.i2p
   ├─All
   ├─2024
   ├─2024-12
   ├─2024-04
   ├─2024-05
   ├─2023
   ├─2023-01
   ├─2022
   ├─2022-09
   ├─2021
   ├─2021-05
   ├─2021-12
   ├─Atom
   ├─CMS
   ├─JabberCard
   ├─Libervia
   ├─Movim
   ├─OMEMO
   ├─Privacy
   ├─Publishing
   ├─PubSub
   ├─RivistaXJP
   ├─Security
   ├─Summit
   ├─Syndication
   ├─VoIP
   └─XMPP

This post, supposing it has tags, will be represented as an item of nodes 2024,
2024-12, All, Atom, CMS, JabberCard, Libervia, Movim, PubSub, Publishing,
RivistaXJP and XMPP.

The item will have to be duplicated on the XMPP server, which means that the
specified nodes would have the exact same item.

The visual indexing of posts be made by the CMS software.

XEP-0496
--------

Mr. Jérôme Poisson of Libervia has created an XEP which should facilitate this
concern, and might neglect the need to duplicate items.

.. epigraph::
   This specification describes how to establish links between pubsub nodes,
   allowing for optional hierarchical organization.

Conclusion
----------

The projects Libervia and Movim are realizing that HTTP is useless, and can
indeed be deprecated by XMPP, as a platform for publishing, business, finance,
and telecommunicatom.

Note
----

A quote from the article "Servers are obsolete":

.. epigraph::
   If hosted filesystems storages, and public key encryption, had been available
   20 years ago, SMTP, POP3, and HTTP would never have been invented.

   Certainly, their markets would have been much smaller.

   -- Todd Boyle CPA Kirkland WA

If you want to play 3D video games, or otherwise risk yourselves and your
privacy with the hazards of the HTTP protocol, and also with ECMAScript. which
needlessly consumes vast amounts of electrical power, then use HTTP, albeit it
is not good for you.

Thanks
------

Special thank you to Mr. Jérôme Poisson of project Libervia, and Mr. Timothée
Jaussoin of project Movim who have meticulously taught me about the
technicalities of XMPP PubSub.

Thank you to my Argentinian, Austrian, Finnish, Italian, and Swedish fellows for
quickly guiding and teaching me about the Gemini and Gopher specifications.

And thank you to everyone else from Asia, Europe and The United States For
America.

I am most honored, and glad to collaborate and work with people who actually
seek to create and help to create value, instead of exploiting vulnerabilities
to abuse and oppress creativity potential.

Thanks to you, I have accomplished in a couple of years more than I have
accomplished in a couple of decades in the middle east.

Your good directions have increased my strength and value more than I could have
imagined to be possible for me in my lifetime.

Post script
-----------

As Mr. Stefan Strigler has stated in the year of 2008.

.. epigraph::
   There has been so much conversation on this topic. Conferences are being held
   and so on. But actually I think it is time to not only talk about it.

   Face it! Get your hands dirty!
