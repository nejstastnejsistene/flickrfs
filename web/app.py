#!/usr/bin/env python

import os

from flickrapi import FlickrAPI
from datastore import Datastore

from flask import Flask
from flask import redirect
from flask import request
app = Flask(__name__)

@app.route('/')
def register():
    # if no cookie, redirect to flickr auth
    # else, ???
    return redirect(flickr.web_login_url('delete'))

@app.route('/flickr')
def flickr_callback():
    frob = request.args.get('frob','')
    token = flickr.get_token(frob)

    user_xml = flickr.test_login()[0]
    uid = user_xml.attrib.get('id','')
    username = user_xml[0].text

    db.put_profile({'token': token, 'uid': uid}, username)
    return redirect('http://github.com/brcooley/pennapps')

if __name__ == '__main__':
    api_key = os.environ.get('FLICKR_API_KEY','')
    api_secret = os.environ.get('FLICKR_SECRET','')
    flickr = FlickrAPI(api_key, api_secret)
    db = Datastore()

    print 'Starting flask'
    app.run(host='0.0.0.0', port=8080, debug=True)
