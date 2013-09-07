#!/usr/bin/env python
# storage.py

import os
import sys
import json
import redis
import requests

from flickrapi import FlickrAPI
from flickrapi.exceptions import FlickrError

URL = 'fuflickr.cloudapp.net'
NAME = 'FlickrFS'
FILE_KEY = '{0}|files'

class FStore(object):

    def __init__(self, user_id=None):
        api_key = os.environ.get('FLICKR_API_KEY')
        api_secret = os.environ.get('FLICKR_SECRET')

        if not api_key or not api_secret:
            raise ValueError('API credentials not available. Check for FLICKR_API_KEY and FLICKR_SECRET env variables')

        if not user_id:
            raise ValueError('User not specified or not in database. Please visit {0} to register for {1}'.format(URL, NAME))
        self.user = user_id
        self.redis = redis.StrictRedis(host=URL)
        self.flickr = FlickrAPI(api_key, api_secret, token=self.get_profile().get('token'))

    def _upload(self, img_list):
        '''Takes a list of images and uploads to flickr, returning the photo_ids'''
        pid_list = []
        for img in img_list:
            # print 'uploading ' + img
            pid = self.flickr.upload(img)[0]
            pid_list.append(pid.text)

        return pid_list

    def _download(self, photo_ids):
        '''Takes a list of flickr photo_ids and downloads them

        Returns the absolute filepath'''
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
        for pid in photo_ids:
            # print 'deleting ' + pid
            self.flickr.photos_delete(photo_id=pid)

    def get_profile(self):
        '''Returns a python dict of users profile data'''
        return self.redis.hgetall(self.user)

    def put_profile(self, profile):
        '''Updates the user's profile with the given information

        Note that setting a field to None will remove that field from the profile'''

        old_profile = self.get_profile()
        old_profile.update(profile)
        for k, v in old_profile.items():
            if v:
                self.redis.hset(self.user, k, v)
            else:
                self.redis.hdel(self.user, k)

        return True

    def get_file_metadata(self, filename):
        '''Returns a python dict of metadata for the given file'''
        return json.loads(self.redis.hget(FILE_KEY.format(self.user), filename) or '{}')

    def put_files_metadata(self, filename, metadata):
        '''Updates the filename metadata with the given information

        Note that setting a field to None will remove that field from the profile'''
        old_metadata = self.get_file_metadata(filename)
        old_metadata.update(metadata)
        new_metadata = {k: v for k, v in old_metadata if v is not None}
        self.redis.hset(FILE_KEY.format(self.user), filename, json.dumps(new_metadata))
        return True

    def get_files(self):
        '''Returns list of users filenames'''
        return self.redis.hkeys(FILE_KEY.format(self.user))

    def get_files_metadata(self):
        '''Returns all file metadata for this user'''
        return self.redis.hgetall(FILE_KEY.format(self.user))

    def delete_user(self):
        '''Removes all data associated with a user'''
        self.delete_user_files()
        self.redis.delete(self.user)

    def delete_user_files(self):
        '''Deletes all user files while leaving the user's token intact'''
        for f in self.get_files():
            images = self.get_file_metadata(f).get('chunks')
            try:
                self._delete([i[0] for i in images])
            except FlickrError:
                pass

        self.redis.delete(FILE_KEY.format(self.user))


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
