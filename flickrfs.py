import os
import tempfile
from PIL import Image


CHUNK_SIZE = 2**25 # 32MB


class FlickrFS(object):

    def __init__(self, size):
        self.enc = NaiveEncoder(size) # FIXME

    def append(self, *args):
        '''Yield tuples containing (chunk_filename, bytes_written), where
           chunk_filename is encoded as a PNG file.'''
        for chunk_filename, bytes_written in self._append(*args):
            # TODO Metadata happens here?
            # A simple png encoding layer on top of _append.
            tmp = self.enc.encode(chunk_filename) 
            yield tmp, bytes_written
            # Delete the intermediate blob.
            os.unlink(chunk_filename)

    def _append(self, blob_filename, offset, data_filename):
        '''Yield tuples containing (chunk_filename, bytes_written).'''
        with open(data_filename) as data:
            while True:
                # Use a new temp file if blob_filename is None.
                if blob_filename is None:
                    blob_filename = tempfile.mktemp()

                # Append to the blob.
                with open(blob_filename, 'w+') as blob:
                    blob.seek(offset)
                    chunk = data.read(self.enc.chunk_size - offset)
                    if not chunk:
                        break
                    blob.write(chunk)
                yield blob_filename, len(chunk)

                # Reset filename and offset, and repeat.
                blob_filename, offset = None, 0


class PngEncoder(object):
    def encode(self, filename):
        raise NotImplementedError
    def decode(self, filename):
        raise NotImplementedError


class NaiveEncoder(PngEncoder):
    '''Encodes data space-efficiently in grayscale PNGs.'''

    def __init__(self, size=(2**14, 2**13)):
        self.size = size
        self.chunk_size = size[0] * size[1]

    def encode(self, filename):
        img = Image.new('P', self.size)
        with open(filename) as f:
            # Read the data and pad with null bytes.
            data = f.read().ljust(self.chunk_size, '\0')
        # Load the data.
        img.fromstring(data)
        # Save to a temporary file.
        tmp = tempfile.mktemp() + '.png'
        img.save(tmp, 'png')
        return tmp

    def decode(self, *chunks):
        # Open a new temp file.
        tmp = tempfile.mktemp()
        with open(tmp, 'w+') as output:
            # Iterate through chunks.
            for filename, start, end in chunks:
                # Write slice of chunk to output file.
                img = Image.open(filename)
                output.write(img.tostring()[start:end])
                # Delete intermediate tempfile.
                os.unlink(filename)
        return tmp


if __name__ == '__main__':
    import StringIO
    fs = FlickrFS((5, 5))
    result = StringIO.StringIO()
    fname = None
    offset = 0
    for filename, n in fs.append(fname, offset, 'README.md'):
        tmp = fs.enc.decode((filename, offset, n))
        with open(tmp) as f:
            x = f.read()
            result.write(x)
        if fname != tmp and fname is not None:
            os.unlink(fname)
        fname = tmp
        offset += n
        offset %= fs.enc.chunk_size
    with open('README.md') as f:
        assert f.read() == result.getvalue(), 'It does not work :O'
