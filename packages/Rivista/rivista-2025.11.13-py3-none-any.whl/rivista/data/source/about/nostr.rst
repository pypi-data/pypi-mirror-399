.. category:
   label, term, scheme
   Nostr, nostr, protocol
   Publishing, publishing, concern
   Syndication, syndication, technology
.. id: nostr
.. link: nostr
.. links:
   title,href,rel
   The logo of the protocol Nostr, /graphics/nostr.svg, avatar, image/svg+xml
   A presentation about Nostr by Mr. Wouter Constant, https://video.fosdem.org/2025/k1105/fosdem-2025-6452-nostr-notes-and-other-stuff-transmitted-by-relays.av1.webm, enclosure
   nostr.org, https://nostr.org, related
   nostr.net, https://nostr.net, related
   start.njump.me, https://start.njump.me, related
   nips.nostr.com, https://nips.nostr.com, related
   nostrapps.com, https://nostrapps.com, related
   "FOSDEM 2025 - Nostr, notes and other stuff transmitted by relays", https://fosdem.org/2025/schedule/event/fosdem-2025-6452-nostr-notes-and-other-stuff-transmitted-by-relays/, related
   The first public announcement of Nostr, https://fiatjaf.com/nostr.html, related
.. published: 2019-11-20 00:00:00 UTC
.. summary:
   Notes and Other Stuff Transmitted by Relays.
   The simplest open protocol that is able to create a censorship-resistant
   world collaborative (i.e. "social") network once and for all.
   It does not rely on any trusted central server, hence it is resilient; it is
   based on cryptographic keys and signatures, so it is tamperproof; it does not
   rely on P2P techniques, therefore it works.
.. title: Nostr
.. type: text

Nostr is an open protocol for censorship resistant publication and collaborative
(i.e. "social") networking.

Nostr reverses the paradigm of "dumb client/smart server" to "smart client/dumb
server", by utilizing relays and public-key cryptography.

Ownership
---------

Be your own content curator, interact with people from across the world, and
discover your niche communities.

Without a forced secretive and closed-source algorithm, your home feed is based
on your subscriptions (i.e. "follows") and interests.

Choice
------

There is no central server, so Alice can send her notes to any servers of her
choice.

Bob can run a server and set his own rules. People may utilize his relay, if
they prefer his relay services, or just fetch specific notes.

Security
--------

Instead of using insecure passwords, all messages are signed using cryptography.
You can verify messages and authenticity without relying on a centralized
component.

Technicality
------------

This is a short summary of how it work:

Everybody runs a client, either native, HTML, or otherwise;
To publish content, you write a post, sign it with your key, and send it to
multiple relays (servers hosted by someone else, or yourself);
To receive updates from other people, you ask multiple relays if they have
information about these people;
Anyone can run a relay;
A relay is fundamentaly simple;
A relay only intermediates by receiving posts from some people and forwarding
them to others;
Relays do not have to be trusted; and
Signatures are verified over client side.

Conclusion
----------

Signed at the core. Nostr empowers people to control their own data. You own
your Nostr.

Post script
-----------

This is a statement which was published over a couple of decades before Nostr
was invented.

.. epigraph::

   Hosted filesystems exist today which are nearly totally robust and reliable
   and online 99.99x% of the time -- and at very low cost.

   If these storages, and public key encryption, had been available 20 years
   ago, SMTP, POP3, and HTTP would never have been invented, nor SQL RDBMSs, in
   their present forms.

   Certainly, their markets would have been much smaller.

   -- Todd Boyle CPA (General Ledger Dialtone)
