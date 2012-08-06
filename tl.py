#!/usr/bin/python
import tempfile
import subprocess
import sys
import os
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
		self.isHQMovie = args.hq
		self.sourceDir = args.source
		self.overwrite = args.overwrite
		self.configDir = "~/.config/timelapsing"
		self.options = None
		self.fileSequenceName = "filesequence.txt"
		self.movieName = "timelapse.avi"
	
	def allFiles(self):
		return filter(lambda f: f.endswith(".jpg"), os.listdir(self.sourceDir))

	def convertAll(self):
		files = self.allFiles()
		sys.stdout.write("Converting %s images" % len(files))
		overwrite = None
		for f in files:
			destFile = os.path.join(self.destDir, f)
			if not os.path.exists(destFile) or self.overwrite or overwrite:
				self.convertSingle(f, destFile)
			elif overwrite == None:
				sys.stdout.write("\n")
				overwrite = self.confirm("Overwrite existing images")
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

	def createImageSequence(self):
		files = self.allFiles()
		files.sort()
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
					"-mf", "type=jpeg:fps=20",
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


parser = argparse.ArgumentParser()
parser.add_argument("-o", "--overwrite", action="store_true", help="overwrite files without notice")
parser.add_argument("-s", "--source", type=str, default=".", help="directory where all time lapse images are")
parser.add_argument("-hq", action="store_true", help="create the movie in high quality (slower)")
group = parser.add_mutually_exclusive_group()
group.add_argument("-c", "--convert", action="store_true", help="convert images and create sequence file")
group.add_argument("-m", "--movie", action="store_true", help="create a movie from sequence file")
args = parser.parse_args()

tl = TimeLapsing(args)

tl.run()


