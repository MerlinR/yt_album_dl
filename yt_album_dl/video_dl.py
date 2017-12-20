#!/usr/bin/python
#==============================================================================
#Title           :lib/video_dl.py
#Description     :The simple way of embedding youtube_dl into a python script,
#                 and tucked away into a class.
__author__	= "Merlin Roe"
#Date            :07/10/2017
__version__	= "0.2"
#Usage           :python lib/video_dl.py
#Notes           :
#Python_version  :2.7.13
#==============================================================================

import sys
import os
import youtube_dl

class ydl_logger(object):
    def debug(self, msg):
        pass
    def warning(self, msg):
        pass
    def error(self, msg):
        print(msg)

def yt_d_hook(d):
        if d['status'] == 'downloading':
            sys.stdout.write('\r\033[K')
            sys.stdout.write('\tDownloading video | ETA: {} seconds'.format(str(d["eta"])))
            sys.stdout.flush()
        elif d['status'] == 'finished':
            sys.stdout.write('\r\033[K')
            sys.stdout.write('\tDownload complete\n')
            sys.stdout.flush()

class yt_downloader:

    url = ""

    ydl_opts = {
        'writethumbnail': 'true',           # Saves stillshot of youtube video as JPG
        'writeinfojson': 'true',            # Stores JSON file of video info, including segments of video.
        'format': 'bestaudio/best',         # Format
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0',
        }],
        'outtmpl': '%(id)s.%(ext)s',        # Output save format
        'logger': ydl_logger(),
        'progress_hooks': [yt_d_hook],
    }

    def __init__(self, url):
        self.url = url
        self.validationCheck()

    def downloadVideo(self):
        print self.url
        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([self.url])

    def setDownloadPath(self, path):
        self.ydl_opts['outtmpl'] = path + self.ydl_opts['outtmpl']

    def validationCheck(self):
        if("youtube" not in self.url):
            print "Currently only supports youtube"
            quit()