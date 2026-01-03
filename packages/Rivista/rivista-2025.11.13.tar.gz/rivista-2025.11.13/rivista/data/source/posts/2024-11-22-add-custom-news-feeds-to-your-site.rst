.. author:
   name,uri
   Schimon Jehudah Zachary, xmpp:sch@pimux.de?message
.. category:
   label, term, scheme
   Atom, atom, filetype
   HTML, html, filetype
   JSON, json, filetype
   RDF, rdf, filetype
   RSS, rss, filetype
   Server, server, concern
   Syndication, syndication, technology
   Tutorial, tutorial, concern
   Twtxt, twtxt, filetype
   XMPP, xmpp, protocol
.. id: 2024-11-22-add-custom-news-feeds-to-your-site
.. published: 2024-11-22 0:00:00 UTC
.. summary:
   If you want to set your RSS feeds to be auto-discoverable; and you utilize
   XMPP, Twtxt, OStatus, or ActivityPub with services such as Akkoma, Mitra, GNU
   Social, Mbin, Mitra, Movim, StatusNet, Pleroma, SoapBox or others; then you
   can use your respective syndication feed of your publishing accounts at your
   own homesite, by adding metadata directives.
.. link: 2024-11-22-add-custom-news-feeds-to-your-site
.. links:
   title,href,rel
   The logo of RSS, /graphics/rss.svg, avatar
   RSS Autodiscovery, https://rssboard.org/rss-autodiscovery, related
   RFC 4287: The Atom Syndication Format, https://rfc-editor.org/rfc/rfc4287, related
.. title: Add custom news feeds to your site
.. type: text

Consult with this tutorial in order for you to utilize any syndication feed as
an automated content and news source at your HTML site, by adding
Autodiscoverability directives to HTML metadata.

While any of codes of this tutorial would work, it is recommended to use the
code with the proper "type" attribute in respect to the type of feed which you
want to add; and attribute "title" may be customized as you desire.

You are not limited to your ActivityPub, OStatus, or XMPP accounts, and you can
also add any source of any other account and type.

Atom
````

.. code:: xml

   <link href="gemini://path/to/feed.atom"
         rel="alternate"
         title="Atom Syndication Format"
         type="application/atom+xml" />

* Recommended.
* Standard (RFC 4287).
* Transformable with XSLT.

Gemini
``````

.. code:: xml

   <link href="gemini://path/to/feed.gmi"
         rel="alternate"
         title="Gemini Feed"
         type="text/gemini" />

* Recommended.

JSON
````

.. code:: xml

   <link href="https://path/to/feed.json"
         rel="alternate"
         title="JSON Feed"
         type="application/json" />

* Not encouraged.

RDF
```

.. code:: xml

   <link href="ftps://path/to/schema.rdf"
         rel="alternate"
         title="Resource Description Framework"
         type="application/rdf+xml" />

* When applicable.
* RDF is mostly utilized for datasets.

RSS
```

.. code:: xml

   <link href="https://path/to/summary.rss"
         rel="alternate"
         title="RDF Site Summary"
         type="application/rss+xml" />

* Discouraged.
* Not standard.

Twtxt
`````

.. code:: xml

   <link href="gopher://path/to/tw.txt"
         rel="alternate"
         title="Twtxt"
         type="text/twtxt+plain" />

* Standard.
* Encouranged.

XMPP
````

.. code:: xml

   <link href="xmpp:pubsub.jabber.org?;node=news"
         rel="alternate"
         title="Atom Over XMPP"
         type="application/atom+xml" />

* Recommended.
* Standard (RFC 4287).
* P2P automated.
