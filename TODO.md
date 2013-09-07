# ToDo List #

### Required ###

 + ~~Decide on exact storage format (tar all files? chunking how? etc.)~~
 + ~~Build flickr interface using python lib flickrapi to store/retrieve images~~
 + ~~Build logic to translate from filename => image(s) required to download/upload~~
 + ~~Decide on purpose of webapp (general storage/retrieval or something like empty yo dropbox)~~
 + ~~Decide on exact metadata format (What we need to save)~~
 + ~~Implement OAuth credentialing and saving of credentials~~
 + Build out CLI client to tie everything together
    + I'm not sure if CLI is the best because the api keys required are for the application and not for the user, and it seems rather inelegant and counterintuitive to be passing all the app keys, username, etc into the cli command. Plus the flickr authentication will require a web browser of some sort.
 + Make website landing page pretty
 + Work on presentation
 
### Priority ###

 + Implement automatic flushing of metadata to special Flickr pic, allow CLI client to initialize DB from this instead of our servers
 + Encrypt data if requested (?)
    + As I described above I don't believe a CLI is feasible with oauth, and I can't think of any "safe" way of handling encryption server-side. I think this is a no go unless Brett feels up to hacking in some javascript AES to do client-side encryption.
 + Integrate with other API's (?)
 
### Other ###

 + DataViz (?)
 + Enable supereasy sharing of files via links (will Flickr API make this easy?)
 + Figure out how to do 2-way integration (pushing and pulling files) with Dropbox or Skydrive
 + Perf
 + Allow users to make files public and utilizing them in de-duping similar uploads from other users (!)
 + Mass-register 1M Flickr accounts, then upload 1TB of /dev/random via FUFlickr from thousands of micro EC2 instances (aka Fuck U, Flickr)
 + Don't do item above
