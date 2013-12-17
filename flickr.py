#!/usr/bin/env python # encoding: utf-8
"""
Flickr.py

Created by Anil Kandangath on 2010-06-30.
Copyright (c) 2010 Anil Kandangath. All rights reserved.
"""

import sys
import getopt

import re
from pprint import pprint as p
import time

# Additional packages
from bs4 import BeautifulSoup
import requests

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

def GetCameraBrands():
  """docstring for GetCameraBrands"""
  url = 'http://www.flickr.com/cameras/brands/'
  listCameraBrands = []
  try:
    r = requests.get(url)
  except:
    print "Could not get url %s" %(url)
    return None
  else:
    soup = BeautifulSoup(''.join(r.text))
    
    # Parse these tags
    div = soup.find("div", id="brands")
    table = div.find("table", {"id":"all-brands"})
    rows = table.find_all("tr", recursive=False)
    print "Rows: %d" %(len(rows))
    for tr in rows:
      camera_tags = tr.find_all("td")
      for tag in camera_tags:
        tag = str(tag)
        m = re.search(".*href=\"(?P<Url>.*)\">(?P<Brand>.*)</a>\n</td>",tag, re.MULTILINE)
        if m:
          listCameraBrands.append( CameraBrand(m.group('Brand'), m.group('Url') ) )
          p(m.group('Brand'))
        # end if
      # end for
  # end try
  return listCameraBrands
  
def GetCameraModels(url):
  """docstring for GetCameraBrands"""
  listCameraModels = []
  try:
    r = requests.get(url)
  except:
    print "Failed to get url %s" %(url)
  else:
    soup = BeautifulSoup(''.join(r.text))
    
    div = soup.find("div", id="models")
    table = div.find("table", {"id":"all-cameras"})
    rows = table.findAll("tr", recursive=False)
    for tr in rows:
      camera_tags = tr.find_all("td")
      # Parse these tags
      for tag in camera_tags:
        tag = str(tag)
        m = re.match(".*\n.*href=\"(?P<Url>.*)\">(?P<Model>.*)</a>",tag)
        if m:
          listCameraModels.append( CameraModel(m.group('Model'), m.group('Url') ) )
          p(m.group('Model'))
       # end if
      # end for
  # end try
  return listCameraModels

if __name__ == "__main__":
  listCameraBrands = []
  listCameraBrands = GetCameraBrands()
  print "Found %d brands\n" %len((listCameraBrands)) 
  # start a file for output
  fdata = open('cameradata.txt', 'w')
  
  # We should have a list of camera brands (with class CameraBrand) at this point.
  # Let's try go browse one level deeper
  for brand in listCameraBrands:
    print "\nProcessing %s %s" %(brand.name, brand.url)
    print "-"*25
    time.sleep(1) # Dont' hammer the servers
    fdata.write("---\n" + brand.name + ", " + brand.url + "\n---\n")
    listCameraModels = []
    listCameraModels = GetCameraModels(brand.url)
    for model in listCameraModels:
      fdata.write(model.name + ", " + model.url + "\n") 
    # end for 
  # end for
  fdata.close()
  sys.exit(main())
