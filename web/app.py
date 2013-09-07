#!/usr/bin/env python

import os
import requests

from flickrapi import FlickrAPI
from datastore import Datastore

from flask import Flask
from flask import redirect
from flask import request
app = Flask(__name__)

@app.route('/')
def register():
    # if no cookie, redirect to flikr auth
    # else, ???
    return redirect(flickr.web_login_url('delete'))

@app.route('/flickr')
def flikr_callback():
    frob = request.args.get('frob','')
    token = flickr.get_token(frob)

    username = flickr.test_login()[0].attrib.get('id','')

    db.put_profile(username, {'token': token})
    # set cookie to know that user is auth'd?
    return 'Ok'

if __name__ == '__main__':
    api_key = os.environ.get('FLICKR_API_KEY','')
    api_secret = os.environ.get('FLICKR_SECRET','')
    flickr = FlickrAPI(api_key, api_secret)
    db = Datastore()

    print 'Starting flask'
    app.run(host='0.0.0.0', port=8080, debug=True)
