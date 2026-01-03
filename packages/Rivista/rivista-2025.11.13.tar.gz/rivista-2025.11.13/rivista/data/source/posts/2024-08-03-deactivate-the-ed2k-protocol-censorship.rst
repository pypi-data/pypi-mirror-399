.. author:
   name,uri
   Schimon Jehudah Zachary, xmpp:sch@pimux.de?message
.. published: 2016-03-18 0:00:00 UTC
.. summary: Use this tutorial to enable eD2k links.
   There is a coordinated effort by some vendors of HTTP browsers to try to
   suppress useful protocols, such as of eDonkey2000.
   They do not want us to enjoy protocols that actually contribute to our daily
   lives; that do not advertise to us to buy things that we do not want nor
   need; that do not tell us what to buy; that do not ask us to confirm whether
   or not our software is automated, as if it is something that anyone should
   know of.
.. link: 2024-08-03-deactivate-the-ed2k-protocol-censorship
.. links:
   title,href,rel
   No server is needed: Bitmessage, LXMF, Nostr, and Syncthing, 2024-06-09-no-server-is-needed-bitmessage-lxmf-nostr-and-syncthing, related
   ed2k link no longer work for aMule - FirstLoveMovies, https://www.first-loves.net/forums/viewtopic.php?style=2&t=16299, related
   link ed2k non funzionano? – ecco la soluzione, https://www.giuseppefava.com/link-ed2k-non-funzionano-ecco-la-soluzione/, related
.. id: 2024-08-03-deactivate-the-ed2k-protocol-censorship
.. category:
   label, term, scheme
   aMule, amule, software
   Bitlord, bitlord, software
   Dream Mule, dream-mule, software
   easyMule, easymule, software
   eDonkey2000, ed2k, protocol
   eMule, emule, software
   Hydranode, hydranode, software
   KaMule, kamule, software
   KMLDonkey, kmldonkey, software
   MLDonkey, mldonkey, software
   Morpheus, morpheus, software
   Peer-to-peer, p2p, concern
   Quazaa, quazaa, software
   Razorback, razorback, software
   Shareaza, shareaza, software
   TitanMule, titanmule, software
   VeryCD, verycd, brand
   Xtreme, xtreme, software
.. title: Deactivate the eD2k protocol censorship
.. type: text

.. figure:: /graphics/emule.svg
   :alt: eMule
   :class: drop-shadow
   :height: 150px
   :loading: lazy
   :target: /graphics/emule.svg
   :width: 150px

   The mascot of eMule.

Blink
-----

Utilize this argument parameter to start browser without censorship.

.. code::

   --disable-features=StandardCompliantNonSpecialSchemeURLParsing

Gecko
-----

* Open URI `about:config` in the address bar;

* Search for key `network.url.useDefaultURI`;

* Set the value of key `network.url.useDefaultURI` to `false`; and

* Restart your HTTP browser.
