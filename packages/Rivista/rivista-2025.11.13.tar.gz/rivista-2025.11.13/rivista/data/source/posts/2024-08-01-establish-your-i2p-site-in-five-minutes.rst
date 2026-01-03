.. author:
   name,uri
   Schimon Jehudah Zachary, xmpp:sch@pimux.de?message
.. published: 2024-08-01 0:00:00 UTC
.. summary:
   This is a concise tutorial for establishing an I2P website.
   I2P is a communication system which behaves similarly to PPN (Peer-to-peer
   network), and particularly to the technology of DHT (Kademlia).
   It allows to communicate with anyone over I2P only, and you decide how you
   want to communicate.
   You can communicate data over BitTorrent, DeltaChat, eDonkey2000, Email, FTP,
   Gemini, Gnutella, Gopher, HTTP, IPFS, IRC, MQTT, MUTE, SSH, Telnet, XMPP, et
   cetera, on top of I2P.
   Be a landlord over the internet.
.. link: 2024-08-01-establish-your-i2p-site-in-five-minutes
.. links:
   title,href,rel
   Get a Website Now! Do not be a Web Peasant!, 2020-06-30-get-a-website-now-do-not-be-a-web-peasant, previous
   Gnutella2 and internet publications, 2026-01-01-gnutella2-and-internet-publications, next
   Research Confirms the Reliability of the I2P Network, https://diva.exchange/en/privacy/research-confirms-the-reliability-of-the-i2p-network/, related
   I2Pd tunnels configuration, tunnels.conf, enclosure
   I2Pd configuration, i2pd.conf, enclosure
   i2pd.website, https://i2pd.website, related
   i2pd.xyz, https://i2pd.xyz, related
   i2pd.i2p, http://i2pd.i2p, related
   Configuring i2pd, https://i2pd.readthedocs.io/en/latest/user-guide/configuration/, related
   Anonymous sites, https://i2pd.readthedocs.io/en/latest/tutorials/http/#host-anonymous-website, related
   Setting up I2P with Nginx, https://landchad.net/i2p/, related
   Anonymous IRC chats, https://i2pd.readthedocs.io/en/latest/tutorials/irc/, related
   Decentralized XMPP instant messenger, https://i2pd.readthedocs.io/en/latest/tutorials/xmpp/, related
   Selfhosting Your Own I2P XMPP Server, http://righttoprivacy.i2p/selfhosting-your-own-i2p-xmpp-server/, related
   Anonymous filesharing, https://i2pd.readthedocs.io/en/latest/tutorials/filesharing/, related
   Using RetroShare with I2P, https://i2pd.readthedocs.io/en/latest/tutorials/retroshare/, related
   Using eMule with I2P, https://forum.emule-project.net/index.php?showtopic=166889, related
   I2P Info Archive, https://strict3443.codeberg.page/i2p-info/hugo/public/archives/, related
   PurpleTe.ch, https://purplete.ch, related
.. id: 2024-08-01-establish-your-i2p-site-in-five-minutes
.. category:
   label, term, scheme
   Computer, computer, concern
   I2P, i2p, network
   Meshnet, meshnet, practice
   Mixnet, mixnet, practice
   Self Host, self-host, practice
   Server, server, concern
   Service, service, concern
   Tutorial, tutorial, concern
   Website, website, medium
.. title: Establish your I2P site in five minutes
.. type: text

.. image:: /graphics/i2p.svg
   :alt: I2P
   :class: drop-shadow
   :height: 150px
   :loading: lazy
   :target: /graphics/i2p.svg
   :width: 150px

This is an introductory tutorial for starting your own I2P service from any
computer and any type of network.

If you already have i2pd installed, then you probably can start from
`Phase 3 <#phase-3-start-a-server>`_ (start a server).

Phase 1 - Install i2pd
----------------------

Download and install i2pd.

`i2pd.website <https://i2pd.website>`_

`i2pd.xyz <https://i2pd.xyz>`_

If you are using Linux, as we hope that you do, then you can install i2pd from
your package manager, or software repository, or app store.

Phase 2 - Configure i2pd
------------------------

This phase is intended for you to slightly understand how I2PD works on your
machine.

You do not need to manually create i2pd folder;

You can install the official package and it will come with a pre-configured
config files.

You can skip this phase; or

Create a directory `~/.i2pd/` and configure a tunnel and i2pd.

Tunnel
``````

Create file `~/.i2pd/tunnels.conf` and add this content.

.. code:: ini

   [anon-website]
   type = http
   host = 127.0.0.1
   port = 8000
   keys = anon-website.dat

Configuration
`````````````

Copy file `/etc/i2pd/i2pd.conf` to `~/.i2pd/i2pd.conf`, and set the following
options; or

Create file `~/.i2pd/i2pd.conf` and add this content.

.. code:: ini

   daemon = false
   ipv4 = true
   ipv6 = true

   [reseed]
   verify = true
   urls = https://reseed.i2p-projekt.de/,https://i2p.mooo.com/netDb/,https://netdb.i2p2.no/

   [addressbook]
   defaulturl = http://shx5vqsw7usdaunyzr2qmes2fq37oumybpudrd4jjj4e4vk4uusa.b32.i2p/hosts.txt
   subscriptions = http://reg.i2p/hosts.txt,http://identiguy.i2p/hosts.txt,http://stats.i2p/cgi-bin/newhosts.txt

Post script
```````````

This is a basic configuration file which is intend for this tutorials so you
would be able to observe that you are able to run your own I2P service.

You are encouraged to read the complete set of options which is available at
`/etc/i2pd/i2pd.conf`.

Phase 3 - Start a server
------------------------

Start an HTTP server at port 8000.

.. code::

   python -m http.server

Execute I2P

.. code::

   i2pd

Phase 4 - Discover your public address
--------------------------------------

Open i2pd webconsole, and navigate to menu I2P tunnels.

`I2P tunnels <http://127.0.0.1:7070/?page=i2p_tunnels>`_

Copy the hostname of "anon-website" under the title "Server Tunnels".

Example:

.. code::

   anon-website ⇒ abcdefghijklmnopqrstuvwxyz12345678900987654321zyxwvu.b32.i2p:8000

Hostname:

.. code::

   bcdefghijklmnopqrstuvwxyz12345678900987654321zyxwvu.b32.i2p:8000

URL:

.. code::

   http://bcdefghijklmnopqrstuvwxyz12345678900987654321zyxwvu.b32.i2p

Phase 5 - Register an address (optional)
----------------------------------------

This phase id optional, and is meant for you, if you want to have a custom
address (e.g. YourCustomAddress.i2p).

Click on the hyperlink "anon-website".

You will then be referred to this URL.

.. code::

   http://127.0.0.1:7070/?page=local_destination&b32=bcdefghijklmnopqrstuvwxyz12345678900987654321zyxwvu

Click on "Address registration line".

Set a desired domain name.

Note: result string can be used only for registering 2LD domains (example.i2p).
For registering subdomains, please use `i2pd-tools`.

You will then be referred to a page which would read "SUCCESS" and be advised to
register at reg.i2p site.

PLEASE COPY AND SAVE THE INFORMATION OF THE TEXT FIELD.

Set a desired description up to 64 characters.

You will then be referred to reg.i2p site which reads "DOMAIN SUCCESSFULY
ADDED".

.. code::

   http://shx5vqsw7usdaunyzr2qmes2fq37oumybpudrd4jjj4e4vk4uusa.b32.i2p/add

PLEASE COPY AND SAVE THE INFORMATION OF THAT PAGE.

You then be able to visit your I2P site via YourCustomAddress.i2p.

Success
-------

By now, you should have successfully setup your presence over the I2P network.

Conclusion
----------

This is a short guide so people would start to immediately explore the
possibility to host I2P sites.

You are encouraged to read the documentations of i2pd and explore other options
that could be beneficial to you.

Welcome to I2P!
