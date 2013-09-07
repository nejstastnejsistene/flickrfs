pennapps
========

Fall 2013 PennApps

### Setup virtualenv for the python script

    virtualenv env
    source env/bin/activate
    pip install -r requirements.txt

### Example usage for data2png.py

    cat README.md | ./data2png.py
    # /tmp/abcdefgh.png <- a temporary file where the image is stored
