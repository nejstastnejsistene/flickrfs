import tempfile

CHUNK_SIZE = 2**27 # 128MB

class FlickrFS(object):

    def append(self, blob_filename, offset, data_filename):
        '''Yield tuples containing (chunk_filename, bytes_written).'''
        with open(data_filename) as data:
            while True:
                # Use a new temp file if blob_filename is None.
                if blob_filename is None:
                    blob_filename = tempfile.mktemp()

                # Append to the blob.
                with open(blob_filename, 'a+') as blob:
                    chunk = data.read(CHUNK_SIZE - offset)
                    if not chunk:
                        break

                    blob.write(chunk)
                    yield blob_filename, len(chunk)

                # Reset filename and offset, and repeat.
                blob_filename, offset = None, 0


if __name__ == '__main__':
    # For testing!
    import sys
    fnames = set()
    fname = None
    offset = 0
    for i in range(10):
        for fname, n in FlickrFS().append(fname, offset, sys.argv[0]):
            fnames.add(fname)
            print 'using file', fname
            print n, 'bytes were written'
            offset += n
        print 'offset is', offset
    print fnames
