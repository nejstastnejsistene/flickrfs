#!/usr/bin/env python

import os
import sys
from PIL import Image


if __name__ == '__main__':
    # Iterate over a list of filenames from stdin.
    for filename in sys.stdin.read().split():

        # Open the file as an image.
        img = Image.open(filename)

        src_pix = img.load()
        #raw_img_str = img.tostring()
        '''
        for i in range(3, len(raw_img_str), 4):
            sys.stdout.write(raw_img_str[i])
        '''    

        
        # TODO: change to deal with varying start and end position
        for x in range(img.size[0]):
            for y in range(img.size[1]):
                sys.stdout.write(chr(src_pix[x,y][3]))
        

        #print "LOOP DONE"
        # Write the decoded image chunk to stdout.
        # sys.stdout.write(decrypt_buff.getvalue())
        #decrypt_buff.close()

        # Delete temporary file now that it has been decoded.
        os.unlink(filename)

