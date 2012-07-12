#!/usr/local/bin/python
"""
ripplr.py
Purpose: A tumblr blog image scraper
Author:  Kendrick Ledet
Date:    7/10/12 
"""
"""
Copyright 2012 Kendrick Ledet
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import time
import urllib2
import urllib
import json
import os

def create_path(path):
	if not os.path.isdir(path):
		os.makedirs(path)

""" Generate a clean blog url to use as folder name """
def clean_title(blog_url):
	return blog_url.split('/')[2]

""" Download a given img link """
def download(img):
	filename = img.split('/')[3] # get the original filename from the image link
	if os.path.exists(os.path.join(path, filename)): # don't overwrite existing images
		pass
	else:
		urllib.urlretrieve(img, os.path.join(path, filename)) # download the img 

""" Get some initial input from the user """
blog_url  = raw_input('Enter tumblr url\n> ')
tag_query = raw_input('Enter a specific tag to filter posts by, (just press enter for no tag filter)\n> ') 
limit     = int(raw_input('Enter max # of images to download (this is quite useful if you want to grab, say, the latest 50 posts, but just enter 0 to download all images)\n> '))


if blog_url[-1] == '/': # if URL has a trailing slash, remove it
	blog_url = blog_url[0:-1]

title = clean_title(blog_url) # get a clean folder name from blog url
""" Set and create download path """
path  = ('downloads/' + title + '/')
create_path(path)

print 'Downloading from %s...' % (blog_url,)
start = 0 # initialize the API reading start offset to 0
download_count = 0
""" Begin the download loop """
while True:
	""" Construct the full URL to retrieve JSON from """
	full_url = '%s/api/read/json?type=photo&debug=1&start=%d&num=50&tagged=%s' % (blog_url, start, tag_query)
	request  = urllib2.Request(full_url) # make a Request object from it

	""" Get JSON response """
	try:
		response = urllib2.urlopen(request)
		page     = response.read()
		response.close()
	except Exception, e:
		pass

	json_output = json.loads(page) # parse the JSON

	if start == 0: # if running on first loop iteration
		print json_output['posts-total'], 'photo posts found' # tell the user how many posts were found
		if limit:
			print 'Downloading a maximum of', str(limit), 'images'
		else:
			print 'Downloading all images'

	""" Download the images """
	for post in json_output['posts']: # for every post in this iteration
		if post['photo-url-1280']: # if image content exists
			download(post['photo-url-1280'])
			download_count = download_count + 1
			if limit: # if limit is defined
				if download_count == limit+1: # if limit reached
					print 'Limit reached, images are in ./downloads/'+title+'/'
					exit(1)
		if post['photos']: # if post has a photoset
			for photo in post['photos']: # download each image in the photoset as well
				download(photo['photo-url-1280'])
				download_count = download_count + 1
				if limit: # if limit is defined
					if download_count == limit+1: # if limit reached
						print 'Limit reached, images are in ./downloads/'+title+'/'
						exit(1)
	if limit:
		if download_count == limit+1:
			break

	start = start + 50 # increment the start GET parameter by 50 for the next loop iteration
	if start > int(json_output['posts-total']): # if no more posts to scrape
		print 'Scraped ', json_output['posts-total'], 'photo posts'
		print 'Downloads are contained in ./downloads/'+title+'/'
		break
