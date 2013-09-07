import os
import random
import tempfile
from PIL import Image


CHUNK_SIZE = 2**25 # 32MB


class FlickrFS(object):

    def __init__(self, enc_cls, *args):
        self.enc = enc_cls(*args) # FIXME

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

    def __init__(self, size=None):
        self.size = size or self.default_size
        self.chunk_size = self.size[0] * self.size[1]

    def encode(self, filename):
        # Create a new image and load the image data.
        img = self._create_image()
        loaded = img.load()
        with open(filename) as f:
            self._encode_data(img, f.read())
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
                self._decode_data(output, img, start, end)
                # Delete intermediate tempfile.
                os.unlink(filename)
        return tmp


class NaiveEncoder(PngEncoder):
    '''Encodes data space-efficiently in grayscale PNGs.'''

    default_size = 2**14, 2**13 # 128MB

    def _create_image(self):
        return Image.new('P', self.size)

    def _encode_data(self, img, data):
        # Read the data and pad with null bytes.
        img.fromstring(data.ljust(self.chunk_size, '\0'))

    def _decode_data(self, out, img, start, end):
        out.write(img.tostring()[start:end])


class AlphaEncoder(PngEncoder):
    '''Save the image in the alpha pixels of an image.'''

    def __init__(self, base_image):
        base_image = Image.open(base_image)
        PngEncoder.__init__(self, base_image.size)
        self.base_image = base_image.load()

    def _create_image(self):
        return Image.new('RGBA', self.size)

    def _encode_data(self, img, data):
        bitmap = img.load()
        width, height = img.size
        for x in range(width):
            for y in range(height):
                try:
                    alpha = ord(data[x * height + y])
                except IndexError:
                    alpha = random.getrandbits(8)
                bitmap[x, y] = self.base_image[x, y] + (alpha,)

    def _decode_data(self, out, img, start, end):
        bitmap = img.load()
        height = img.size[1]
        for i in range(start, end):
            x, y =  divmod(i, height)
            out.write(chr(bitmap[x, y][3]))


if __name__ == '__main__':
    import StringIO
    fss = [ FlickrFS(NaiveEncoder, (5, 5))
          , FlickrFS(AlphaEncoder, 'favicon.jpg')
          ]
    for fs in fss:
        result = StringIO.StringIO()
        fname = None
        offset = 0
        for filename, n in fs.append(fname, offset, 'README.md'):
            tmp = fs.enc.decode((filename, offset, n))
            with open(tmp) as f:
                result.write(f.read())
            if fname != tmp and fname is not None:
                os.unlink(fname)
            fname = tmp
            offset += n
            offset %= fs.enc.chunk_size
        with open('README.md') as f:
            assert f.read() == result.getvalue(), 'It does not work :O'
            print fs.enc.__class__.__name__, 'works! :D'
