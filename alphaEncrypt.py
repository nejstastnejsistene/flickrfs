#!/usr/bin/env python

from itertools import chain
import math
import sys
import tempfile
from PIL import Image
import random
import glob

def read_from_chunk(chunk, x, y, height):
    if len(chunk) > x*height + y:
        return ord(chunk[x*height + y])
    return random.randint(0,256)


if __name__ == '__main__':

    if len(sys.argv) != 2:
        sys.stderr.write("MISSING IMAGE DIRECTORY NAME\n")
        sys.exit(1)

    image_dir = sys.argv[1]
    
    image_choices = glob.glob(image_dir+'/*[.jpg^.png]')
#    print(image_choices)

    cur_image_name = random.choice(image_choices)
    hide_behind = Image.open(cur_image_name)

    #print hide_behind.size

    #define chunk size
    CHUNK_SIZE = hide_behind.size[1] * hide_behind.size[0]

    # Read the first chunk.
    chunk = sys.stdin.read(CHUNK_SIZE)

    # Run until the end of data.
    while chunk:
        # Create a square image to minimize the number of pixels.
        # size = int(math.ceil(len(chunk) ** 0.5))

        # Create new square RGBA image.
        img = Image.new('RGBA', (hide_behind.size[0], hide_behind.size[1]))

        hiding_pix = hide_behind.load()
        encrypted_pix = img.load()

        # print hiding_pix[10,20]
        # print encrypted_pix[1,20]

        width = hide_behind.size[0]
        height = hide_behind.size[1]
        
        for x in range(width):
            for y in range(height):
                encrypted_pix[x , y] = hiding_pix[x , y] + (read_from_chunk(chunk,x,y, height) ,)

        # Save to a temporary file, and print the filename.
        filename = tempfile.mktemp() + '.png'
        img.save(filename, 'png')
        print filename

        #select next image
        cur_image_name = random.choice(image_choices)
        hide_behind = Image.open(cur_image_name)
        # define chunk size
        CHUNK_SIZE = hide_behind.size[1] * hide_behind.size[0]

        # Read the next chunk.
        chunk = sys.stdin.read(CHUNK_SIZE)
