#!/usr/bin/env python

import sys
import flickrfs

if __name__ == '__main__':
    for photoid in flickrfs.flickrupload(sys.stdin.read().split()):
        print photoid
