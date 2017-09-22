#!/usr/bin/python
#==============================================================================
#Title           :yt_download.py
#Description     :
__author__	= "Merlin Roe"
#Date            :19/09/2017
__version__	= "1.0"
#Usage           :python yt_download.py
#Notes           :
#Python_version  :2.7.13
#==============================================================================

import sys
import os
import re
import youtube_dl
import json
import argparse
from pydub import AudioSegment

class MyLogger(object):
    def debug(self, msg):
        pass
    
    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

def my_hook(d):
    if d['status'] == 'downloading':
        sys.stdout.write('\r\033[K')
        sys.stdout.write('\tDownloading video | ETA: {} seconds'.format(str(d["eta"])))
        sys.stdout.flush()
    elif d['status'] == 'finished':
        sys.stdout.write('\r\033[K')
        sys.stdout.write('\tDownload complete\n\tConverting video to wav\n')
        sys.stdout.flush()

ydl_opts = {
    'writethumbnail': 'true',
    'writeinfojson': 'true',
    'format': 'bestaudio/best',
    'outtmpl': '%(id)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
        'preferredquality': '0',
    }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}

video_info = {
        'URL': None,
        'id': None,
        'path': None,
        'video_path': None,
        'json_path': None,
        'img_path': None,
        'title_def': None,
        'artist_def': None,
        'album_def': None,
        'album_artist_def': None,
        'reverse_title': None
}

#########################################################################################################

def find_video_id(path):
    files = os.listdir(path)

    for fileN in files:
        if(".info.json" in fileN):
            return fileN.split('.')[0]

#########################################################################################################

def clean_filename(filename):
    return re.sub(r'[\\/\.\[\]\,\?\{\}\(\)\-]',"",filename) #Removes chars that could cause issues as file name.

#########################################################################################################

def split_title(title):

    #Split video title and clean up string, encode into utf-8 for metadata
    title = title.encode('utf-8')

    title = re.sub("\xe2\x80\x93", "-", title) #Fixes issues with "en dash"
    title = re.sub("\xe2\x80\x94", "-", title) #Fixes issues with "en dash"
    split_title = title.split(' - ')

    regex = re.compile(r"[\]\)\}]") #Split and clean first half (from brackets etc)
    if regex.search(split_title[0]):
        split_title[0] = regex.split(split_title[0])[1]

    regex = re.compile(r"^\d+[\.\)\s]") #remove any initial numbering within list
    if regex.search(split_title[0]):
        split_title[0] = regex.split(split_title[0])[1]
    
    split_title[0] = split_title[0].strip()

     #Split and clean second half (from brackets etc)
    regex = re.compile(r"(\s\()|(\s\[)|(\s\{)|(\s[w|W]/)")

    if regex.search(split_title[1]):
        split_title[1] = regex.split(split_title[1])[0]
    split_title[1] = split_title[1].strip()

    #return in order based on reverse of not.
    if(video_info['reverse_title']):
        return split_title[1].title(), split_title[0].title()
    else:
        return split_title[0].title(), split_title[1].title()

#########################################################################################################

def format_single(video, path, data):
    sys.stdout.write('\tVideo detected as single song.\n')
    sys.stdout.flush()

    ARTIST, TITLE = split_title(data['fulltitle'])
    
    if video_info['artist_def'] is not None:
        ARTIST = video_info['artist_def'][0]
    if video_info['album_def'] is not None:
        ALBUM = video_info['album_def'][0]
    if video_info['title_def'] is not None:
        TITLE = video_info['title_def'][0]

    FILE_NAME = "{}_{}".format(ARTIST, TITLE)
    FILE_NAME = clean_filename(FILE_NAME)

    video.export("{}{}.{}".format(path,FILE_NAME,"mp3"), 
        format="mp3", 
        tags={'artist': ARTIST, 'title': TITLE},
        cover=video_info['img_path']
    )

#########################################################################################################

def format_album(video, path, data):
    sys.stdout.write('Video is an album of the same artist.\n\tIf this is wrong, then well fuck.\n')
    sys.stdout.flush()

    ARTIST, ALBUM = split_title(data['fulltitle'])

    if video_info['artist_def'] is not None:
        ARTIST = video_info['artist_def'][0]
    if video_info['album_def'] is not None:
        ALBUM = video_info['album_def'][0]
    
    for i in range(0, len(data['chapters'])):

        regex = re.compile(r"(\s\()|(\s\[)|(\s\{)|(\s[w|W]/)")
        TITLE = data['chapters'][i]['title']

        if regex.search(TITLE):
            TITLE = regex.split(data['chapters'][i]['title'])[0]

        regex = re.compile(r"^\d+[\.\)\s]")
        if regex.search(TITLE):
            TITLE = regex.split(TITLE)[1] #Removes any numbering at the begining of song title.

        TITLE = TITLE.title().strip() #removes starting and ending spaces/new lines

        if video_info['title_def'] is not None:
            TITLE = video_info['title_def'][0]

        #get start and duration of songs in miliseconds
        start = data['chapters'][i]['start_time'] * 1000
        duration = (data['chapters'][i]['end_time'] * 1000) - start

        print "%d: %s - %s\n\t...currently being split." % (i+1, ARTIST, TITLE)

        video[start:][:duration].export("{}{}.{}".format(path,clean_filename(TITLE),"mp3"), 
            format="mp3", 
            tags={'artist': ARTIST, 'title': TITLE, 'album': ALBUM, 'track': i+1, 'album_artist': 'Various Artists'},
            cover=video_info['img_path']
        )
        

    print "Finished downloading and spliting %s\nStored within %s" % (data['fulltitle'], path)

#########################################################################################################

def format_compilation(video, path, data):
    sys.stdout.write('Video is an compilation album.\n\tIf this is wrong, then well fuck.\n')
    sys.stdout.flush()

    ALBUM = data['fulltitle'].strip().encode('utf-8')

    if video_info['album_def'] is not None:
        ALBUM = video_info['album_def'][0]
 
    for i in range(0, len(data['chapters'])):

        ARTIST, TITLE = split_title(data['chapters'][i]['title'])

        if video_info['artist_def'] is not None:
            ARTIST = video_info['artist_def'][0]
        if video_info['title_def'] is not None:
            TITLE = video_info['title_def'][0]

        #get start and duration of songs in miliseconds
        start = data['chapters'][i]['start_time'] * 1000
        duration = (data['chapters'][i]['end_time'] * 1000) - start

        print "%d: %s - %s\n\t...currently being split." % (i+1, ARTIST, TITLE)

        video[start:][:duration].export("{}{}.{}".format(path,clean_filename(TITLE),"mp3"), 
            format="mp3", 
            tags={'artist': ARTIST, 'title': TITLE, 'album': ALBUM, 'track': i+1, 'album_artist': 'Various Artists'},
            cover=video_info['img_path']
        )

    print "Finished downloading and spliting %s\nStored within %s" % (data['fulltitle'], path)

#########################################################################################################

def clean_files():
    #deletes json and wav file
    os.remove(video_info['video_path'])
    os.remove(video_info['json_path'])
    os.remove(video_info['img_path'])

#########################################################################################################

if __name__ == "__main__":
    
    #Arguments
    parser = argparse.ArgumentParser(
            description='Uses youtube_dl to download songs and albums and accuractly adds metadata'
    )

    parser.add_argument(
            'link', 
            action='store', 
            nargs=1,
            help='Youtube Link'
    )

    parser.add_argument('-d', dest='direc', 
            action='store', 
            nargs='?', 
            default='.',
            help="Directory to save mp3, creates folder if it doesnt exist."
    )
    
    parser.add_argument(
            '-r', dest='reverse', 
            action='store_true', 
            help="If video uses reveresed naming convention title (Song - Artist)/(Album - Artist), use -r tag to correctly create tags."
    )

    parser.add_argument(
            '-t', dest='title', 
            action='store', 
            nargs=1,
            help="song(s) title."
    )

    parser.add_argument(
            '-a', dest='artist', 
            action='store', 
            nargs=1,
            help="Artist to add to metadata of the mp3s"
    )

    parser.add_argument(
            '-A', dest='album', 
            action='store', 
            nargs=1,
            help="Album to add to metadata of the mp3s."
    )

    #parser.add_argument(
    #        '-y', dest='album_artist', 
    #        action='store', 
    #        nargs=1,
    #        help="Album artist to add to metadata of the mp3s."
    #)

    #disabld while figure if only MP3 get metadata tags
    #parser.add_argument(
    #        '-e', dest='extension', 
    #        action='store', 
    #        nargs=1,
    #        help="Format to save files as."
    #)

    #parser.add_argument(
    #        '-f', dest='folder', 
    #        action='store_true', 
    #        help="Should files be placed within own album folder. E.G path/{ALBUM}/song(s)"
    #)
    
    args = parser.parse_args()

    video = None
    video_info['URL'] = args.link
    video_info['path'] = args.direc + '/'
    video_info['reverse_title'] = args.reverse
    video_info['artist_def'] = args.artist
    video_info['album_def'] = args.album
    video_info['title_def'] = args.title
    #video_info['album_artist_def'] = args.album_artist

    ydl_opts['outtmpl'] = video_info['path'] + ydl_opts['outtmpl']

    #creates destination folder
    if (not os.path.exists(video_info['path'])):
        os.makedirs(video_info['path'])

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(video_info['URL'])

    video_info['id'] = find_video_id(args.direc)
    video_info['video_path'] = video_info['path'] + video_info['id'] + '.wav'
    video_info['json_path'] = video_info['path'] + video_info['id'] + '.info.json'
    video_info['img_path'] = video_info['path'] + video_info['id'] + '.jpg'

    #Load vudei into audiosegment
    video = AudioSegment.from_file(video_info['video_path'], 'wav')
    
    #Extract all video json data 
    with open(video_info['json_path']) as data_file:    
            data = json.load(data_file)

    if(data['chapters'] is None):
        format_single(video, video_info['path'], data) 
    elif(" - " in data['fulltitle']):
        format_album(video, video_info['path'], data)
    else:
        format_compilation(video, video_info['path'], data)

    clean_files()