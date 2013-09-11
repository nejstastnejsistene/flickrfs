import os
from StringIO import StringIO
from flickrfs import *

def test_without_chunking(filename='README.md'):
    with open(filename) as f:
        original_data = f.read()
    s = StringIO()
    decodepngs(flickrdownload(flickrupload(encodepng(filename))), outfile=s)
    assert s.getvalue()[:len(original_data)] == original_data

def test_with_chunking(filename='README.md'):
    with open(filename) as f:
        original_data = f.read()
    # Round down the image size to the next lower perfect square.
    chunk_size = int(len(original_data)**0.5)**2
    # Should split into 2 chunks, filename.png and filename.part2.png
    filenames = list(encodepng(filename, chunk_size=chunk_size))
    assert len(filenames) == 2, filenames
    assert os.path.basename(filenames[0]) == filename + '.png'
    assert os.path.basename(filenames[1]) == filename + '.part2.png'
    # Make sure it decodes properly as normal.
    s = StringIO()
    decodepngs(flickrdownload(flickrupload(filenames)), outfile=s)
    assert s.getvalue()[:len(original_data)] == original_data
