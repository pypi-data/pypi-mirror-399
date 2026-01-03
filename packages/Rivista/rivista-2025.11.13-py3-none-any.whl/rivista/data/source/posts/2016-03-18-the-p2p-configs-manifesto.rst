.. author:
   name,uri
   axet, https://axet.gitlab.io
.. category:
   label, term, scheme
   BitTorrent, bittorrent, protocol
   BTSync, btsync, software
   DC++, dcpp, software
   eDonkey2000, ed2k, protocol
   Encryption, encryption, concern
   Gnutella, gnutella, protocol
   Peer-to-peer, p2p, technology
   Peer-to-peer network, ppn, concern
   Telecommunication, telecommunication, concern
   Syndication, syndication, technology
   VoIP, voip, technology
.. id: 2016-03-18-the-p2p-configs-manifesto
.. link: 2016-03-18-the-p2p-configs-manifesto
.. source-title: p2p-configs
.. source-link: https://gitlab.com/axet/p2p-configs
.. source-updated: 2016-03-18 0:00:00 UTC
.. links:
   title,href,rel,type
   p2p-configs, https://gitlab.com/axet/p2p-configs, related, text/html
   comments, https://gitlab.com/axet/p2p-configs/-/issues, replies, text/html
   P2P, /graphics/p2p.svg, avatar, image/svg+xml
   p2p-share: DC++, https://dcpp.wordpress.com, related, text/html
   p2p-share: eMule, https://emule-project.com, related, text/html
   p2p-share: GTK-GNUTELLA, https://gtk-gnutella.sourceforge.net, related, text/html
   p2p-share: MLDonkey, https://mldonkey.sourceforge.net, related, text/html
   p2p-share: Notes, https://gitlab.com/axet/notes, related, text/html
   p2p-share: qBittorrent, https://qbittorrent.org, related, text/html
   p2p-share: Retroshare, https://retroshare.cc, related, text/html
   p2p-share: Shareaza, https://shareaza.sourceforge.net, related, text/html
   p2p-share: Syncthing, https://syncthing.net, related, text/html
   p2p-text: Jami, https://jami.net, related, text/html
   p2p-text: LXMF, https://unsigned.io/website/software/LXMF.html, related, text/html
   p2p-text: Nostr, https://nostr.com, related, text/html
   p2p-text: Tox, https://tox.chat, related, text/html
   p2p-text: Bitmessage, https://bitmessage.org, related, text/html
   "No server is needed: Bitmessage, LXMF, Nostr, and Syncthing", 2024-06-09-no-server-is-needed-bitmessage-lxmf-nostr-and-syncthing, related
.. published: 2016-03-18 0:00:00 UTC
.. rights:
   This article was published in the year of 2016, without any licensing
   information; it is presumed, therefor, that this content is currently
   copyrighted to "axet", and copying of this document is prohibited by others.
.. summary: The future of the internet.
.. title: The p2p-configs manifesto
.. type: text

I see no future for REST internet. I see no future for “Cloud Internet”.

Internet is currently under heavy assault from government. And government
control is growing over years. People can't share content. Right now you can be
targeted as individual for sharing a movie or music file. People restricted to
create content. You can't create screencasts and share it among your listeners
without taking a risk been prosecuted by companies calming rights for your
content.

It is clear we need to change it.

I'd like to see more people involved in developing P2P Internet. Where you have
IP's bans, no DNS related issues.

We can turn the sides from been pirates to new government who rules the internet
in online and offline in real live.

Just imagine a nice open-source application, which can operate on desktop
machine or mobile phone. After starting it you can find content by using QR code
or secret ID to find a subscription.

This content provided by person who is holding it's private key and uploading
content to everyone who has a public key (ID or QR code). Content provided by
this person is encrypted. Only if you have a key you can decrypt it. Content can
be automatically decrypted if subscriber feed author allows it to be public. To
obtain decrypted key you can pay a Monero token to subscriber feed author and he
will send it using a P2P message. You can immediately decrypt the content and
reshare it using new encryption key (yours) so you start to earn money from P2P
users if they agrees to download it from you and pay you.

Everyone who is downloading content from this subscription peer is also sharing
it so everyone boost the most popular content to speed it up (yes, just as it
occurs over BitTorrent).

You can download a file just knowing it secret (i.e. Universal ID).

It also works offline! If you already have a content you can watch it, read it,
or share in the private network not connected to world internet.

You can tag the content. Just by browsing internet you allowed to cache it's
content and assign an unique ID so it would be easy to create your own
Subscriber Feed and share content among your subscribers.

As you can see commercial also works here. You can share content with you ads.

It is compatible with old web based internet. You can continue browsing
government or business controlled internet to follow the links or read another
lie from your president.

What I deeem to be important to implement
`````````````````````````````````````````

P2P Configs
-----------

This is project will help you to store your application data in the private P2P
cloud. If you lose your notebook, you can restore the data from your automatic
backup archive created by P2P Configs service operated on your home router. Or
you reading a book from your mobile phone using Read P2P Configs application,
which also operated on your desktop machine. Current page should be synced back
to your desktop, avoiding any centralized cloud based (spying) software.

Every application instance has it's id, which holds the configuration.
Configuration based on tree structure like git goes. And when you create
conflict parameter change or current application keeps two values. It maybe
useful with different download folder parameter for each application instance on
each device. So, parameters should have special types and different resolve
logic (one shloud replace latest by it's date, another, keep two values
separateley for two devices).

P2P Share
---------

A universal engine which combines BitTorrent functionality, eDonkey2000
protocol, DC++, BTSync. Place where you can create share, download content, and
subscribe.

P2P Text
--------

Send or read an email or engage in a video call.
