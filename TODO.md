# ToDo List #

### Required ###

 + Decide on exact storage format (tar all files? chunking how? etc.)
    + We could use `tar` which is really easy, and is useful if you are using lots of small images. Chunking currently works by chopping up large files into 128MB chunks and using one png file for each chunk.
 + Build flickr interface using python lib flickrapi to store/retrieve images
    + I took a look at it and `flickerapi` seems really easy to use, but it won't work from a command line environment, it needs to be a web app. See the comments on oauth and cli below.
 + Build logic to translate from filename => image(s) required to download/upload
    + If we use tar:
        + `tar c -O <filenames> | ./data2png.py`
        + `echo <png names> | ./png2data.py | tar x`
    + Otherwise:
        + `cat <filename> | ./data2png.py`
        + `echo <png names> | ./png2data.py`
 + Decide on purpose of webapp (general storage/retrieval or something like empty yo dropbox)
 + Decide on exact metadata format (What we need to save)
    + Needs a list of filenames/urls to represent the chunks of a file, as well as the size in bytes of the data stored in a chunk.
    + If using tar, we will probably need to list the files stored in each image.
 + Implement OAuth credentialing and saving of credentials
    + This will require a website to handle the oauth callbacks. To review, auth works by sending users to a url where they authenticate with flickr, then that url will have a callback that will request our webserver to complete the authentication.
 + Build out CLI client to tie everything together
    + I'm not sure if CLI is the best because the api keys required are for the application and not for the user, and it seems rather inelegant and counterintuitive to be passing all the app keys, username, etc into the cli command. Plus the flickr authentication will require a web browser of some sort.
 + Work on presentation
 
### Priority ###

 + Implement automatic flushing of metadata to special Flickr pic, allow CLI client to initialize DB from this instead of our servers
 + Encrypt data if requested (?)
 + Build nice UI for webapp
 + Integrate with other API's (?)
 
### Other ###

 + DataViz (?)
 + Enable supereasy sharing of files via links (will Flickr API make this easy?)
 + Figure out how to do 2-way integration (pushing and pulling files) with Dropbox or Skydrive
 + Perf
 + Allow users to make files public and utilizing them in de-duping similar uploads from other users (!)
 + Mass-register 1M Flickr accounts, then upload 1TB of /dev/random via FUFlickr from thousands of micro EC2 instances (aka Fuck U, Flickr)
 + Don't do item above
