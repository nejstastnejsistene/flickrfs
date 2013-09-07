#!/usr/bin/env python

import sys
import tempfile
from PIL import Image

if __name__ == '__main__':
    data = sys.stdin.read()
    size = int(len(data) ** 0.5 + 1)
    img = Image.new('P', (size, size))
    img.fromstring(data.ljust(size*size, '\0'))
    filename = tempfile.mktemp() + '.png'
    img.save(filename, 'png')
    print filename
