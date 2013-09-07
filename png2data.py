#!/usr/bin/env python

import os
import sys
from PIL import Image


if __name__ == '__main__':
    # Iterate over a list of filenames from stdin.
    for filename in sys.stdin.read().split():

        # Open the file as an image.
        img = Image.open(filename)

        # Write the decoded image chunk to stdout.
        sys.stdout.write(img.tostring())
        
        # Delete temporary file now that it has been decoded.
        os.unlink(filename)

