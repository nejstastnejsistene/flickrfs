#!/usr/bin/env python

import sys
import flickrfs

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write('Usage: {0}: <filename>'.format(*sys.argv))
        sys.exit(2)
    for pngfile in flickrfs.encodepng(sys.argv[1]):
        print pngfile
