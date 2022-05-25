Recording video documentation
*****************************

This page describes how to prepare :mod:`message_ix` documentation in video format.

.. contents::
   :local:

Scripts for current videos, each on its own page:

.. toctree::
   :maxdepth: 1

   video/install


Installation of the software
============================
We use free and open source software so that production of the videos (like the documentation and the software itself) can be done by anyone.

- `OBS Studio <https://obsproject.com>`_ for screen recording.
- `Shotcut <https://shotcut.org>`_ or `ffmpeg <https://ffmpeg.org/>`_ for editing.

Compare existing examples:

- http://software.ece.iiasa.ac.at/ixmp-server/tutorials.html —tutorials for the Scenario Explorer web interface.

Recording
=========
Since recording a video tutorial in one cut without making any mistakes can be very difficult, it is advised to pause or stop the recording in between.
The recording snippets can then be easily concat with one of the above editing software.

General rules:
  - Avoid filler words (“okay”, “um”, etc.).
    Instead, use silence to separate sentences and sections.

Scripts and subtitles
=====================
The folder containing this file (:file:`doc/source/video/`) also holds scripts (in :file:`.rst` format) and example subtitle files (in :file:`.srt`) format for videos already recorded.

- If adding a new video, also add the script and subtitles.
  This is so the script can be modified and re-read in order to update the video with minimal effort.
- Like a screenplay, include both the *words spoken* and the *actions performed on screen*, in the intended order.

General rules:
  - Do not mention specific dates or events.

Editing
=======
As the video tutorials should be properly IIASA-branded one need to follow the `"General video guidelines" <https://iiasahub.sharepoint.com/:w:/r/sites/com/_layouts/15/Doc.aspx?sourcedoc=%7B674376E4-F94C-4C8B-967F-CF1238E6A4B7%7D&file=Video%20Guidelines.docx&action=default&mobileredirect=true&DefaultItemOpen=1>`_.
The following examples will help to concat the intros and outros to the recording, and possible recording snippets, if the video wasn't recorded in one cut.

*Concat videos via ffmpeg*

Create a .txt file, e.g. *to_concat.txt*.
In this file, add "file" and the path to each of the video files you want to concat in "''".
The first path is to the video, which will be shown first::

    file '~\video_1.mp4'
    file '~\video_2.mp4'
    file '~\video_3.mp4'

The following concats all videos listed in *to_concat.txt* and safe them into a new video *concat.mp4*::

    $ ffmpeg -safe 0 -f concat -i ~\to_concat -c copy concat.mp4

.. note::
   Only videos in the same format can be concated.

*Add textbox via ffmpeg*

In some cases it is needed to add a title or a note to the video, e.g. *title.png*.
This image can be overlaid during a certain time onto the video [1]_::

    $ ffmpeg -i concat.mp4 -i ~\titel.png -filter_complex "[0:v][1:v] overlay=25:25:enable='between(t,0,20)'" -pix_fmt yuv420p -c:a copy concat-w-title.mp4

.. [1]  For extensive information, please have a e.g. a look `here <https://video.stackexchange.com/questions/12105/add-an-image-overlay-in-front-of-video-using-ffmpeg>`_.
