#!/usr/bin/env python

import sys, os, io
import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from PIL import Image

#Bytes
MaxImageSize = 150000
#Pixels
MaxImageDimension = 500


def RemoveBloatText(path):
	openSqrBrkt = path.find('[')
	closeSqrBrkt = path.rfind(']')
	if openSqrBrkt > -1 and closeSqrBrkt > openSqrBrkt:
		newPath = path[:openSqrBrkt] + path[closeSqrBrkt+1:]
		os.rename(path, newPath)
		print "Renamed: "
		print path
		print "to"
		print newPath
		return newPath
	else:
		return path


#Returns a io.BytesIO object containing the image data
def DownSizeImage(bytesIO, JpgQuality=90):
	print "Downsizing"
	img = Image.open(bytesIO)
	w = img.size[0]
	h = img.size[1]
	if w > MaxImageDimension:
		aspectRatio = float(w) / h
		newsize = (MaxImageDimension, int(MaxImageDimension * aspectRatio))
		img = img.resize(newsize)
	newImgBytes = io.BytesIO()
	img.save(newImgBytes, "JPEG", quality=JpgQuality)
	newImgBytes.seek(0)	
	return newImgBytes



#Parse an audio file
def ParseFile(filePath, dontPrint=''):
	if filePath.endswith('mp3'):
		audioFile = MP3(filePath, ID3=ID3)
		for tag in audioFile:
			if tag.find('APIC') > -1:
				imgType = audioFile[tag].mime
				imgExtension = ''
				if imgType.find('jp') > -1:
					imgExtension = '.jpg'
				elif imgType.find('png') > -1:
					imgExtension = '.png'


				imgData = audioFile[tag].data
				imgDataLen = len(imgData)
				if imgDataLen > MaxImageSize:
					print "\t Parsing file: " + filePath.replace(dontPrint, '')
					imgBytesIO = io.BytesIO(imgData)
					newImgBytesIO = DownSizeImage(imgBytesIO)
					audioFile.tags.delall('APIC')
					audioFile.tags.add(
						APIC(
							encoding = 3,
							mime = 'image/png',
							type = 3,
							desc = u'',
							data = newImgBytesIO.read()
						)
					)
					audioFile.save()

#Recursively parse a folder, calling ParseFile for each file
def ParseFolder(folder):
	if folder.endswith("/") == False:
		folder += "/"
	if os.path.isdir(folder):
		folder = RemoveBloatText(folder)
		print "Parsing folder: " + folder
		folderContents = os.listdir(folder)
		for item in folderContents:
			itemPath = folder + item
			if os.path.isfile(itemPath):
				ParseFile(itemPath, folder)
			else:
				ParseFolder(itemPath)
arg1 = ""

#Set arg1, if no arguments were passed set to the cwd
if len(sys.argv) >= 2:
	arg1 = sys.argv[1]
else:
	arg1 = os.getcwd()

print "Using dir: " + arg1

ParseFolder(arg1)
