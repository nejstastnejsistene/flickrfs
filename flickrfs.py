import math
import os
import sys
from StringIO import StringIO
from PIL import Image


# Break up large files to avoid flickr's filesize limit and
# to quicken upload and download times.
CHUNK_SIZE = 2**20 # 1MB


def encodepng(infile=sys.stdin):
    '''Encode data into multiple PNG files.

       This reads data from infile (defaulting to stdin) and encodes the raw
       data into grayscale PNG images. If the data is larger than CHUNK_SIZE,
       The data will be split across multiple PNG files each containing at
       most CHUNK_SIZE data. To handle the multiple image streams, this
       function returns a generator which yields file-like objects containing
       PNG images.

       Example usage, which saves the chunked files to tempfiles:

       import tempfile
       for pngfile in encodepng():
           filename = tempfile.mktemp()
           with open(filename, 'w+') as f:
               f.write(pngfile.read())
           print filename
    '''

    # Read the first chunk.
    chunk = infile.read(CHUNK_SIZE)

    # Run until the end of data.
    while chunk:
        # Create a square image to minimize the number of pixels.
        size = int(math.ceil(len(chunk) ** 0.5))

        # Create new square grayscale image.
        img = Image.new('L', (size, size))

        # Read the chunk into the image, padding with null bytes.
        img.fromstring(chunk.ljust(size*size, '\0'))

        # Yield a file like object containing the png.
        outfile = StringIO()
        img.save(outfile, 'png')
        outfile.seek(0)
        yield outfile
        
        # Read the next chunk.
        chunk = infile.read(CHUNK_SIZE)


def decodepngs(pngfiles, outfile=sys.stdout):
    '''Read in PNG files, and write out the data encoded within them.

       This uses a sequence of PNG file objects (pngfiles) and concatenates
       their stored data to outfile (defaulting to stdout).

       Example usage:
       
       # Prints to stdout the data encoded within foo.png and bar.png.
       with open('foo.png') as foo, open('bar.png') as bar:
           decodepngs([foo, bar])
    '''

    for pngfile in pngfiles:

        # Open the file as an image.
        img = Image.open(pngfile)

        # Retrieve the contents from within the png.
        outfile.write(img.tostring())
