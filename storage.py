#!/usr/bin/env python
# storage.py

import os
import sys
import json
import redis
import requests

from flickrapi import FlickrAPI

class FStore(object):

    def __init__(self, token):
        api_key = os.environ.get('FLICKR_API_KEY')
        api_secret = os.environ.get('FLICKR_SECRET')
        assert api_key != None and api_secret != None
        self.flickr = FlickrAPI(api_key, api_secret, token=token)

    def _upload(self, img_list):
        '''Takes a list of images and uploads to flickr'''
        assert isinstance(img_list, list)
        for img in img_list:
            # print 'uploading ' + img
            self.flickr.upload(img)

    def _download(self, photo_ids):
        '''Takes a list of flickr photo_ids and downloads them

        Returns the absolute filepath'''
        assert isinstance(photo_ids, list)
        flist = []
        for pid in photo_ids:
            sizes = self.flickr.photos_getSizes(photo_id=pid)
            img = requests.get(sizes[0][-1].attrib['source'])

            # use the photo id as the file name
            with open(pid, 'w+') as f:
            f.write(img.content)

            # save the file path in our list
            flist.append(os.path.abspath(pid))

        # return the list of fully-qualified pathnames
        return flist

    def _delete(self, photo_ids):
        '''Takes a list of flickr photo_ids and deletes them'''
        assert isinstance(photo_ids, list)
        for pid in photo_ids:
            # print 'deleting ' + pid
            self.flickr.photos_delete(photo_id=pid)


def print_usage():
    print 'usage: up_down.py [img]'

def main():
    token = '72157635426291810-1cc633b8ce447829'
    ffs = FStore(token)


    ########## delete photos ##########
    photo_ids = ['9696283248', '9696282758']
    ffs._delete(photo_ids)

    '''
    ########## download photos ##########
    photo_ids = ['9693022251', '9695265660']
    ffs._download(photo_ids)
    '''

    '''
    ########## upload photos ##########
    img_list  = ['images/flyingBrearJackassKills.png', 'images/sodaEffects.png',
        'images/franklinOnLife.png', 'images/stallman.png',
        'images/hardwarePoster.png', 'images/ubuntuJoke.png',
        'images/linuxFlowchart.png', 'images/watermelonMurder.png',
        'images/plagueDoctor.png']

    ffs._upload(img_list)
    '''

if __name__ == '__main__':
    main()
