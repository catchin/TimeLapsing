TimeLapsing
============

A python tool to create time lapse movies from a series of images.

Prerequisites
-------------

* Python 2.7 (probably v2.6 or v3 also work)
* ImageMagick (especially the "convert" tool)
* mencoder
* eog (or another image viewer)

Features
--------

* Quickly test ImageMagick's resize/crop/etc. options on one image
* Batch convert all images according to this setting
* Create a file with all images as a sequence
* Convert the image sequence into a movie
* Command line arguments to do just one thing or another

List of improvements
--------------------

* Guess reasonable resize/crop settings for an image
* Put together image sequence using exif data
* Add readline support
* Support other image viewers
* ...
