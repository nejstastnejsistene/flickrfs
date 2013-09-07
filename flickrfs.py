import os
import random
import tempfile
from PIL import Image

from datastore import Datastore
from storage import FStore


def mktemp():
    return tempfile.mktemp(prefix='flickrfs_')

class FlickrFS(object):

    def __init__(self, encoder, store, fstore):
        self.encoder = encoder
        self.store = store
        self.fstore = fstore
        self.files = store.get_files_metadata()

    def _clear(self):
        '''For debugging'''
        self.store.clear()
        self.files = store.get_files_metadata()

    def __getitem__(self, key):
        if isinstance(key, basestring):
            # Retrive a file.
            return self.encoder.decode(*self.files[key]['chunks'])

    def add(self, filename):
        if filename in self.files:
            raise KeyError, "file '{}' already exists".format(filename)
        self.files[filename] = {}
        self.files[filename]['chunks'] = []
        chunks = []
        for png_file, blob_id in self.append(filename):
            print 'uploading', png_file, 'to', blob_id
            #if blob_id is not None
            #    fstore._delete(blob_id)
            #blob_id, = fstore._upload([filename])
            blob_id = png_file # Remove this when flickr gets integrated
            fdata = self.files[filename]['chunks'].pop(0)
            chunks.append([blob_id] + fdata[1:])
            #os.unlink(filename)

        # Save the metadata.
        self.files[filename]['chunks'] = chunks
        self.store.put_files_metadata(filename, self.files[filename])

    def append(self, filename):
        '''Yield tuples containing (blob_filename, blob_id),
           where blob_filename is encoded as a PNG file.'''
        for blob_filename, blob_id in self._append(filename):
            # A simple png encoding layer on top of _append.
            tmp = self.encoder.encode(blob_filename) 
            yield tmp, blob_id
            #self.files[filename][-1][0] = tmp # FIXME
            # Delete the intermediate blob.
            os.unlink(blob_filename)

    def _append(self, filename):
        '''Yield tuples containing (blob_filename, blob_id).'''
        current_blob = self.files[filename].get('current_blob')
        current_blob_id = self.files[filename].get('current_blob_id')
        current_offset = self.files[filename].get('current_offset', 0)
        with open(filename) as data:
            while True:
                # Use a new temp file if no blob is specified.
                if current_blob is None:
                    current_blob = mktemp()

                # Append to the blob.
                with open(current_blob, 'w+') as blob:
                    blob.seek(current_offset)
                    n = self.encoder.chunk_size - current_offset
                    chunk = data.read(n)
                    if not chunk:
                        break
                    blob.write(chunk)

                    # Append this chunk to the filename.
                    self.files[filename]['chunks'].append(
                        [current_blob_id, current_offset, len(chunk)])

                    # Update the offset.
                    current_offset += len(chunk)
                    current_offset %= self.encoder.chunk_size

                yield current_blob, current_blob_id

                if current_offset == 0:
                    current_blob = None
                    current_blob_id = None
        self.files[filename]['current_blob'] = current_blob
        self.files[filename]['current_blob_id'] = current_blob_id
        self.files[filename]['current_offset'] = current_offset


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
                    #alpha = random.getrandbits(8)
                    return
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
                    #byte_to_add = random.getrandbits(8)
                    return

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
                ran_out = False
                #print "coords:", x, y
                try:
                    byte_to_add = ord(data[x * height*2 + y*2])
                except IndexError:
                    byte_to_add = random.getrandbits(8)
                    return

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
                    ran_out = True

                #print alpha
                bitmap[x, y] = (r_val, g_val, b_val, alpha)
                if ran_out:
                    return


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
                    #alpha = random.getrandbits(8)
                    return
                bitmap[x, y] = self.base_image[x, y] + (alpha,)

    def _decode_data(self, out, img, start, end):
        bitmap = img.load()
        height = img.size[1]
        for i in range(start, end):
            x, y =  divmod(i, height)
            out.write(chr(bitmap[x, y][3]))


class StealthEncoder(PngEncoder):
    '''Save the data in the alpha pixels of an image, and adjust the image to look good on flickr'''

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
                    adj_r = (255.0/alpha)*(self.base_image[x,y][0] + alpha - 255)
                    if adj_r < 0:
                        adj_r = 0
                    if adj_r > 255:
                        adj_r = 255
                    adj_g = (255.0/alpha)*(self.base_image[x,y][1] + alpha - 255)
                    if adj_g < 0:
                        adj_g = 0
                    if adj_g > 255:
                        adj_g = 255
                    adj_b = (255.0/alpha)*(self.base_image[x,y][2] + alpha - 255)
                    if adj_b < 0:
                        adj_b = 0
                    if adj_b > 255:
                        adj_b = 255
                    bitmap[x,y] = (int(adj_r), int(adj_g), int(adj_b), alpha)
                except IndexError:
                    alpha = 255
                    bitmap[x, y] = self.base_image[x, y] + (alpha,)

                
    def _decode_data(self, out, img, start, end):
        bitmap = img.load()
        height = img.size[1]
        for i in range(start, end):
            x, y =  divmod(i, height)
            out.write(chr(bitmap[x, y][3]))

if __name__ == '__main__':
    import StringIO
    store = Datastore('test')
    fstore = FStore('token')
    fss = [ FlickrFS(NaiveEncoder((5, 5)), store, fstore)
          , FlickrFS(AlphaEncoder('favicon.jpg'), store, fstore)
          , FlickrFS(LowBitEncoder('favicon.jpg'), store, fstore)
          #, FlickrFS(DoubleEncoder('favicon.jpg'), store, fstore)
           , FlickrFS(StealthEncoder('favicon.jpg'), store)
          ]
    testfile = 'README.md'
    testfile2 = 'flickrfs.py'
    for fs in fss:
        fs._clear()
        fs.add(testfile)
        fs.add('flickrfs.py')
        with open(fs[testfile]) as result, open(testfile) as control:
            assert result.read() == control.read()
        with open(fs[testfile2]) as result, open(testfile2) as control:
            assert result.read() == control.read(), fs.encoder.__class__
