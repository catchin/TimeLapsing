#!/usr/bin/python
import tempfile
import subprocess
import os
from os import path

def convert(sourceDir, destDir, options):
	for files in os.listdir(sourceDir):
		if files.endswith(".jpg") or files.endswith(".jpeg"):
			convertSingle(files, os.path.join(destDir, files), options)

def convertSingle(img, outimg, options):
	args = ["convert"]
	args.extend(options)
	args.extend([img, outimg])
	subprocess.call(args)

def testConvert(img, options):
	tmpfile = tempfile.NamedTemporaryFile(suffix=".jpg")
	convertSingle(img, tmpfile.name, options)
	subprocess.call(["eog", tmpfile.name])
	print(tmpfile.name)
	tmpfile.close()

#testConvert("/data/dateien/Bilder/Digicam/2012/07_Stuttgart/6/20120730-n032732.jpg", ["-scale", "1920x1080"])


