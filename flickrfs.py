import os
import random
import tempfile
from PIL import Image


CHUNK_SIZE = 2**25 # 32MB


class FlickrFS(object):

    def __init__(self, enc_cls, *args):
        self.enc = enc_cls(*args) # FIXME
        self.current_blob = None
        self.current_offset = 0

    def append(self, filename):
        '''Yield tuples containing (chunk_filename, bytes_written), where
           chunk_filename is encoded as a PNG file.'''
        for chunk_filename, bytes_written in self._append(filename):
            # TODO Metadata happens here?
            # A simple png encoding layer on top of _append.
            tmp = self.enc.encode(chunk_filename) 
            yield tmp, bytes_written
            # Delete the intermediate blob.
            os.unlink(chunk_filename)

    def _append(self, filename):
        '''Yield tuples containing (chunk_filename, bytes_written).'''
        with open(filename) as data:
            while True:
                # Use a new temp file if no blob is specified.
                if self.current_blob is None:
                    self.current_blob = tempfile.mktemp()

                # Append to the blob.
                with open(self.current_blob, 'w+') as blob:
                    blob.seek(self.current_offset)
                    n = self.enc.chunk_size - self.current_offset
                    chunk = data.read(n)
                    if not chunk:
                        break
                    blob.write(chunk)
                    self.current_offset += len(chunk)
                    self.current_offset %= self.enc.chunk_size
                yield self.current_blob, len(chunk)

                # Reset filename and offset, and repeat.
                self.current_blob, self.current_offset, = None, 0


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

    default_size = 2**14, 2**13 # 128MB

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
    fss = [ FlickrFS(NaiveEncoder, (5, 5))
          , FlickrFS(AlphaEncoder, 'favicon.jpg')
          , FlickrFS(LowBitEncoder, 'favicon.jpg')
          , FlickrFS(DoubleEncoder, 'favicon.jpg')
          ]
    for fs in fss:
        result = StringIO.StringIO()
        # Save just enough metadata to decode files.
        last_blob = None
        last_offset = fs.current_offset
        for filename, n in fs.append('README.md'):
            tmp = fs.enc.decode((filename, last_offset, n))
            with open(tmp) as f:
                result.write(f.read())
            # Delete old blobs.
            if last_blob != tmp and last_blob is not None:
                os.unlink(last_blob)
            # Update metadata.
            last_blob = tmp
            last_offset = fs.current_offset
            #print result.getvalue()
        with open('README.md') as f:
            assert f.read() == result.getvalue(), 'It does not work :O'
            print fs.enc.__class__.__name__, 'works! :D'
