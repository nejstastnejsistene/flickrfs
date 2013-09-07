import os
import random
import tempfile
from PIL import Image

from datastore import Datastore


def mktemp():
    return tempfile.mktemp(prefix='flickrfs_')

class FlickrFS(object):

    def __init__(self, encoder, store):
        self.encoder = encoder
        self.store = store
        # TODO read this from the store.
        self.files = {}
        self.current_blob = None
        self.current_blob_id = None
        self.current_offset = 0

    def __getitem__(self, key):
        if isinstance(key, basestring):
            # Retrive a file.
            return self.encoder.decode(*self.files[key])

    def add(self, filename):
        for filename, blob_id in self.append(filename):
            print 'uploading', filename, 'to', blob_id
            # if blob_id is None
            #   create new file in flickr and save the blob_id
            # else
            #   update blog_id
            # os.ulink(filename)

        # Save the metadata.
        self.store.put_file_metadata(filename, {
            'files': self.files,
            'current_blob': self.current_blob,
            'current_blob_id': self.current_blob_id,
            'current_offset': self.current_offset,
            })

    def append(self, filename):
        '''Yield tuples containing (blob_filename, blob_id),
           where blob_filename is encoded as a PNG file.'''
        if filename in self.files:
            raise KeyError, "file '{}' already exists".format(filename)
        self.files[filename] = []
        for blob_filename, blob_id in self._append(filename):
            # A simple png encoding layer on top of _append.
            tmp = self.encoder.encode(blob_filename) 
            yield tmp, blob_id
            self.files[filename][-1][0] = tmp # FIXME
            # Delete the intermediate blob.
            os.unlink(blob_filename)

    def _append(self, filename):
        '''Yield tuples containing (blob_filename, blob_id).'''
        with open(filename) as data:
            while True:
                # Use a new temp file if no blob is specified.
                if self.current_blob is None:
                    self.current_blob = mktemp()

                # Append to the blob.
                with open(self.current_blob, 'w+') as blob:
                    blob.seek(self.current_offset)
                    n = self.encoder.chunk_size - self.current_offset
                    chunk = data.read(n)
                    if not chunk:
                        break
                    blob.write(chunk)

                    # Append this chunk to the filename.
                    self.files[filename].append([self.current_blob_id,
                        self.current_offset, len(chunk)])

                    # Update the offset.
                    self.current_offset += len(chunk)
                    self.current_offset %= self.encoder.chunk_size

                yield self.current_blob, self.current_blob_id

                if self.current_offset == 0:
                    self.current_blob = None
                    self.current_blob_id = None


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
        tmp = mktemp() + '.png'
        img.save(tmp, 'png')
        return tmp

    def decode(self, *chunks):
        # Open a new temp file.
        tmp = mktemp()
        with open(tmp, 'w+') as output:
            # Iterate through chunks.
            for filename, start, end in chunks:
                # Write slice of chunk to output file.
                img = Image.open(filename)
                self._decode_data(output, img, start, end)
                # Delete intermediate tempfile.
                os.unlink(filename)
        return tmp

    def _create_image(self):
        '''Create a PIL image that the converted PNG will be stored in.'''
        raise NotImplementedError

    def _encode_data(self, img, data):
        '''Encode `data` into the PIL image `img`.'''
        raise NotImplementedError

    def _decode_data(self, out, img, start, end):
        '''Write the data stored in `img` from `start` to `end` into `out`.'''
        raise NotImplementedError



class NaiveEncoder(PngEncoder):
    '''Encodes data space-efficiently in grayscale PNGs.'''

    default_size = 2**10, 2**10 # 1MB

    def _create_image(self):
        return Image.new('P', self.size)

    def _encode_data(self, img, data):
        # Read the data and pad with null bytes.
        img.fromstring(data.ljust(self.chunk_size, '\0'))

    def _decode_data(self, out, img, start, end):
        out.write(img.tostring()[start:end])

class AlphaEncoder(PngEncoder):
    '''Save the data in the alpha pixels of an image.'''

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
                #print "acoord:", x, y
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

class LowBitEncoder(PngEncoder):
    '''save data in the low bits of the color values '''

    def __init__(self, base_image):
        base_image = Image.open(base_image)
        PngEncoder.__init__(self, base_image.size)
        self.base_image = base_image.load()

    def _create_image(self):
        return Image.new('RGB', self.size)

    def _encode_data(self, img, data):
        bitmap = img.load()
        width, height = img.size
        for x in range(width):
            for y in range(height):
                try:
                    byte_to_add = ord(data[x * height + y])
                    
                except IndexError:
                    byte_to_add = random.getrandbits(8)

                r_dat = byte_to_add >> 6
                g_dat = (byte_to_add >> 3) & 0b111
                b_dat = byte_to_add & 0b111
                
                r_val = (self.base_image[x , y][0] & 0b1111100) | (r_dat)
                g_val = (self.base_image[x , y][1] & 0b1111000) | (g_dat)
                b_val = (self.base_image[x , y][2] & 0b1111000) | (b_dat)
                
                bitmap[x, y] = (r_val, g_val, b_val)

    def _decode_data(self, out, img, start, end):
        bitmap = img.load()
        height = img.size[1]
        for i in range(start, end):
            x, y =  divmod(i, height)
            color_vals = bitmap[x,y]
            from_r = color_vals[0] & 0b11
            from_g = color_vals[1] & 0b111
            from_b = color_vals[2] & 0b111
            recovered_byte = (from_r << 6) | (from_g << 3) | (from_b)
            out.write(chr(recovered_byte))



class DoubleEncoder(PngEncoder):
    '''Save the data in the alpha pixels and the rgb values of an image.'''

    def __init__(self, base_image):
        base_image = Image.open(base_image)
        width , height = base_image.size
        # we need to lie about the image size in order to get enough data
        PngEncoder.__init__(self, (2*width, height))
        self.base_image = base_image.load()

    def _create_image(self):
        return Image.new('RGBA', self.size)

    def _encode_data(self, img, data):
        bitmap = img.load()
        width, height = img.size
        #print "encoding..."
        for x in range(width/2):
            for y in range(height):
                #print "coords:", x, y
                try:
                    byte_to_add = ord(data[x * height*2 + y*2])
                except IndexError:
                    byte_to_add = random.getrandbits(8)

                r_dat = byte_to_add >> 6
                g_dat = (byte_to_add >> 3) & 0b111
                b_dat = byte_to_add & 0b111
                
                r_val = (self.base_image[x , y][0] & 0b1111100) | (r_dat)
                g_val = (self.base_image[x , y][1] & 0b1111000) | (g_dat)
                b_val = (self.base_image[x , y][2] & 0b1111000) | (b_dat)
                
                try:
                    alpha = ord(data[x * height*2 + y*2 + 1])
                except IndexError:
                    alpha = random.getrandbits(8)

                #print alpha
                bitmap[x, y] = (r_val, g_val, b_val, alpha)


    def _decode_data(self, out, img, start, end):
        bitmap = img.load()
        height = img.size[1]
        end = start+(end-start)/2
        #print "decoding..."
        for i in range(start, end):
            x, y =  divmod(i, height)
            color_vals = bitmap[x,y]
            from_r = color_vals[0] & 0b11
            from_g = color_vals[1] & 0b111
            from_b = color_vals[2] & 0b111
            recovered_byte = (from_r << 6) | (from_g << 3) | (from_b)
            out.write(chr(recovered_byte))
            out.write(chr(bitmap[x, y][3]))



if __name__ == '__main__':
    import StringIO
    store = Datastore('test')
    fss = [ FlickrFS(NaiveEncoder((5, 5)), store)
          , FlickrFS(AlphaEncoder('favicon.jpg'), store)
          , FlickrFS(LowBitEncoder('favicon.jpg'), store)
          , FlickrFS(DoubleEncoder('favicon.jpg'), store)
          ]
    testfile = 'README.md'
    for fs in fss:
        store.clear()
        fs.add(testfile)
        with open(fs[testfile]) as result, open(testfile) as control:
            assert result.read() == control.read()

