#!/usr/bin/env python

import os
import sys
import tempfile
import requests
import flickrapi

api_key = os.environ.get('FLICKR_API_KEY')
api_secret = os.environ.get('FLICKR_API_SECRET')
token = os.environ.get('FLICKR_ACCESS_TOKEN')
assert api_key and api_secret and token, (api_key, api_secret, token)

if __name__ == '__main__':
    for photo_id in sys.stdin.read().split():
        flickr = flickrapi.FlickrAPI(api_key, api_secret, token=token)
        sizes = flickr.photos_getSizes(photo_id=photo_id)
        image = requests.get(sizes[0][-1].attrib['source'])
        filename = tempfile.mktemp('.png')
        with open(filename, 'w+') as f:
            f.write(image.content)
        print filename
