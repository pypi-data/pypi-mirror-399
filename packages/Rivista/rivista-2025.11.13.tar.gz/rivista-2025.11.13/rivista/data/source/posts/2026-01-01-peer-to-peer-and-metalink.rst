.. author:
   name,uri
   Schimon Jehudah Zachary, xmpp:sch@pimux.de?message
.. category:
   label, term, scheme
   BitTorrent, bittorrent, protocol
   eDonkey2000, ed2k, protocol
   easyMule, easymule, software
   File ID, file-id, practice
   Gnutella, gnutella, protocol
   ID, id, practice
   Identifier, identifier, practice
   IPFS, ipfs, protocol
   KGet, kget, software
   Metadata, metadata, concern
   Metalink, metalink, filetype
   MUTE, mute, software
   Peer-to-peer, p2p, concern
   Phex, phex, software
   Peer-to-peer network, ppn, concern
   RetroShare, retroshare, software
   VeryCD, verycd, brand
.. id: 2026-01-01-peer-to-peer-and-metalink
.. published: 2026-01-01 0:00:00 UTC
.. summary:
   P2P systems must be designed to distribute content based on file-identifier.
   In contrast to the practice of mandatory metadata-identifier, the practice
   of file-identifier is sustainable, and it ensures the preservation and
   further distribution of contents, whereas Metalink would be utilized to
   provide the functionality to distribute multiple files at once, and across
   several protocols.
   The purpose of handling of multiple files at once should be chiefly reserved
   to Metalink.
.. link: 2026-01-01-peer-to-peer-and-metalink
.. links:
   title,href,rel
   Metalinker.org - Why Metalink?, https://metalinker.org/why.html, related
   "Metalinker: Integrating HTTP, FTP and P2P", https://torrentfreak.com/metalinker-integrating-http-ftp-and-p2p/, related
   Metalink @ Packages Resources, http://metalink.packages.ro, related
   Shareaza Wiki, https://shareaza.sourceforge.net/mediawiki/Main_Page, related
   Gnutella2 Developer Network, https://g2.doxu.org, related
   Bit Torrent, http://bitconjurer.org/BitTorrent/, related
.. title: Peer-to-Peer and Metalink
.. type: text

.. figure:: /graphics/metalink.svg
   :alt: Metalink
   :height: 150px
   :loading: lazy
   :target: /graphics/metalink.svg
   :width: 150px

A Peer-to-Peer Network, is a network of machines that interact as equals
(peers). It is different from ‘traditional’, server-centric networks in that
there is no central point of control that is ‘in charge’ of a network.

P2P networks are resilient, and difficult to forcibly shut down or restrict, yet
easy to establish without having to invest large sums of money in servers.

Decentralized content transfer protocols (henceforth “P2P”), such as Advanced
Direct Connect, BitTorrent, Direct Connect, eDonkey2000, Gnutella, Gnutella2,
Hypercore, IPFS, MUTE, OpenFastTrack, OpenFT, and Overnet, are designed for
copying files from one machine to another.

P2P protocols are better than centralized content transfer protocols, such as
FTP, Gemini, HTTP, Telnet, SSH, and XMPP, because centralized protocols
“punish”, so to speak, sites for being popular. Since the serving (uploading) of
contents is done from one place, popular sites need enormous machines and ample
bandwidth.

With P2P, clients automatically mirror files that they download, making the
burden of publishers almost insignificant. Since every publisher can distribute
millions of copies of a CD image a day over an ordinary DSL line, by having the
rest of the people to ‘serve’ (upload) the copies for the publisher.

BitTorrent and IPFS versus eDonkey2000 and Gnutella
---------------------------------------------------

BitTorrent has ‘metainfo’ and IPFS has ‘CID’ as metadata files, for the
indexing and distribution of contents.

BitTorrent and IPFS utilize metadata files for the indexing, distribution, and
verification of contents; Torrent (‘metainfo’) for BitTorrent, and CID for IPFS.

eDonkey2000 and Gnutella utilize file identifiers for the indexing,
distribution, and verification of contents; MD4 for eDonkey2000, and SHA-1 for
Gnutella. Gnutella employs the “Tiger tree hash” for the distribution of
content.

Metainfo
--------

The practice of metadata files is not bad, even when it is not standard (i.e.
Metalink), but it is bad for metadata file to be compulsory, as it means further
dependence.

Dependency
``````````

Since the practice of metadata files is compulsory in BitTorrent and IPFS, there
is a redundant, unnecessary and mandatory reliance on metadata files. This
means, that the distribution of contents over BitTorrent or IPFS relies on the
existence of metadata files, and therefore this reliance is unsteady, because in
a circumstance when no one has a certain metadata file, even when the content
files, that where listed in that metadata file, are located on millions of
machines, it would not be possible to retrieve any of those content files due to
the reliance on a metadata file.

Fixed structure
```````````````

Additionally, because metadata files enforce a structure of content files which
are indexed, the practice of compulsory metadata files, thereby, coerces people,
who want to further distribute files over BitTorrent or IPFS, to save copies of
metadata files (i.e. Torrent files) and also to maintain the same structure of
files as they appear in the arrayal index of subject metadata files, often by
creating redundant copies of the same files due to several metadata files that
index the same files in a different array.

Fixed filenames
```````````````

Further more, when file naming practice changes, either by consent (e.g.
replacing white-spaces by periods), or by constrains (disallowing characters),
then it would void some of the indexed files of some metadata files and
subsequently prevent the further distribution of files.

Consequently, whether by choice or otherwise, people will cease from
distributing some files, either because they do not know or are not interested
to save and manage metadata (e.g. Torrent) files, or because of constrains of
storage, or difficulties to manage multiple metadata files of the same content
files with different structures, or due to switching to a new software (e.g.
from Deluge Torrent to qBittorrent), especially when one has hundreds or event
thousands of completed and active transactions.

Some of these problems could be mitigated by adding Metainfo management
functionalities to software, yet such functionalities will not constitute a
sustainable solution.

Solidified pieces
`````````````````

Another significant problem with BitTorrent, is that thre is no segregation of
file, so it is impossible to download chosen files of a Torrent, without
downloading other files, because the indexed data chunks are mixed (i.e.
‘intertwined’, so to speak) with one another, and are not properly segmented.

Uncorrectability
````````````````

And most importantly, as mandatory metadata files are fixated, correctability is
impossible; that is, indexed content has its own checksum hash identifier, and
when that index is modified, the checksum hash identifier changes also.

Suppose of a metadata file which contains musical creations of Ludwig van
Beethoven, and then it appears that there are a couple of missing files;
changing the index would create a new metadata file and it would be needed to
share it again, and inform the people who has the older metadata file to switch
to the newer metadata file; however, that older metadata file could already be
distributed by millions of people, so it would be a difficult task to neglect
the older metadata file in favour of the new one.

Furthermore, suppose that a multimedia content is distributed and people are
interested in subtitles of their own languages; it would be impossible to do so,
as every metadata file of every set of subject multimedia file and related
subtitles file be different.

This is why mandatory metadata files should be neglected in favour of Metalink;
because, adaptivity and correctability is possible with Metalink, and is one of
the prominent reasons that Metalink is important.

FileID
------

eDonkey2000 and Gnutella software distribute and verify files by their checksum
hash; MD4 and SHA-1, respectively. Checksums are unique to every file.

The practice of file-identifier is convenient and flexible, because it enables
to specify directories to index for distribution (e.g. articles, books, images,
music, videos, et cetera), and to arrange files as desired, without being bound
to a specific array of files and directories.

Subsequently, content over networks which utilize the practice of FileID,
sustains for a longer period of time, and, practically, forever.

The only benefit that IPFS and BitTorrent have over protocols that identify
content by File ID, rather than by metadata file, is allowing the sharing of
a cluster of files.

Nevertheless, this benefit can also be available for protocols that utilize File
ID, using Metalink.

Metalink enables for eDonkey2000, Gnutella, and MUTE software to offer further
Versatility by being a modular component, and by that to offer the choice to
either utilize a singular file model, a routine mechanism, or multiple files, by
utilizing the Metalink framework.

Metalink
--------

Metalink is an internet framework which is designed to accelerate and facilitate
the downloading of data in a reliable and secure manner. It circumscribes both
types of downloading methods; from centralized protocols, such as FTP, Gemini,
Gopher, and HTTP, to decentralized protocols, such as BitTorrent, eDonkey2000,
Gnutella, and MUTE.

Metalink substitutes static links with an XML file `.metalink`, which contains
locations of sources of a singular file or of multiple files. In addition to
FTP, HTTP, and RSYNC sources, Metalink can be utilized with P2P methods,
including BitTorrent, eDonkey2000, Gnutella2, and MUTE.

Files that are downloaded with Metalink are automatically verified, and it is
possible to utilize any type of checksum as well as PGP signatures with
Metalink, in order to verify contents.

If an error occurs during transfer, or if content was intentionally (i.e.
maliciously) altered, the checksums will not match.

When an error happens with centralized content delivery methods, it would be
necessary to download the subject content again. However, with Metalink, if the
`.metalink` file of a subject content includes a security checksum or a Torrent,
software that utilize Metalink can use the specified checksum or the Torrent
file to verify content integrity; and if only a certain part (i.e. ‘chunk’) of a
subject content has errors, then only that specific part be downloaded, instead
of the whole file.

Comparison
----------

In this table “Metainfo” represents BitTorrent and IPFS.

=========== ======== ======= ========
Concern     Metainfo FileID  Metalink
=========== ======== ======= ========
Cluster     Yes      Yes ¹   Yes
Correctable No       Yes     Yes
Metadata    Yes      Yes ²   Yes
Optional    No ³     Yes     Yes
Segregation No ⁴     Yes     Yes
Versatility No ⁵     Yes     Yes
=========== ======== ======= ========

Notes
`````

1. File clustering is possible with Metalink.
2. Metadata is optional and feasible with Metalink.
3. Metainfo is a mandatory requirement which is needed to locate content.
4. Chunks of indexed files are mixed together, so it is impossible to
   selectively download chosen contents without partially downloading other
   contents.
5. Fixed filenames and structure that can not be otherwise adapted.

State of affairs
----------------

Files that were distributed since the public inception of eDonkey2000 are still
available over eDonkey2000, whereas most of the files that were distributed
since the public inception of BitTorrent are often expire after a decade or so,
and new metadata files have to be created, and then published, in the hope that
those who attempt to download by the void metadata file would know where to find
the new metadata file.

Conclusion
----------

The protocols BitTorrent and IPFS should be designed to distribute content based
on singular files, as eDonkey2000 and Gnutella do, whereas Metalink could and
should be utilized as a chief mean to enable the distribution of multiple files
at once, and accross different P2P systems.
