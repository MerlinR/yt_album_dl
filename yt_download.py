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
import argparse
from pydub import AudioSegment
from lib.video_dl import yt_downloader
from lib.vid_control import video_data

download_settings = {
    'path': None,               #Path songs are extracted into
    'title_def': None,          #Forced Title
    'artist_def': None,         #Forced Artist
    'album_def': None,          #Forced Album
    'album_artist_def': None,   #Forced album artist (useful for complitation)
    'reverse_title': None       #Reverse the order of title, either in video or songs/artists.
}

#########################################################################################################

def store_arguments(arguments):
    if arguments.artist is not None:
        download_settings['artist_def'] = clean_title(arguments.artist[0])
    if arguments.album is not None:
        download_settings['album_def'] = clean_title(arguments.album[0])
    if arguments.title is not None:
        download_settings['title_def'] = clean_title(arguments.title[0])
    if arguments.album_artist is not None:
        download_settings['album_artist_def'] = clean_title(arguments.album_artist[0])

    download_settings['path'] = arguments.direc + '/'
    download_settings['reverse_title'] = arguments.reverse

#########################################################################################################

def forced_arguments(artist, album, title, album_artist):

    if download_settings['artist_def'] is not None:
        artist = download_settings['artist_def']
    if download_settings['album_def'] is not None:
        album = download_settings['album_def']
    if download_settings['title_def'] is not None:
        title = download_settings['title_def']
    if download_settings['album_artist_def'] is not None:
        album_artist = download_settings['album_artist_def']
    
    return artist, album, title, album_artist

#########################################################################################################

def clean_filename(filename):
    #Removes chars that could cause issues as file name.
    return re.sub(r'[\\/\.\[\]\,\?\{\}\(\)\-\"]',"",filename) 

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

def split_title(title):

    #Split video title and clean up string, encode into utf-8 for meta-data
    title = title.encode('utf-8')

    #Removes "en dash" (weird HTML based dashes) not ASCII
    title = re.sub("\xe2\x80\x93", "-", title)
    title = re.sub("\xe2\x80\x94", "-", title)

    #Removes extra brackets etc from titles
    title = clean_title(title)

    split_title = title.split('-')

    #return in order based on reverse of not.
    if(download_settings['reverse_title']):
        return split_title[1], split_title[0]
    else:
        return split_title[0], split_title[1]

#########################################################################################################

def find_video_ids(path):
    files = os.listdir(path)
    found_ids = []

    for fileN in files:
        if(".info.json" in fileN):
            found_ids.append(fileN.split('.')[0])
    
    return found_ids

#########################################################################################################

def export_song(start, duration, video, path, img_path, file_name, artist, title, album, album_artist):
    #Load video into audiosegment
    video_split = AudioSegment.from_file(video.video_path, 'webm')

    #While video splitting is always necessary we can add meta-data and convert to MP3
    video_split[start:][:duration].export("{}{}.{}".format(download_settings['path'] ,file_name, "mp3"), 
        format="mp3", 
        tags={'artist': artist, 'title': title, 'album': album, 'album_artist': album_artist},
        cover=video.img_path
    )

#########################################################################################################

def format_single(video):
    sys.stdout.write('\tVideo detected as single song.\n')
    sys.stdout.flush()

    #Splits title into artist and title.
    artist, title = split_title(video.json_contents['fulltitle'])

    #Check for forced arguments
    artist, album, title, album_artist = forced_arguments(artist, "", title, "")
    
    #sets safe name for saving file to Disk
    file_name = "{}_{}".format(artist, title)
    file_name = clean_filename(file_name)

    #Export video as MP3 with meta-data
    export_song(0, video.json_contents['duration'] * 1000, video, 
                download_settings['path'], video.img_path, file_name, 
                artist, title, album, album_artist)

    print "Finished downloading %s\nStored within %s" % (video.json_contents['fulltitle'], download_settings['path'])

#########################################################################################################

def format_album(video):
    sys.stdout.write('Video is an album of the same artist.\n\tIf this is wrong, then well fuck.\n')
    sys.stdout.flush()

    artist, album = split_title(video.json_contents['fulltitle'])

     #Check for forced arguments
    artist, album, title, album_artist = forced_arguments(artist, album, "", "")
    
    for i in range(0, len(video.json_contents['chapters'])):

        title = clean_title(video.json_contents['chapters'][i]['title'])

        #Check everything for each song is fairly redundant
        artist, album, title, album_artist = forced_arguments(artist, album, title, album_artist)

        #get start and duration of songs in milliseconds
        start = video.json_contents['chapters'][i]['start_time'] * 1000
        duration = (video.json_contents['chapters'][i]['end_time'] * 1000) - start

        print "%d: %s - %s\n\t...currently being split." % (i+1, artist, title)

        #Export video as MP3 with meta-data
        export_song(start, duration, video, 
                    download_settings['path'], video.img_path, clean_filename(title), 
                    artist, title, album, album_artist)
    print "Finished downloading and splitting %s\nStored within %s" % (video.json_contents['fulltitle'], download_settings['path'])

#########################################################################################################

def format_compilation(video):
    sys.stdout.write('Video is an compilation album.\n\tIf this is wrong, then well fuck.\n')
    sys.stdout.flush()

    album = video.json_contents['fulltitle'].strip().encode('utf-8')

    artist, album, title, album_artist = forced_arguments("", album, "", "")
 
    for i in range(0, len(video.json_contents['chapters'])):

        artist, title = split_title(video.json_contents['chapters'][i]['title'])

        artist, album, title, album_artist = forced_arguments(artist, album, title, album_artist)

        #get start and duration of songs in milliseconds
        start = video.json_contents['chapters'][i]['start_time'] * 1000
        duration = (video.json_contents['chapters'][i]['end_time'] * 1000) - start

        print "%d: %s - %s\n\t...currently being split." % (i+1, artist, title)

        export_song(start, duration, video, 
                    download_settings['path'], video.img_path, clean_filename(title), 
                    artist, title, album, album_artist)

    print "Finished downloading and splitting %s\nStored within %s" % (video.json_contents['fulltitle'], download_settings['path'])

#########################################################################################################

if __name__ == "__main__":
    
    #Arguments
    parser = argparse.ArgumentParser(
            description='Uses youtube_dl to download songs and albums and accurately adds meta-data'
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
            help="Directory to save MP3, creates folder if it doesn't exist."
    )
    
    parser.add_argument(
            '-r', dest='reverse', 
            action='store_true', 
            help="If video uses reversed naming convention title (Song - Artist)/(Album - Artist), use -r tag to correctly create tags."
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
            help="Artist to add to meta-data of the MP3"
    )

    parser.add_argument(
            '-A', dest='album', 
            action='store', 
            nargs=1,
            help="Album to add to meta-data of the MP3."
    )

    parser.add_argument(
            '-y', dest='album_artist', 
            action='store', 
            nargs=1,
            help="Album artist to add to meta-data of the MP3."
    )

    #parser.add_argument(
    #        '-f', dest='folder', 
    #        action='store_true', 
    #        help="Should files be placed within own album folder. E.G path/{album}/song(s)"
    #)

    args = parser.parse_args()          #Arguments
    dl_videos = []                      #Each video downloaded
    video = yt_downloader(args.link[0]) #YT Downloader class

    #Checks on argument
    store_arguments(args)

    #creates destination folder
    #THIS NEEDS RE-WORK LOOK INTO USING /TMP
    if (not os.path.exists(download_settings['path'])):
        os.makedirs(download_settings['path'])

    #Sets template dir for Youtube-dl settings
    video.output_dir(download_settings['path'])

    #Downloads video using settings and given URL.
    video.download_video()

    #For each video downloaded create a class(struct) to hold information.
    for video in find_video_ids(args.direc):
        dl_videos.append(video_data(video, download_settings['path']))

    #Use video download count to find play lists
    #This is kinda Janky, although mostly works, could be issues with album and compilation
    #Also passing [0] for everything else just seems off
    if(len(dl_videos) > 1):
        print "playlist"
    elif(dl_videos[0].json_contents['chapters'] is None):
        format_single(dl_videos[0]) 
    elif("-" in dl_videos[0].json_contents['fulltitle']):
        format_album(dl_videos[0])
    else:
        format_compilation(dl_videos[0])