#!/usr/bin/env python

import json
import redis

FILE_KEY = '{0}|files'

class Datastore(object):

    def __init__(self, user_id):
        self.user_id = user_id
        self.redis = redis.StrictRedis()
        self.user = user_id

    def clear(self, user_id=None):
        user_id = user_id or self.user
        self.redis.delete(user_id)
        self.redis.delete(FILE_KEY.format(user_id))

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
                self.redis.hset(self.user_id, k, v)
            else:
                self.redis.hdel(self.user_id, k)

        return True

    def get_files_metadata(self, user_id=None):
        '''Returns a python dict of metadata for all files'''
        key = FILE_KEY.format(user_id or self.user)
        return json.loads(self.redis.get(FILE_KEY.format(key)) or '{}')

    def put_files_metadata(self, metadata, user_id=None):
        '''Updates the filename metadata with the given information'''
        #user_id = user_id or self.user
        #old_metadata = self.get_files_metadata(user_id, filename)
        #old_metadata.update(metadata)
        self.redis.set(FILE_KEY.format(user_id or self.user),
                       json.dumps(metadata))
        return True

    def get_files(self, user_id=None):
        '''Returns list of users filenames'''
        return self.redis.hkeys(FILE_KEY.format(user_id or self.user))
