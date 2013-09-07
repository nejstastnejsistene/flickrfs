#!/usr/bin/env python

import json
import redis

FILE_KEY = '{0}|files'

class Datastore(object):

    def __init__(self, user_id=None):
        self.redis = redis.StrictRedis()
        self.user = user_id

    def get_profile(self, user_id=None):
        '''Returns a python dict of users profile data'''
        return self.redis.hgetall(user_id or self.user)

    def put_profile(self, profile, user_id=None):
        '''Updates the user's profile with the given information

        Note that setting a field to None will remove that field from the profile'''

        user_id = user_id or self.user
        old_profile = self.get_profile(user_id)
        old_profile.update(profile)
        for k, v in old_profile.items():
            if v:
                self.redis.hset(user_id, k, v)
            else:
                self.redis.hdel(user_id, k)

        return True

    def get_file_metadata(self, filename, user_id=None):
        '''Returns a python dict of metadata for the given filename'''
        return json.loads(self.redis.hget(FILE_KEY.format(user_id), filename) or '{}')

    def put_file_metadata(self, filename, metadata, user_id=None):
        '''Updates the filename metadata with the given information

        Note that setting a field to None will remove that field from the metadata'''

        user_id = user_id or self.user
        old_metadata = self.get_file_metadata(user_id, filename)
        old_metadata.update(metadata)
        self.redis.hset(FILE_KEY.format(user_id), filename, json.dumps({k: v for k, v in old_metadata.items() if v is not None}))
        return True

    def get_files(self, user_id=None):
        '''Returns list of users filenames'''
        return self.redis.hkeys(FILE_KEY.format(user_id or self.user))
