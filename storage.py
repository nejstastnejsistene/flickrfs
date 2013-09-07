#!/usr/bin/env python

import sys
import json
import redis

from flickrapi import FlickrAPI

class FStore(object):

    def __init__(self):
        self.flickr = FlickrAPI(os.environ.get('FLICKR_API_KEY'), os.environ.get('FLICKR_SECRET'), token=token)

    # TODO: Mike should modify _upload and _download to take in lists of images and photo_ids
    #       and upload/download them all

    def _upload(self, image):
        self.flickr.upload(image)

    def _download(self, photo_id):
        sizes = flickr.photos_getSize(photo_id=photo_id)

        original_url = [size.get('source') for size in sizes[0] if size.get('label') is 'Original'][0]

        # TODO: Mike needs to use original_url to download the image and return the absolute filepath


def print_usage():
    print 'usage: up_down.py [img]'

def main():
    if len(sys.argv) != 2:
        print_usage()
        sys.exit(1)

    img = sys.argv[1]

    upload(tok, img)
    search()

if __name__ == '__main__':
    main()
