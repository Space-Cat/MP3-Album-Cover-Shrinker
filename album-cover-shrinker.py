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

verbose = True

#Returns a io.BytesIO object containing the image data
def DownSizeImage(bytesIO, JpgQuality=90):
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
		if verbose:
			print "Parsing File: " + filePath
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
					print "\t Shrinking file: " + filePath.replace(dontPrint, '')
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
		if verbose:
			print "Parsing folder: " + folder
		folderContents = os.listdir(folder)
		for item in folderContents:
			itemPath = folder + item
			if os.path.isfile(itemPath):
				ParseFile(itemPath, folder)
			else:
				ParseFolder(itemPath)

def Main():
	targetFolder = os.getcwd()
	jpegQuality = 90
	imageWidth = 500
	maxImageSize = 150000

	argCount = len(sys.argv)

	if argCount >= 2:
		targetFolder = sys.argv[1]
	if argCount >= 3:
		jpegQuality = sys.argv[2]
	if argCount >= 4:
		imageWidth = sys.argv[3]
	if argCount >= 5:
		maxImageSize = sys.argv[4]
	if argCount >= 6:
		maxImageSize = sys.argv[5]
	
	print "Target folder: " + targetFolder
	
	ParseFolder(targetFolder)
	
Main()
