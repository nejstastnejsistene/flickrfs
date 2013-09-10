#!/usr/bin/env python

import math
import sys
import tempfile
from PIL import Image

# Break up large files to avoid flickr's filesize limit and
# to quicken upload and download times.
CHUNK_SIZE = 2**20 # 1MB


if __name__ == '__main__':
    # Read the first chunk.
    chunk = sys.stdin.read(CHUNK_SIZE)

    # Run until the end of data.
    while chunk:
        # Create a square image to minimize the number of pixels.
        size = int(math.ceil(len(chunk) ** 0.5))

        # Create new square grayscale image.
        img = Image.new('L', (size, size))

        # Read the chunk into the image, padding with null bytes.
        img.fromstring(chunk.ljust(size*size, '\0'))

        # Save to a temporary file, and print the filename.
        filename = tempfile.mktemp() + '.png'
        img.save(filename, 'png')
        print filename
        
        # Read the next chunk.
        chunk = sys.stdin.read(CHUNK_SIZE)
