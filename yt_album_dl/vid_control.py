#!/usr/bin/python
#==============================================================================
#Title           :lib/video_class.py
#Description     :Essentially a Struct class, is called with the video ID and path, 
#                 which it builds the file Paths. Using the class destructor to
#                 delete the remaing files after re-formating song(s)
__author__	= "Merlin Roe"
#Date            :07/10/2017
__version__	= "0.2"
#Usage           :python lib/video_class.py
#Notes           :
#Python_version  :2.7.13
#==============================================================================

import sys
import os
import json

class video_data:

    def __init__(self, GivenVideoID, GivenVideoPath):
        self.video_id = GivenVideoID
        self.video_path = GivenVideoPath + self.video_id + '.wav'
        self.json_path = GivenVideoPath + self.video_id + '.info.json'
        self.img_path = GivenVideoPath + self.video_id + '.jpg'

        with open(self.json_path) as data_file:    
            self.jsonVideoData = json.load(data_file)

    def deleteTempFiles(self):
        os.remove(self.video_path)
        os.remove(self.json_path)
        os.remove(self.img_path)

    # Using class destructor to delete the remnants of the download.
    def __del__(self):
        self.deleteTempFiles()