#!/usr/bin/python
#==============================================================================
#Title           :yt_download.py
#Description     :
__author__  = "Merlin Roe"
#Date            :19/09/2017
__version__ = "1.7"
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

ydl_opts = {
    'writethumbnail': 'true',           #Saves stillshot of youtube video as JPG
    'writeinfojson': 'true',            #Stores JSON file of video info, including segments of video.
    'format': 'bestaudio/best',         #Format
    'outtmpl': '%(id)s.%(ext)s',        #Output save format
 #   'postprocessors': [{                
 #       'key': 'FFmpegExtractAudio',
 #       'preferredcodec': 'wav',
 #       'preferredquality': '0',
 #   }],
    'logger': ydl_logger(),
    'progress_hooks': [yt_d_hook],
}

video_info = {
        'URL': None,                #Youtube URL
        'id': None,                 #Video ID (from YT)
        'path': None,               #Path songs are extracted into
        'video_path': None,         #Entire path of video
        'json_path': None,          #Entire path of JSON file
        'img_path': None,           #Entire path of Album art
        'title_def': None,          #Forced Title
        'artist_def': None,         #Forced Artist
        'album_def': None,          #Forced Album
        'album_artist_def': None,   #Forced album artist (useful for complitation)
        'reverse_title': None       #Reverse the order of title, either in video or songs/artists.
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

def clean_title(title):

    #Remove set of brackets and everything within them
    regex = re.compile(r"[\(\[\{].+[\]\)\}]") 
    if regex.search(title):
        title = regex.sub("", title)

    #remove any initial numbering at the start (this and above can be combined)
    regex = re.compile(r"^\d+[\.\)\s]") 
    if regex.search(title):
        title = regex.split(title)[1]

    #return with no trailing white spaces
    return title.strip().title()

#########################################################################################################

def forced_arguments(artist, album, title, album_artist):

    if video_info['artist_def'] is not None:
        artist = video_info['artist_def']
    if video_info['album_def'] is not None:
        album = video_info['album_def']
    if video_info['title_def'] is not None:
        title = video_info['title_def']
    if video_info['album_artist_def'] is not None:
        album_artist = video_info['album_artist_def']
    
    return artist, album, title, album_artist

#########################################################################################################


def split_title(title):

    #Split video title and clean up string, encode into utf-8 for metadata
    title = title.encode('utf-8')

    title = re.sub("\xe2\x80\x93", "-", title) #Fixes issues with "en dash"
    title = re.sub("\xe2\x80\x94", "-", title) #Fixes issues with "en dash"
    split_title = title.split('-')

    #Removes extra brackets etc from titles
    split_title[0] = clean_title(split_title[0])
    split_title[1] = clean_title(split_title[1])

    #return in order based on reverse of not.
    if(video_info['reverse_title']):
        return split_title[1], split_title[0]
    else:
        return split_title[0], split_title[1]

#########################################################################################################

def format_single(video, path, data):
    sys.stdout.write('\tVideo detected as single song.\n')
    sys.stdout.flush()

    artist, title = split_title(data['fulltitle'])
    artist, album, title, album_artist = forced_arguments(artist, "", title, "")
    
    file_name = "{}_{}".format(artist, title)
    file_name = clean_filename(file_name)

    video.export("{}{}.{}".format(path,file_name,"mp3"), 
        format="mp3", 
        tags={'artist': artist, 'title': title, 'album': album, 'album_artist': album_artist},
        cover=video_info['img_path']
    )

#########################################################################################################

def format_album(video, path, data):
    sys.stdout.write('Video is an album of the same artist.\n\tIf this is wrong, then well fuck.\n')
    sys.stdout.flush()

    artist, album = split_title(data['fulltitle'])

    artist, album, title, album_artist = forced_arguments(artist, album, "", "")
    
    for i in range(0, len(data['chapters'])):

        title = clean_title(data['chapters'][i]['title'])

        #Check everything for each song is fairly redundant
        artist, album, title, album_artist = forced_arguments(artist, album, title, album_artist)

        #get start and duration of songs in miliseconds
        start = data['chapters'][i]['start_time'] * 1000
        duration = (data['chapters'][i]['end_time'] * 1000) - start

        print "%d: %s - %s\n\t...currently being split." % (i+1, artist, title)

        video[start:][:duration].export("{}{}.{}".format(path,clean_filename(title),"mp3"), 
            format="mp3", 
            tags={'artist': artist, 'title': title, 'album': album, 'track': i+1, 'album_artist': album_artist},
            cover=video_info['img_path']
        )
        

    print "Finished downloading and spliting %s\nStored within %s" % (data['fulltitle'], path)

#########################################################################################################

def format_compilation(video, path, data):
    sys.stdout.write('Video is an compilation album.\n\tIf this is wrong, then well fuck.\n')
    sys.stdout.flush()

    album = data['fulltitle'].strip().encode('utf-8')

    artist, album, title, album_artist = forced_arguments("", album, "", "")
 
    for i in range(0, len(data['chapters'])):

        artist, title = split_title(data['chapters'][i]['title'])

        artist, album, title, album_artist = forced_arguments(artist, album, title, album_artist)

        #get start and duration of songs in miliseconds
        start = data['chapters'][i]['start_time'] * 1000
        duration = (data['chapters'][i]['end_time'] * 1000) - start

        print "%d: %s - %s\n\t...currently being split." % (i+1, artist, title)

        video[start:][:duration].export("{}{}.{}".format(path,clean_filename(title),"mp3"), 
            format="mp3", 
            tags={'artist': artist, 'title': title, 'album': album, 'track': i+1, 'album_artist': album_artist},
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

    parser.add_argument(
            '-y', dest='album_artist', 
            action='store', 
            nargs=1,
            help="Album artist to add to metadata of the mp3s."
    )

    #parser.add_argument(
    #        '-f', dest='folder', 
    #        action='store_true', 
    #        help="Should files be placed within own album folder. E.G path/{album}/song(s)"
    #)
    
    args = parser.parse_args()

    video = None
    video_info['URL'] = args.link
    video_info['path'] = args.direc + '/'
    video_info['reverse_title'] = args.reverse

    if args.artist is not None:
        video_info['artist_def'] = clean_title(args.artist[0])
    if args.album is not None:
        video_info['album_def'] = clean_title(args.album[0])
    if args.title is not None:
        video_info['title_def'] = clean_title(args.title[0])
    if args.album_artist is not None:
        video_info['album_artist_def'] = clean_title(args.album_artist[0])

    #creates destination folder
    if (not os.path.exists(video_info['path'])):
        os.makedirs(video_info['path'])


    #Sets template for Youtube-dl settings
    ydl_opts['outtmpl'] = video_info['path'] + ydl_opts['outtmpl']

    #Downloads video using settings and given URL.
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(video_info['URL'])


    video_info['id'] = find_video_id(args.direc)
    video_info['video_path'] = video_info['path'] + video_info['id'] + '.webm'
    video_info['json_path'] = video_info['path'] + video_info['id'] + '.info.json'
    video_info['img_path'] = video_info['path'] + video_info['id'] + '.jpg'

    #Load video into audiosegment
    video = AudioSegment.from_file(video_info['video_path'], 'webm')
    
    #Extract all video json data 
    with open(video_info['json_path']) as data_file:    
            data = json.load(data_file)

    #Use chapters to figure out if Single, Album or compilation.
    if(data['chapters'] is None):
        format_single(video, video_info['path'], data) 
    elif("-" in data['fulltitle']):
        format_album(video, video_info['path'], data)
    else:
        format_compilation(video, video_info['path'], data)

    clean_files()