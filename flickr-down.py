#!/usr/bin/env python

import sys
import flickrfs

if __name__ == '__main__':
    for filename in flickrfs.flickrdownload(sys.stdin.read().split()):
        print filename
