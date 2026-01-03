.. category:
   label, term, scheme
   Atom, atom, filetype
   News, news, concern
   Syndication, syndication, technology
   RDF, rdf, filetype
   RSS, rss, filetype
.. id: rss
.. link: rss
.. links:
   title,href,rel,type
   The RSS specification, /graphics/rss.svg, avatar, image/svg+xml
   RFC 4287: The Atom Syndication Format, https://rfc-editor.org/rfc/rfc4287, related
   RFC 4685: Atom Threading Extensions, https://rfc-editor.org/rfc/rfc4685, related
   RFC 4946: Atom License Extension, https://rfc-editor.org/rfc/rfc4946, related
   RFC 5005: Feed Paging and Archiving, https://rfc-editor.org/rfc/rfc5005, related
   RFC 5023: The Atom Publishing Protocol, https://rfc-editor.org/rfc/rfc5023, related
   RFC 5854: The Metalink Download Description Format, https://rfc-editor.org/rfc/rfc5854, related
   Metalinker.org, https://metalinker.org, related
   XEP-0277: Publishing Over XMPP, https://xmpp.org/extensions/xep-0277.xml, related
   XEP-0472: PubSub Social Feed, https://xmpp.org/extensions/xep-0472.xml, related
   HTTP Conditional Get for RSS Hackers, https://fishbowl.pastiche.org/2002/10/21/http_conditional_get_for_rss_hackers, related
   The Atom Syndication Format and Publishing Protocol, https://intertwingly.net/wiki/pie/FrontPage, related, text/html
   What Is RSS, https://xml.com/pub/a/2002/12/18/dive-into-xml.html, related
   RSS Rapidly Becoming the Next Standard in Commercial Internet-Publishing and Online Information Distribution, http://emediawire.com/releases/2005/1/emw200210.htm, related
   The Architecture of RSS, http://scripting.com/stories/2010/09/16/theArchitectureOfRss.html, related
   Why Big Media Wants to Kill RSS, and Why We Should Not Let It, https://newsome.org/2011/01/04/why-big-media-wants-to-kill-rss-and-why-we-shouldnt-let-it/, related
   What the Heck is RSS? And why should I care?, https://copyblogger.com/what-the-heck-is-rss/, related
   How to use RSS feeds to boost your productivity, https://zapier.com/blog/how-to-use-rss-feeds/, related
   Why Atom instead of RSS?, https://news.ycombinator.com/item?id=26169162, related
   Pretty Atom-Feed Previews with XSLT, https://slatecave.net/blog/atom-xslt/, related
   RSS Guide - How to get started using RSS, https://thoughts.melonking.net/guides/rss-guide-how-to-get-started-using-rss, related
   RSS - The Best Way To Improve Your Internet Experience, https://ijver.me/en/blog/use-rss/, related
.. published: 2025-07-14 00:00:00 UTC
.. summary: The specification Rich Site Summary.
.. title: RSS
.. type: text

RSS (Rich Site Summary) feeds allow you to see when sites have added new content
so you can get the latest headlines and videos in one place, as soon as they are
published, *without* having to visit the sites you have taken the feeds from,
and RSS virtually includes every "self-refreshing" or "self-updating" content.

Mechanism
`````````

RSS feeds are an internet format that utilized to publish frequently updated
content (such as news headlines, real-time stock market quotes, journal entries,
videos, et cetera) in a standardized XML format.

An RSS document includes text (full or summerized) and metadata such as links to
torrents, internet pages, publishing time, authorship.

Usage
`````

When seeing the RSS logo on a site, clicking on it let you subscribe to its RSS
feed, which simply means copying the feed URL and pasting it into your RSS
Reader.

The basic idea is that you do not have to "refresh" anything because it is done
automatically. Once you have bookmarked your favorite feeds, only launch your
news reader to know what is new.

XMPP
````

Initially implemented by "Tigase Inc.", RSS for XMPP (henceforth "Atom Over
XMPP") is the most advanced version of RSS; It is the implementation which has
made RSS truely real-time, for the first time in its history over the internet.

Atom Over XMPP enables real-time immediate updates, with a maximal deviation
difference of 15 - 30 seconds, at most, from the time a new update is published.

Because Atom Over XMPP allows to automate the delivery of real-time updates in a
matter of seconds; since its inception, in the early years of the millennium of
2000, Atom Over XMPP has been the de-facto standard for publishing of critical
information amongst high ranking units in aviation, intelligence, military, and
police organizations, including elite special armed forces.

Vocabulary
``````````

* Atom - The Atom Syndication Format is the current standard format for RSS.

* Atom Over XMPP - A method of distributing RSS updates over XMPP, in real-time.

* Bitcast - A syndication feed which is meant to convey hyper-content (any type
  of textual or multimedia content of unlimited size), in batch, over the
  BitTorrent Peer-to-Peer network.

* Data feed - A practice to receive current data from any data source. It is
  utilized by real-time applications in point-to-point settings.

* Metacast - A syndication feed which is meant to convey hyper-content (any type
  of textual or multimedia content of unlimited size), in batch, over multiple
  protocols, including Peer-to-Peer protocols, such as BitTorrent, eD2k
  (eDonkey2000), FTP, G2 (Gnutella), Gemini, HTTP, IPFS, and SSH, by utilizing
  the Metalink technology.

* Metalink - Metalink is an internet framework which is designed to accelerate
  and facilitate the downloading of data in a reliable and secure manner. It
  circumscribes both types of downloading methods, centralized and decentralized
  protocols. For consumers and content providers, Metalink makes downloading
  simpler, faster, and more reliable.

* Microsummary - A plain text document which, usually, has a single line with
  under a hundred of characters, and it usually informs of a status of an
  affair or concern. It is short, fast, and bandwidth efficient; and it is
  intended to be a complementary mean to RSS

* Microsummary (XML) - An XML file with XPath rules which is designed for the
  extraction of data from sites that either do not provide Microsummaries nor
  RSS feeds.

* Photofeed - A syndication feed which is specifically meant to convey imagery
  content.

* Podcast - A syndication feed which is specifically meant to convey audible
  content.

* PPN - An abberviation for Peer-to-Peer (P2P) Network which is a reference to
  protocols and networks, such as BitTorrent, eD2k, G2, and IPFS, that are
  mainly designed for the safe and secure distribution of content of any size;
  be it articles, audio books, digital books, documents, games, music, videos
  and other types of multimedia content; Most of P2P software support the
  technology of RSS.

* Product feed - A syndication feed which is specifically meant to convey a list
  of commodities and products.

* RSS - An acronym for Really Simple Syndication or Rich Site Summary.

* RSS Feed - An XML document which is formed in a standard structure.

* Syndication - A general reference to any technology which allows to convey
  structured data in an automated fashion.

* Vocast - A syndication feed which is specifically meant to convey motion
  picture content.

.. epigraph::

   RSS is all about *real-time* information.
