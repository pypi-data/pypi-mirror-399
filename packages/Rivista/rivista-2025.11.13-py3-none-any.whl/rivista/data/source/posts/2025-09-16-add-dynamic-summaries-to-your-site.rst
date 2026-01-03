.. author:
   name,uri
   Schimon Jehudah Zachary, xmpp:sch@pimux.de?message
.. category:
   label, term, scheme
   Dynamic Title, dynamic-title, practice
   Live Title, live-title, practice
   Microsummary, microsummary, technology
   Syndication, syndication, technology
   Tutorial, tutorial, concern
   XML, xml, technology
   XPath, xpath, query-language
   XSL, xsl, technology
   XSLT, xslt, computer-language
.. id: 2025-09-16-add-dynamic-summaries-to-your-site
.. link: 2025-09-16-add-dynamic-summaries-to-your-site
.. links:
   title,href,rel
   An example microsummary extension of NLnet, /file/nlnet-next-deadline.xml, enclosure
   An XSLT stylesheet for microsummary extension, /file/microsummary.xsl, enclosure
   Microsummary topics, https://udn.realityripple.com/docs/Archive/Mozilla/Microsummary_topics, related
   Microsummary XML grammar reference, https://udn.realityripple.com/docs/Archive/Mozilla/Microsummary_topics/XML_grammar_reference, related
   Creating a Microsummary, https://udn.realityripple.com/docs/Archive/Mozilla/Creating_a_microsummary, related
   Microsummary - Microformats, http://microformats.org/wiki/page-summary-formats, related
   Microsummaries XML Namespace, https://mozilla.org/microsummaries/0.1, related
   Live Title Generator, http://userstyles.org/livetitle/, related
   OSCON - Microsummaries on the internet, https://mdn.dev/archives/media/presentations/microsummaries/, related
   mykzilla: microsummaries beyond bookmarks, http://melez.com/mykzilla/2006/07/microsummaries-beyond-bookmarks.html, related
.. published: 2025-09-16 0:00:00 UTC
.. summary:
   The mechanism of microsummary allows to have both static and dymamic titles
   for internet sites, for any purpose, from special announcements to
   advretizing items of a garage sale, and more.
.. title: Add dynamic summaries to your site
.. type: text

.. image:: /graphics/newspaper.svg
   :alt: Newspaper
   :height: 150px
   :loading: lazy
   :target: /graphics/newspaper.svg
   :width: 150px

When a site offers a microsummary (a regularly updated summary of the premier
information on a given internet page), people can create a bookmark with a
"Dynamic Title", otherwise known as so-called "Live Title".

These Dynamic Titles are compact enough to fit in an area which is available to
a typical bookmark label, dashboard, pager, PDA, or desktop notification.

Dynamic Titles display helpful information about pages than static page titles,
and are regularly updated with current and latest information.

Unlike RSS, Dynamic Titles are temporary, and are subjected to instant changes
and updates that are intended to be quick, short and ephemeral, and are not
meant to be permamaent, because they only represent concerns of current moments.

Compared to the messaging and telecommunication system of XMPP, RSS may be
regarded as consistent "presence" messages, and Dynamic Titles can be regarded
as temporary "regular" messages.

The change rate of Dynamic Titles is typically shorter and more frequent than of
RSS.

There are various of sites that can be bookmarked with Dynamic Titles, and
Rivitsa offers this capability as well.

Usage
`````

Whether you manage a Sunday service of a Church, and you want to
advertize the number of members who are expected to attend at next service; or
advertize of products of an auction, garage sale, or inventory store; or
advertize items of catalogues such as arts, music, poems, songs, or words; or
advertise of current geographical data or weather forecast.

The possibilities are indeed vast and useful.

It is recommended for catalogues (e.g. "word of the day"), forums, publications,
trackers, et cetera, to utilize Dynamic Titles as a secondary mean to RSS.

Code
````

Example code of a microsummary.

Metadata and plain text
-----------------------

In file `/index.xhtml` add this code inside the element `<head></head>`.

.. code:: xml

   <link href="/index.txt"
         rel="microsummary"
         type="text/plain; charset=utf-8">

Create a file `/index.txt` and add this note.

.. epigraph::
   Community choir gathering is set to next Tuesday.

Of course, it would be more productive that the data file `/index.txt` would be
updated automatically, unless you have a special requirement to update it
manually.

Upon adding a bookmark of page `/index.xhtml` internet browsers that support
Dynamic Titles would prompt to utilize the static or the dynamic title of a
given page.

Microsummaries XML namespace
----------------------------

The secondary fashion is to have an XML file which would have the directives to
extract the desired data. This is particularly helpful when the subject page,
which has the desired data, has no support for microsummaries, yet.

.. code:: xml

   <?xml version="1.0" encoding="UTF-8"?>
   <?xml-stylesheet href="microsummary.xslt" type="text/xsl"?>
   <generator xmlns="http://mozilla.org/microsummaries/0.1" name="Slixfeed version check">
     <pages>
       <include>https://git.xmpp-it.net/sch/Slixfeed/src/branch/master/slixfeed.doap</include>
     </pages>
     <update interval="30"/>
     <template>
       <transform xmlns="http://www.w3.org/1999/XSL/Transform" version="1.0">
         <output method="text"/>
         <template match="/">
           <value-of select="normalize-space(string(//version))"/>
         </template>
       </transform>
     </template>
   </generator>

Adding the URL of that XML file will create a bookmark which would display the
current version of Slixfeed news service.

Examples
````````

Type of contexts, pages, and possible microsummaries.

Activity
--------

Community activity name; and time remaining.

.. epigraph::
   🏐 Volleyball - 2 hours and 14 minutes left

Version check
-------------

Project name; commit number; and commit date.

.. epigraph::
   Slixfeed - b23ae16657 - 2025-07-06 11:17:21 +03:00

Auction
-------

Item name; current highest bid; and time remaining.

.. epigraph::
   💻 Purism Librem 15 - $300 - 1 day left

BitTorrent
----------

Latest completed torrent.

.. epigraph::
   🎞 The News-Benders (1968)

Broadcast
---------

Production name; radio show name; host name; and time remaining for show start.

.. epigraph::
   RLM: Behind The Woodshed - Hal Anthony - 17 minutes countdown

Countdown
---------

Number of days to an event.

.. epigraph::
   42 days left

Events
------

Event name; subject name; current number of attendeed; and speaker.

.. epigraph::
   FOSDEM 2025 - Nostr - 1272 attendeed - Wouter Constant

Firewall server
---------------

Component name; sum of blocked advertisements; sumof blocked scripts; and state.

.. epigraph::
   pi-hole: 53427 ads - 3456 scripts - updating database

Component name; number of blocked IP addresses; and current mode.

.. epigraph::
   OpenWRT: 548 blocked - deny incomming

Forum thread
------------

Thread name; number of comments; and last commenter.

.. epigraph::
   Movim interoperability with the Libervia Forums system- 162 comments - Goffi

Freight shipment
----------------

Product name; package number; status; current mean; and current place.

.. epigraph::
   7 ounce of gold - 53FT92437HA - shipping - armored trucks - Khazakhstan

Fundraise
---------

Sum of fund; and number of people who pledged.

.. epigraph::
   🪙 784,957 Monero - 13,623 supporters

Gaming server
-------------

AssaultCube CLA versus RVSF playing Capture The Flag.

Game name; rivals; and score.

.. epigraph::
   CTF: 🔴 １５ 🔵 １９

.. epigraph::
   CLA: １５; RVSF: １９ (CTF)

AssaultCube statistics.

Sum of player; and sum of spectators.

.. epigraph::
   8578 (37 spectators)

Gathering quorum
----------------

Current number of expected attendeed; and pastor name.

.. epigraph::
   47 attendeed - Peter J. Fuentes

IP address check
----------------

Protocol version; and address.

.. epigraph::
   IPv4: 127.0.0.1

IRC channel
-----------

Number of participants.

.. epigraph::
   362 participants

MOTD
----

Message of the day.

.. epigraph::
   Deyr fé deyja frændr deyr sjálfr it sama ek veit einn at aldri deyr dómr um
   dauðan hvern.

   -- Hávamál v78

News site
---------

Programme name; and latest headline.

.. epigraph::
   NLnet NGI0: A succesful experiment of a homebrew printed RISC-V processor

Poll
----

.. epigraph::
   Left 38:62 Right

Product for sale
----------------

Product name; current price; and availability.

.. epigraph::
   MNT Reform - $430 - 608 units in stock

Profile
-------

Contact name; activity (XEP-0108); and mood (XEP-0107).

.. epigraph::
   Erika: ⛷ skiing - 🤨 serious

Rating
------

Rating level.

.. epigraph::
   🌟🌟🌟🌟⭐

Risk alert
----------

District name; danger level, or type; details about danger; and advisory.

.. epigraph::
   PE: 🚗 1 car accident - 0 casualties

.. epigraph::
   PH: 🚨 7 armed drones - 4 casualties - remain underground

.. epigraph::
   SN: 🔥 2 square miles - 0 casualties - escapement from road 41

.. epigraph::
   TX: 🌊 4 square miles - 30 missing - escapement from Mount Clara

Stock quote
-----------

Stock price and movement.

.. epigraph::
   MNT: 732.74 + 0.15 ⬆

Streaming server
----------------

MPD currently played concerto.

.. epigraph::
   🎼 Antonio Vivaldi - Autunno - Adagio molto

Icecast currently played show.

.. epigraph::
   🎙 Tales from Babylon - Military Disability

Support ticket
--------------

Ticket number; status; owner; and ETA.

.. epigraph::
   ConverseJS - In progress - JCBrand - ETA: 4 days 3 hours

System monitor
--------------

Component name; temperature; and current state.

.. epigraph::
   CPU: 🟡 25℃ (working)

.. epigraph::
   CPU: 🔴 75℃ (critical)

Component name; I/O rate; and current state.

.. epigraph::
   Disk: Reading: 🟢 4KiB/s (routine) - Writing: 🟠 35MiB/s (high)

Turnament
---------

Game icon; player name; current scores; and player name.

.. epigraph::
   🎾 Mike 🯷🯱 - 🯸🯴 Doug

Current place; and racer name.

.. epigraph::
   1st: Mike.C - 2nd: Doug.O - 3rd: Lee.R - 4th: Hal.A

Version check
-------------

Software name; and version number.

.. epigraph::
   💡 Gajim - version 0.16.1

Recent title of slackware.com site.

.. epigraph::
   🐧 Slackware 15.0 is released!

Viking word of the day
----------------------

Norse word of the day.

.. epigraph::
   📑 Vindauga	(lit. “wind-eye”)

Weather report
--------------

Country name; temperature; and current forecast.

.. epigraph::
   PA: 🌤 25℃ (mostly sunny)

Conclusion
``````````

Typically, a bookmark title will be the page title and will not change.

Dynamic titles offer automatically updating bookmark titles of specific
information of a given page.

For example, if you were bookmarking an online auction, the title might inform
you of the current highest bid and the period of time for which the auction will
be open for.

In that manner, you do not have to keep visiting the site to see that
information, and, instead, you can gaze at a bookmark (dynamic) title, and by
that to have subtle updates about occasional concerns.

Microsummaries are helpful, useful, and cheap to maintain.

Post script
```````````

While microsummaries were initially made for bookmarks, they are also usable for
dashboards, desktops and other software of other types and environments.
