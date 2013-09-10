#!/usr/bin/env python

import tempfile
import flickrfs

if __name__ == '__main__':
    for pngfile in flickrfs.encodepng():
        filename = tempfile.mktemp()
        with open(filename, 'w+') as f:
            f.write(pngfile.read())
        print filename
