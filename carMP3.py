#!/usr/bin/python3
'''
Tool to maximise volume and randomise play order for MP3 files on a Flash
disk for use in a cheapo car MP3 player that doesn't have a random play
feature.

You need to have the Python 3 pytaglib library and the mp3gain command
line tool installed.  There are Ubuntu packages for this, libtag1-dev and
mp3gain.  Then sudo easy_install3 pytaglib.  (There is an Ubuntu package
for pytaglib but Eclipse / PyDev doesn't want to play nice with it at the time
of writing.)  

You'll also need Python 3. Python 3 is good. Python 2 is soooo 2000.

'''
import copy
import os
import random
import re
import shutil
import string
import subprocess
import sys
import taglib
import tempfile


def idGenerator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def main(cardDir):

    # Get a temporary directory on the local hard disk for working on since
    # Flash drives are veeery slow for manipulating MP3 files
    tmpDirObj = tempfile.TemporaryDirectory()
    tmpDirName = tmpDirObj.name
    print(tmpDirName)
    
    # For every file on the Flash drive...
    for file in os.listdir(cardDir):
        if re.match(r'^.*?mp3$', file): 
            print(file)
            tmpFile = tmpDirName + '/' + file
            # Copy files from Flash to temporary directory on hard disk
            shutil.copyfile(cardDir + '/' + file, tmpFile)
            # Read the MP3 file's ID3 track information since mp3gain 
            # will stomp on certain versions (e.g. V1) of ID3 tag information
            id3r = taglib.File(tmpFile)
            originalTags = copy.deepcopy(id3r.tags)
            # Maximise volume of track
            subprocess.call(['mp3gain', '-r', '-k',  tmpFile])
            # Re-write the track information to the MP3 file
            id3r = taglib.File(tmpFile)
            id3r.tags.update(originalTags)
            id3r.save()

    trackListing = ''
   
    # Rename every file in the temporary directory on the hard disk
    # with a randomised 8.3 file name so that the dumb MP3 player doesn't
    # play all the MP3 files in alphanumeric order (no random play feature!)
    for file in os.listdir(tmpDirName):
        randomisedFileName = idGenerator(8).lower() + '.mp3'
        tmpFile = tmpDirName + '/' + file
        id3r = taglib.File(tmpFile)
        os.rename(tmpFile, tmpDirName + '/' + randomisedFileName)
        trackListing = trackListing + id3r.tags['ARTIST'][0] + '-' + \
            id3r.tags['TITLE'][0] + '-' + randomisedFileName + '\n'
        

    # Create a text file on the Flash drive that might be useful when
    # adding tracks at a later date since the file names are going to 
    # be randomised
    fhOut = open(cardDir + '/' + '000trackListing.txt', 'w')
    print(trackListing, file=fhOut)
    fhOut.close()
    
    # Sharp intake of breath - delete all the MP3 files on the Flash drive
    for file in os.listdir(cardDir):
        if re.match(r'^.*?mp3$', file): 
            os.remove(cardDir + '/' + file)
    
    # Copy all the files from hard disk to Flash drive       
    for file in os.listdir(tmpDirName):
        shutil.copyfile(tmpDirName + '/' + file, cardDir + '/' + file)
    
if __name__ == "__main__":
    main(sys.argv[1])
