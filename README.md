pennapps
========

Fall 2013 PennApps

### Setup virtualenv for the python script

    virtualenv env
    source env/bin/activate
    pip install -r requirements.txt

### Example usage for data2png.py and png2data.py

    ./data2png.py README.md
    # /tmp/flickrfs-abcdef/README.md.png <- temp file containing the image
    echo ahoj | ./data2png.py ahoj.txt | ./png2data.py
    # ahoj <- the temporary file from the intermediate step was deleted

### How everything works together

    ./data2png.py README.md | ./flickr-up.py
    # 0123456789 <- photo id
    echo <photo id> | ./flickr-down.py | ./png2data.py
    # <contents of README.md after round trip>
