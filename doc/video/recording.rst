Recording video documentation
*****************************

This page describes how to prepare :mod:`message_ix` documentation in video format.

Install the software.
We use free and open source software so that production of the videos (like the documentation and the software itself) can be done by anyone.

- `OBS Studio <https://obsproject.com>`_ for screen recording.
- `Shotcut <https://shotcut.org>`_ for editing.

Compare existing examples:

- http://software.ene.iiasa.ac.at/ixmp-server/tutorials.html —tutorials for the Scenario Explorer web interface.

**Scripts and subtitles.**
The folder containing this file (:file:`doc/source/video/`) also holds scripts (in :file:`.rst` format) and example subtitle files (in :file:`.srt`) format for videos already recorded.

- If adding a new video, also add the script and subtitles.
  This is so the script can be modified and re-read in order to update the video with minimal effort.
- Like a screenplay, include both the *words spoken* and the *actions performed on screen*, in the intended order.
- General rules:

  - Do not mention specific dates or events.
  - Avoid filler words (“okay”, “um”, etc.).
    Instead, use silence to separate sentences and sections.

Current videos
==============

.. toctree::

   install
