#!/usr/bin/env python
# up_down.py
# uploads images to flickr and 
# downloads original image links 
import flickrapi
import sys

# upload() 
# upload image
def upload(api_key, api_secret, tok, img):
  flickr = flickrapi.FlickrAPI(api_key, api_secret, token=tok)
  #flickr.upload(img, callback=show_progress)
  flickr.upload(img)

''' # show_progress doesn't seem to catch the callback
def show_progress(progress, done):
  if done:
    print "Done!"
  else:
    print "At %s%%" % progress
    '''

# search()
# prints a url of the original images
# on the authenticated users flickr
def search(api_key, api_secret):
  flickr = flickrapi.FlickrAPI(api_key, api_secret)
  uid = 'me' # key to indicate the authenticated user
  photos = flickr.photos_search(user_id=uid, extras='original_format')

  for photo in photos[0]:
    # Build the url, for details see 
    # http://www.flickr.com/services/api/misc.urls.html
    url = ('http://farm' +
	   photo.attrib['farm'] + '.staticflickr.com/' +
	   photo.attrib['server'] + '/' +
	   photo.attrib['id'] + '_' + 
	   photo.attrib['originalsecret'] + '_o.png')
    print url, photo.attrib['title']

# print_usage()
# prints command line usage
def print_usage():
  print 'usage: up_down.py [img]'

def main():
  api_key = # API_KEY GOES HERE
  api_secret = # API_SECRET GOES HERE
  tok = # TOKEN GOES HERE

  if len(sys.argv) != 2:
    print_usage(); sys.exit(1)

  img = sys.argv[1]

  upload(api_key, api_secret, tok, img)
  search(api_key, api_secret)


if __name__ == '__main__':
  main()
