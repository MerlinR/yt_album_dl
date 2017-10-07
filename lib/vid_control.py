#!/usr/bin/python
#==============================================================================
#Title           :lib/video_class.py
#Description     :Essentially a Struct class, is called with the video ID and path, 
#                 which it builds the file Paths. Using the class destructor to
#                 delete the remaing files after re-formating song(s)
__author__	= "Merlin Roe"
#Date            :07/10/2017
__version__	= "0.1"
#Usage           :python lib/video_class.py
#Notes           :
#Python_version  :2.7.13
#==============================================================================

import sys
import os
import json

class video_data:

    video_id = ""
    video_path = ""
    json_path = ""
    img_path = ""

    json_contents = None

    def __init__(self, given_id, given_path):

        self.video_id = given_id
        self.video_path = given_path + self.video_id + '.webm'
        self.json_path = given_path + self.video_id + '.info.json'
        self.img_path = given_path + self.video_id + '.jpg'

        with open(self.json_path) as data_file:    
            self.json_contents = json.load(data_file)

    def __del__(self):
        os.remove(self.video_path)
        os.remove(self.json_path)
        os.remove(self.img_path)


    def print_data(self):
        print self.video_id
        print self.video_path
        print self.json_path
        print self.img_path