#!/usr/bin/env python
# encoding: utf-8
"""
Flickr.py

Created by Anil Kandangath on 2010-06-30.
Copyright (c) 2010 Anil Kandangath. All rights reserved.
"""

import sys
import getopt

import urllib
import urllib2, httplib
from urllib2 import Request, urlopen, URLError, HTTPError
import StringIO
import gzip
from BeautifulSoup import BeautifulSoup
import re


help_message = '''
This is a screen scraping program for the camera list on Flickr.
'''

class CameraBrand():
	def __init__(self, name="", url=""):
		self.name = name
		self.url = "http://www.flickr.com" + url
		self.models = {}
	#end def
# end class CameraBrand
		
class CameraModel():
	def __init__(self, name="", url=""):
		self.name = name
		self.url = "http://www.flickr.com" + url
	#end def
# end class CameraModel

class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg
	#end def
#end class Usage


def main(argv=None):
	if argv is None:
		argv = sys.argv
	try:
		try:
			opts, args = getopt.getopt(argv[1:], "ho:v", ["help", "output="])
		except getopt.error, msg:
			raise Usage(msg)
	
		# option processing
		for option, value in opts:
			if option == "-v":
				verbose = True
			if option in ("-h", "--help"):
				raise Usage(help_message)
			if option in ("-o", "--output"):
				output = value
	
	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >> sys.stderr, "\t for help use --help"
		return 2

def GetCameraBrands(url, headers):
	"""docstring for GetCameraBrands"""
	httplib.HTTPConnection.debuglevel = 1
	request = urllib2.Request(url=url,headers=headers)
	opener = urllib2.build_opener()
	
	listCameraBrands = []
	try:
		response = opener.open(request)
	except HTTPError,e:
		print 'Server could not fulfil request. Error: ', e.code
	except URLError,e:
		print 'Failed to reach server. Error: ', e.reason
	else:
		the_page = response.read()
		# Unzip the compressed data stream		
		compressedstream = StringIO.StringIO(the_page)
		gzipper = gzip.GzipFile(fileobj=compressedstream)
		data = gzipper.read()
		# Need to decode utf-8 if this has to be printed anywhere
		data = data.decode('utf-8')
		doc = [data]
		soup = BeautifulSoup(''.join(doc))
		camera_tags = soup.findAll('h4')
		# Parse these tags
		for tag in camera_tags:
			tag = str(tag)
			m = re.match(".*href=\"(.*)\">(.*)</a>",tag)
			if m:
				listCameraBrands.append( CameraBrand(m.group(2), m.group(1) ) )
			# end if
		# end for
	# end try
	return listCameraBrands
	
def GetCameraModels(url, headers):
	"""docstring for GetCameraBrands"""
	httplib.HTTPConnection.debuglevel = 1
	request = urllib2.Request(url=url,headers=headers)
	opener = urllib2.build_opener()
	
	listCameraModels = []
	try:
		response = opener.open(request)
	except HTTPError,e:
		print 'Server could not fulfil request. Error: ', e.code
	except URLError,e:
		print 'Failed to reach server. Error: ', e.reason
	else:
		the_page = response.read()
		# Unzip the compressed data stream		
		compressedstream = StringIO.StringIO(the_page)
		gzipper = gzip.GzipFile(fileobj=compressedstream)
		data = gzipper.read()
		# Need to decode utf-8 if this has to be printed anywhere
		data = data.decode('utf-8')
		doc = [data]
		soup = BeautifulSoup(''.join(doc))
		
		div = soup.find("div", id="models")
		table = div.find("table", {"class":"cfModels sortable"})
		rows = table.findAll('tr')
		for tr in rows:
			camera_tags = tr.findAll("td", "cfM")
			#print camera_tags
			# Parse these tags
			for tag in camera_tags:
				tag = str(tag)
				m = re.match(".*\n.*href=\"(.*)\">(.*)</a>",tag)
				if m:
					listCameraModels.append( CameraModel(m.group(2), m.group(1) ) )
				# end if
			# end for
	# end try
	return listCameraModels

if __name__ == "__main__":
	url = 'http://www.flickr.com/cameras/brands/'
	accept = 'application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5'
	user_agent = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; en-US) AppleWebKit/533.4 (KHTML, like Gecko) Chrome/5.0.375.86 Safari/533.4'
	headers = { 'User-Agent' : user_agent, 'Accept' : accept, 'Accept-encoding' : 'gzip' }
	
	listCameraBrands = []
	listCameraBrands = GetCameraBrands(url, headers)
	
	# start a file for output
	fdata = open('cameradata.txt', 'w')
	
	# We should have a list of camera brands (with class CameraBrand) at this point.
	# Let's try go browse one level deeper
	for brand in listCameraBrands:
		print "Processing "
		print brand.name, brand.url
		print "-"*25
		fdata.write("---\n")
		fdata.write(brand.name + " " + brand.url + "\n")
		fdata.write("---\n")
		listCameraModels = []
		listCameraModels = GetCameraModels(brand.url, headers)
		for model in listCameraModels:
			#print model.name, model.url
			fdata.write(model.name + " " + model.url + "\n")
		# end for
	# end for
	fdata.close()
	sys.exit(main())
