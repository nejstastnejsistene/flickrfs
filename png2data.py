#!/usr/bin/env python

import os
import sys
import tempfile
import flickrfs


def consumefiles(filenames):
    '''Yield open files and then unlink them, given a list of filenames.'''
    for filename in filenames:
        with open(filename) as f:
            yield f
        os.unlink(filename)

if __name__ == '__main__':
    files = consumefiles(sys.stdin.read().split())
    flickrfs.decodepngs(files)
