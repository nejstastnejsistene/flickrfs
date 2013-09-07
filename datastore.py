#!/usr/bin/env python

import json
import redis

FILE_KEY = '{0}|files'

class Datastore(object):

    def __init__(self, user_id):
        self.user_id = user_id
        self.redis = redis.StrictRedis()

    def clear(self):
        self.redis.delete(self.user_id)
        self.redis.delete(FILE_KEY.format(self.user_id))

    def get_profile(self):
        '''Returns a python dict of users profile data'''
        return self.redis.hgetall(self.user_id)

    def get_files(self):
        '''Returns list of users filenames'''
        return self.redis.hkeys(FILE_KEY.format(self.user_id))

    def get_file_metadata(self, filename):
        '''Returns a python dict of metadata for the given filename'''
        return json.loads(self.redis.hget(FILE_KEY.format(self.user_id),
                                          filename) or '{}')

    def put_profile(self, profile):
        '''Updates the user's profile with the given information

        Note that setting a field to None will remove that field from the
        profile'''
        old_profile = self.get_profile()
        old_profile.update(profile)
        for k, v in old_profile.items():
            if v:
                self.redis.hset(self.user_id, k, v)
            else:
                self.redis.hdel(self.user_id, k)

        return True

    def put_file_metadata(self, filename, metadata):
        '''Updates the filename metadata with the given information

        Note that setting a field to None will remove that field from the
        metadata'''
        old_metadata = self.get_file_metadata(filename)
        old_metadata.update(metadata)
        self.redis.hset(FILE_KEY.format(self.user_id), filename, json.dumps({k: v for k, v in old_metadata.items() if v is not None}))
        return True
