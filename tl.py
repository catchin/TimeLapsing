#!/usr/bin/python
import tempfile
import subprocess
import sys
import os
from os import path
import argparse

class TimeLapsing:
	def __init__(self):
		self.sourceDir = "."
		self.configDir = "~/.config/timelapsing"
		self.options = None

	def convertAll(self):
		files = filter(lambda f: f.endswith(".jpg"), os.listdir(self.sourceDir))
		sys.stdout.write("Converting %s images" % len(files))
		for f in files:
			self.convertSingle(f, os.path.join(self.destDir, f))
			sys.stdout.write(".")
			sys.stdout.flush()
		print("done")

	def convertSingle(self, img, outimg):
		args = ["convert"]
		args.extend(self.options)
		args.extend([img, outimg])
		return subprocess.call(args)

	def testForConvertParameters(self, img=None):
		print("Enter the conversion you want to do.\n" \
				"Examples:\n" \
				" -crop 2144x1206+0+109 +repage -scale 1920x1080\n" \
				" -crop 2144x1206+0+109 +repage -scale 1920x1080 -level 3,95\n" \
				" -rotate 2.0 -crop 2087x1174+42+84 +repage -scale 1920x1080\n" \
				" -crop 3216x1809+0+50 +repage -scale 1920x1080\n\n" \
				"Enter a blank line when you are satisfied with the output image.\n")

		if img == None:
			for files in os.listdir(self.sourceDir):
				if files.endswith(".jpg"):
					img = files
					break
		while True:
			sys.stdout.write("=> ")
			readline = sys.stdin.readline().strip()
			if len(readline) == 0:
				break
			self.options = readline.split(" ")
			self.testConvert(img)

	def testConvert(self, img):
		tmpfile = tempfile.NamedTemporaryFile(suffix=".jpg")
		success = self.convertSingle(os.path.join(self.sourceDir,img), tmpfile.name)
		if success == 0:
			subprocess.call(["eog", tmpfile.name])
		tmpfile.close()
	
	def run(self):
		self.testForConvertParameters()
		self.destDir = os.path.join(self.sourceDir, "converted")
		os.mkdir(self.destDir)
		self.convertAll()


parser = argparse.ArgumentParser()
parser.add_argument("-s", "--source", type=str, help="directory where all time lapse images are")
args = parser.parse_args()

tl = TimeLapsing()
if args.source:
	tl.sourceDir = args.source

tl.run()


