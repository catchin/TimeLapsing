#!/usr/bin/python
import tempfile
import subprocess
import sys
import os
from os import path
import argparse

class TimeLapseCatchin:
	def __init__(self):
		self.sourceDir = "."

	def convertAll(self, sourceDir, destDir, options):
		for files in os.listdir(sourceDir):
			if files.endswith(".jpg") or files.endswith(".jpeg"):
				self.convertSingle(files, os.path.join(destDir, files), options)

	def convertSingle(self, img, outimg, options):
		args = ["convert"]
		args.extend(options)
		args.extend([img, outimg])
		return subprocess.call(args)

	def testForConvertParameters(self, options=None):
		print("Enter the conversion you want to do.\n" \
				"Examples:\n" \
				" -crop 2144x1206+0+109 +repage -scale 1920x1080\n" \
				" -crop 2144x1206+0+109 +repage -scale 1920x1080 -level 3,95\n" \
				" -rotate 2.0 -crop 2087x1174+42+84 +repage -scale 1920x1080\n" \
				" -crop 3216x1809+0+50 +repage -scale 1920x1080\n\n" \
				"Enter a blank line when you are satisfied with the output image.\n")

		while True:
			sys.stdout.write("=> ")
			readline = sys.stdin.readline().strip()
			if len(readline) == 0:
				return options
			options = readline.split(" ")
			self.testConvert("20120730-n032732.jpg", options)

	def testConvert(self, img, options):
		tmpfile = tempfile.NamedTemporaryFile(suffix=".jpg")
		success = self.convertSingle(os.path.join(self.sourceDir,img), tmpfile.name, options)
		if success == 0:
			subprocess.call(["eog", tmpfile.name])
		tmpfile.close()
	
	def run(self):
		options = self.testForConvertParameters()
		print(options)


parser = argparse.ArgumentParser()
parser.add_argument("-s", "--source", type=str, help="directory where all time lapse images are")
args = parser.parse_args()

tl = TimeLapseCatchin()
if args.source:
	tl.sourceDir = args.source

tl.run()


