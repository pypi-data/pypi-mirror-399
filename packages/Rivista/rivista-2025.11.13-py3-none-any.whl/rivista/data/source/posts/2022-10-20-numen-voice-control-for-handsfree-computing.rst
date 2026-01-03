.. author:
   name,uri
   John Gebbie, https://liberapay.com/geb
.. published: 2022-10-20 0:00:00 UTC
.. summary:
   Voice control for handsfree computing.
   Numen is a voice control software which enables full control of FreeBSD or
   Linux machines without needing to type. It empowers people who otherwise
   could not use their computers, and further helps to avoid hand strain. Numen
   is a free (libre) software and operates locally and privately, without any
   need for internet connectivity.
.. link: 2022-10-20-numen-voice-control-for-handsfree-computing
.. links:
   title,href,rel
   Demonstration video, https://numenvoice.org/numen.webm, enclosure
   Sxmo voice control with Numen (360p), magnet:?xt=urn:btih:ac8ed6a2ca299ca8378ff2915ffb28f00c1a332a&dn=Sxmo%20voice%20control%20with%20Numen%20360p.mp4&xl=13484486&tr=wss%3A%2F%2Fdiode.zone%3A443%2Ftracker%2Fsocket&tr=https%3A%2F%2Fdiode.zone%2Ftracker%2Fannounce&ws=https://video-diode-zone.s3.us-west-001.backblazeb2.com/streaming-playlists/hls/690cf4cb-82af-4b18-8827-71b839a2df5b/b0dcbdf1-132d-4648-bcbc-43b218315c1a-360-fragmented.mp4, enclosure
   Sxmo voice control with Numen (720p), magnet:?xt=urn:btih:ba3d73cb5c7394f024e018a2e305fe8f80a1b205&dn=Sxmo%20voice%20control%20with%20Numen%20720p.mp4&xl=31140665&tr=wss%3A%2F%2Fdiode.zone%3A443%2Ftracker%2Fsocket&tr=https%3A%2F%2Fdiode.zone%2Ftracker%2Fannounce&ws=https://video-diode-zone.s3.us-west-001.backblazeb2.com/streaming-playlists/hls/690cf4cb-82af-4b18-8827-71b839a2df5b/687e07e1-6f5f-4b7d-8293-4b9cd8595f27-720-fragmented.mp4, enclosure
   Sxmo voice control with Numen (1080p), magnet:?xt=urn:btih:2e8f4d2186109c138170f8d64ed41da6ccc0765e&dn=Sxmo%20voice%20control%20with%20Numen%201080p.mp4&xl=74170426&tr=wss%3A%2F%2Fdiode.zone%3A443%2Ftracker%2Fsocket&tr=https%3A%2F%2Fdiode.zone%2Ftracker%2Fannounce&ws=https://video-diode-zone.s3.us-west-001.backblazeb2.com/streaming-playlists/hls/690cf4cb-82af-4b18-8827-71b839a2df5b/78315f10-2658-444a-a9c9-c3cd47e6518e-1080-fragmented.mp4, enclosure
   Numen homesite, https://numenvoice.org, related
   Numen source code, https://git.sr.ht/~geb/numen, related
   Numen video channel, https://peertube.tv/c/numen, related
   A demonstration of Numen with SXMO, https://diode.zone/w/dYo8QcVVFFpzS7PwddFPMV, related
   John Gebbie - Liberapay, https://liberapay.com/geb, related
.. id: 2022-10-20-numen-voice-control-for-handsfree-computing
.. category:
   label, term, scheme
   Accessibility
   Audio
   CCXML
   Computer
   Interaction
   Interface
   Speech
   Voice
   VoiceXML
.. title: Numen - Voice control for handsfree computing
.. type: text

.. image:: /graphics/speak.svg
   :alt: Speak
   :height: 150px
   :loading: lazy
   :target: /graphics/speak.svg
   :width: 150px

Numen is voice control for handsfree computing, to allow to type efficiently by
saying syllables and literal words. It works system-wide on FreeBSD, and Linux;
and the speech recognition mechanism operates locally.

.. raw:: html

   <video
     controls=""
     poster="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyMDAgMjAwIj48dGV4dCB5PSIuOWVtIiBmb250LXNpemU9IjE3MCI+8J+Onu+4jzwvdGV4dD48L3N2Zz4K"
     preload="none"
     style="width:100%;height:100%;">
     <source src="https://numenvoice.org/numen.webm"/>
   </video>

`Demonstration video <https://numenvoice.org/numen.webm>`_

Numen is a project that enables people to use a computer with their voice. The
main motivation is to help people with strain or limited use of their hands. I
wrote numen because I found nothing simple that just worked, everything was a
framework to configure with application specific rules and grammars, trying to
be your text editor and voice assistant, layered on top of something
proprietary. I just wanted an efficient keyboard alternative that worked
everywhere without hassle.

With Numen it is possible to type inputs by saying syllables and literal words,
and it can be significantly efficient when using standard tools. It is useful
for writing and manipulating code in Vim and it is comfortable to surf the
internet using qutebrowser, you can also use the phrases that you use
everywhere, and you do not need to configure anything.

Conclusion
``````````

While other approaches of other software offer needless complexity into the
voice control and then only work with specific applications and graphical
environments, Numen works universally in X11, Wayland, and TTY; and it will
soon be able to turn miniature computers (e.g. Single Board Computers) into
voice input devices for any computer.

Post script
```````````

Numen was created by Mr. John Gebbie.
