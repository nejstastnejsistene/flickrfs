#!/usr/bin/env python

from argparse import ArgumentParser

def upload(args):
    pass

def download(args):
    pass

def main():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(title='subcommands')

    parser_upload = subparsers.add_parser('upload', help='uploads files to flickr')
    parser_upload.add_argument('filename')
    parser_upload.set_defaults(func=upload)

    parser_download = subparsers.add_parser('download', help='downloads files from flickr')
    parser_download.add_argument('filename')
    parser_download.set_defaults(func=download)

    parser.parse_args()

if __name__ == '__main__':
    main()
