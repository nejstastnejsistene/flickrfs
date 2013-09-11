#!/usr/bin/env python

import os
import sys
import flickrapi

api_key = os.environ.get('FLICKR_API_KEY')
api_secret = os.environ.get('FLICKR_API_SECRET')
token = os.environ.get('FLICKR_ACCESS_TOKEN')
assert api_key and api_secret and token, (api_key, api_secret, token)

if __name__ == '__main__':
    for filename in sys.stdin.read().split():
        flickr = flickrapi.FlickrAPI(api_key, api_secret, token=token)
        print flickr.upload(filename)[0].text
        os.unlink(filename)
