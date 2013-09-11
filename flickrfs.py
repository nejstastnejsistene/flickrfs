import math
import os
import sys
import tempfile
from PIL import Image


# Break up large files to avoid flickr's filesize limit and
# to quicken upload and download times.
CHUNK_SIZE = 2**20 # 1MB


def encodepng(filename, infile=None, chunk_size=CHUNK_SIZE):
    '''Encode data into multiple PNG files.

       This reads data from infile (defaulting to stdin) and encodes the raw
       data into grayscale PNG images. If the data is larger than CHUNK_SIZE,
       The data will be split across multiple PNG files each containing at
       most CHUNK_SIZE data. To handle the multiple image streams, this
       function returns a generator which yields PNG filenames.

       Example usage:

       import tempfile
       for pngfile in encodepng('README.md'):
           print pngfile
    '''

    tempdir = tempfile.mktemp(prefix='flickrfs-')
    os.mkdir(tempdir)
    basename = os.path.basename(filename)
    outfilename = os.path.join(tempdir, basename)

    # If infile is not specified try filename if it exists, otherwise
    # use stdin.
    close = False
    if infile is None:
        try:
            infile = open(filename)
            close = True
        except IOError:
            infile = sys.stdin

    # Read the first chunk.
    part = 0
    chunk = infile.read(chunk_size)

    # Run until the end of data.
    while chunk:
        # Create a square image to minimize the number of pixels.
        size = int(math.ceil(len(chunk) ** 0.5))

        # Create new square grayscale image.
        img = Image.new('L', (size, size))

        # Read the chunk into the image, padding with null bytes.
        img.fromstring(chunk.ljust(size*size, '\0'))

        fname = outfilename
        if part > 0:
            fname += '.part' + str(part)
        fname += '.png'
        # Yield a file like object containing the png.
        with open(fname, 'w+') as outfile:
            img.save(outfile, 'png')
        yield fname
        
        # Read the next chunk.
        chunk = infile.read(chunk_size)
        part += 1

    # Close the file if applicable.
    if close:
        infile.close()


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
