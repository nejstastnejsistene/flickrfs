#!/usr/bin/env python

import os

from datastore import Datastore
from argparse import ArgumentParser

def upload(args):
    # This should use funcitons defined in a flickr interface module along with the metadata stuff from datastore
    # to upload files in the correct places after running them through the data2png type scripts
    print 'Uploading {0} using {1} encoding...'.format(args.filename, args.encoding)

def download(args):
    print 'Downloading {0}...'.format(args.filename)

def list(args):
    print 'Listing files...'
    db = Datastore(args.username)
    db.get_files()

def main():
    parser = ArgumentParser()
    parser.add_argument('username', help='Your Flickr username')
    subparsers = parser.add_subparsers(title='subcommands')

    parser_upload = subparsers.add_parser('upload', help='uploads files to Flickr')
    parser_upload.add_argument('filename')
    parser_upload.add_argument('-e', '--encoding', default='normal', choices=['raw','normal','stealth'])
    parser_upload.set_defaults(func=upload)

    parser_download = subparsers.add_parser('download', help='downloads files from Flickr')
    parser_download.add_argument('filename')
    parser_download.set_defaults(func=download)

    parser_filelist = subparsers.add_parser('list', help='lists files stored on Flickr')
    parser_filelist.set_defaults(func=list)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
