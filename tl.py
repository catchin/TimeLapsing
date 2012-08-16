#!/usr/bin/python
# TimeLapsing
# Copyright (C) 2012  Fabian Kneissl <fabian@kneissl-web.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import tempfile
import subprocess
import sys
import os
import re
from os import path
import argparse

class TimeLapsing:
	def __init__(self, args):
		if not args.convert and not args.movie:
			self.isConvertImages = True
			self.isCreateMovie = True
		else:
			self.isConvertImages = args.convert
			self.isCreateMovie = args.movie
		self.fps = args.fps
		self.isHQMovie = args.hq
		self.sourceDir = args.source
		self.overwrite = args.overwrite
		self.configDir = "~/.config/timelapsing"
		self.options = None
		self.fileSequenceName = "filesequence.txt"
		self.movieName = "timelapse.avi"
	
	def allFiles(self):
		files = filter(lambda f: f.endswith(".jpg"), os.listdir(self.sourceDir))
		files.sort()
		return files

	def convertAll(self):
		files = self.allFiles()
		sys.stdout.write("Converting %s images" % len(files))
		overwrite = None
		if self.overwrite:
			overwrite = True
		for f in files:
			destFile = os.path.join(self.destDir, f)
			pathExists = os.path.exists(destFile)
			if overwrite == None and pathExists:
				overwrite = self.confirm("Overwrite existing images")
			if overwrite:
				self.convertSingle(f, destFile)
			sys.stdout.write(".")
			sys.stdout.flush()
		print("done")

	def convertSingle(self, img, outimg):
		args = ["convert"]
		args.extend(self.options)
		args.extend([img, outimg])
		return subprocess.call(args)

	def testForConvertParameters(self, img=None):
		if img == None:
			img = self.allFiles()[0]
		imgWidth = int(re.search("[0-9]+", subprocess.check_output(["identify", "-format", "'%w'", img])).group(0))
		imgHeight = int(re.search("[0-9]+", subprocess.check_output(["identify", "-format", "'%h'", img])).group(0))
		print("Your input image has dimensions %sx%s.\n" % (imgWidth, imgHeight))
		aspect = 16.0/9
		maxImgWidth = int(min(imgWidth, imgHeight * aspect))
		maxImgHeight = int(min(imgHeight, imgWidth / aspect))
		suggestedCrop = "%sx%s+%s+%s" % (maxImgWidth, maxImgHeight, 
				abs(maxImgWidth-imgWidth)/2,
				abs(maxImgHeight-imgHeight)/2)
		print("Enter the conversion you want to do.\n" \
				"Examples:\n" \
				" -crop %s +repage -scale 1920x1080\n" \
				" -crop %s +repage -scale 1920x1080 -level 3,95\n" \
				" -rotate 2.0 -crop 2087x1174+42+84 +repage -scale 1920x1080\n\n" \
				"Enter a blank line when you are satisfied with the output image.\n" %
				(suggestedCrop, suggestedCrop))

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

	def createImageSequence(self):
		files = self.allFiles()
		filename = os.path.join(self.sourceDir, self.fileSequenceName)
		if self.confirm("Overwrite image sequence file", filename):
			with open(filename, "w") as f:
				f.writelines(map(lambda s: os.path.join(self.destDir, s) + "\n", files))
	
	def createMovie(self):
		filename = os.path.join(self.sourceDir, self.movieName)
		if self.confirm("Overwrite time lapse movie", filename=filename):
			args = ["mencoder"]
			if self.isHQMovie:
				args.extend(["-ovc", "x264", "-x264encopts", "preset=veryslow:tune=film:crf=15:frameref=15:fast_pskip=0:threads=auto"])
			else:
				args.extend(["-ovc", "lavc", "-lavcopts", "vcodec=mpeg4:mbd=2:trell:autoaspect:vqscale=3"])
			args.extend(["-nosound", 
					"-mf", "type=jpeg:fps=%s" % self.fps,
					"-o", filename, 
					"mf://@%s" % os.path.join(self.sourceDir, self.fileSequenceName)])
			subprocess.call(args)
	
	def confirm(self, prompt, defaultResponse=False, filename=None):
		if filename:
			if not os.path.exists(filename) or self.overwrite:
				return True
			else:
				prompt = prompt + " " + filename
		if defaultResponse:
			prompt = prompt + " [Y/n]?"
		else:
			prompt = prompt + " [y/N]?"
		while True:
			answer = raw_input(prompt)
			if not answer:
				return defaultResponse
			elif answer.lower() == "y" or answer.lower() == "j":
				return True
			elif answer.lower() == "n":
				return False
	
	def run(self):
		self.destDir = os.path.join(self.sourceDir, "converted")
		if not os.path.isdir(self.destDir):
			os.mkdir(self.destDir)
		if self.isConvertImages:
			self.testForConvertParameters()
			self.convertAll()
			self.createImageSequence()
		if self.isCreateMovie:
			self.createMovie()

print '''TimeLapsing  Copyright (C) 2012  Fabian Kneissl <fabian@kneissl-web.net>
This program comes with ABSOLUTELY NO WARRANTY; for details see LICENSE.txt.
This is free software, and you are welcome to redistribute it
under certain conditions; for details see LICENSE.txt.
'''

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--overwrite", action="store_true", help="overwrite files without notice")
parser.add_argument("-s", "--source", type=str, default=".", help="directory where all time lapse images are")
parser.add_argument("-hq", action="store_true", help="create the movie in high quality (slower)")
parser.add_argument("-fps", type=int, default=20, help="the frames per second the movie should have")
group = parser.add_mutually_exclusive_group()
group.add_argument("-c", "--convert", action="store_true", help="convert images and create sequence file")
group.add_argument("-m", "--movie", action="store_true", help="create a movie from sequence file")
args = parser.parse_args()

tl = TimeLapsing(args)

tl.run()


