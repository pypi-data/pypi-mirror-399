.. category:
   label, term, scheme
   Atom, atom, filetype
   News, news, concern
   RDF, rdf, filetype
   Twtxt, twtxt, filetype
   RSS, rss, filetype
   Syndication, syndication, technology
.. id: twtxt
.. link: twtxt
.. links:
   title,href,rel
   The logo of Twtxt, /graphics/twtxt.svg, avatar, image/svg+xml
   Homesite, https://twtxt.dev, related
   Delightful Twtxt, https://delightful.coding.social/delightful-twtxt/, related
.. published: 2025-07-14 00:00:00 UTC
.. summary: A minimalist, plain-text publishing format that is simple to use and realize.
.. title: Twtxt
.. type: text

Twtxt is a minimalist, plain-text publishing format that is simple to use and
realize.

Mechanism
---------

Twtxt operates via simple text files called "feeds," each containing a user's
status updates. These files are typically served by content delivery servers,
such as FTP, Gemini, Gopher, and HTTP; and made accessible through a URL (e.g.
`https://example.com/twtxt.txt`).

Extensions
----------

It is possible to extend the functionalities of Twtxt by incorporating
`Twt extensions <https://twtxt.dev/extensions.html>`_.

File format
-----------

A Twtxt feed contains one status update per line. Each line starts with an
`RFC3339 <https://datatracker.ietf.org/doc/html/rfc3339>`_ date-time string
(with or without a UTC offset), followed by a TAB character (`\t`) that
separates it from the actual text (it is recommended to append new statuses to
the end of the file).

The file must be UTF-8 encoded and use LF (`\n`) as line separators.

A feed typically begins with metadata, which might include the user's preferred
nickname, an avatar, and an optional description. It is recommended to separate
metadata from statuses by a blank line.

Interaction
-----------

Interactions with mentions and threads.

Mentions in the text take one of two forms: `@<source.nick source.url>` or
`@<source.url>`. These should be expanded by the client when rendering the Twts.
The `source.url` helps discover new feeds and distinguish between users with the
same nickname on the same domain. The `source.url` can be interpreted as a Twtxt
URI.

Threads are represented using subjects, which are written in the format
`(<subject>)` at the start of a Twt. For precise threading, content-based
addressing identifies individual Twts in a feed.
Explore the `Twt Hash <https://twtxt.dev/exts/2020-12-11-Twt-Hash.html>`_
extension for more details.

Participation in a thread is simple: reply by copying the Twt Subject into a new
Twt. A Twt Hash is a Blake2b hash, base32 encoded without padding, converted to
all lowercase letters and shortened to the last 7 characters.
The hash is calculated from the content `<url>\n<timestamp>\n<text>`.

For example:

.. code:: bash

   $ printf '%s\n%s\n%s' \
     'https://example.com/twtxt.txt' '2024-09-29T13:30:00Z' 'Hello World!' \
     | b2sum -l 256 | awk '{ print $1 }' | xxd -r -p | base32 \
     | tr -d '=' | tr 'A-Z' 'a-z' | tail -c 8
   ohmmloa

Example feed
------------

Below is an example of a Twtxt feed:

.. code::

   # nick        = example
   # url         = https://example.com/twtxt.txt
   # avatar      = https://example.com/avatar.png
   # description = An example feed

   2024-09-29T13:30:00Z   Hello World!
   2024-09-29T13:40:00Z   (#ohmmloa) Is anyone alive? 🤔

.. epigraph::

   Syndicated technologies embody of what free and open telecommunication should
   really be, a truely free-speech-driven telecommunication and publishing
   international system.

   -- Alex J. Anderson
