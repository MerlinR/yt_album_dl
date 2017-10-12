#!/usr/bin/python
#==============================================================================
# Title           :yt_album_splitter.py
# Description     :
__author__  = "Merlin Roe"
# Date            :19/09/2017
__version__ = "1.7"
# Usage           :python yt_album_splitter.py
# Notes           :
# Python_version  :2.7.13
#==============================================================================

import sys
import os
import re
import argparse
from pydub import AudioSegment
from lib.video_dl import yt_downloader
from lib.vid_control import video_data

VIDEO_TYPES = {'p', 's', 'a', 'c'}

download_settings = {
    'path': None,               # Path songs are extracted into
    'video_type': None,         # Type of video downloading (single,album,compilation,playlist)
    'title_def': None,          # Forced Title
    'artist_def': None,         # Forced Artist
    'album_def': None,          # Forced Album
    'album_artist_def': None,   # Forced album artist (useful for complitation)
    'reverse_title': None       # Reverse the order of title, either in video or songs/artists.
}

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def store_arguments(arguments):
    if arguments.artist is not None:
        download_settings['artist_def'] = clean_title(arguments.artist[0])
    if arguments.album is not None:
        download_settings['album_def'] = clean_title(arguments.album[0])
    if arguments.title is not None:
        download_settings['title_def'] = clean_title(arguments.title[0])
    if arguments.album_artist is not None:
        download_settings['album_artist_def'] = clean_title(arguments.album_artist[0])
    if arguments.videe_type is not None:
        download_settings['video_type'] = arguments.videe_type[0]

    download_settings['path'] = arguments.direc + '/'
    download_settings['reverse_title'] = arguments.reverse

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

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

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def clean_filename(filename):
    # Removes chars that could cause issues as file name.
    return re.sub(r'[^a-zA-Z0-9\-\_\ ]',"",filename) 

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def clean_title(title):

    # Remove set of brackets and everything within them
    title = re.sub(r'[\(\[\{].+[\]\)\}]', "", title)

    # Removes left over brackets, and possible symbols not needed within a file.
    title = title.rstrip(':"&-_[]{}()')

    # remove any initial numbering at the start (this and above can be combined)
    regex = re.compile(r"^\d+[\.\)\s]") 
    if regex.search(title):
        title = regex.split(title)[1]

    # return with no trailing white spaces
    return title.strip().title()

def clean_song(song):
    song = re.sub(r'[\:\-\|\+\=\,\.\']\s', "", song)

    # remove any initial numbering at the start (this and above can be combined)
    regex = re.compile(r"^\d+[\.\)\s]") 
    if regex.search(song):
        song = regex.split(song)[1]

    # return with no trailing white spaces
    return song.strip().title()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def split_title(title):

    # Split video title and clean up string, encode into utf-8 for meta-data
    title = title.encode('utf-8')

    # Removes "en dash" (weird HTML based dashes) not ASCII
    title = re.sub("\xe2\x80\x93", "-", title)
    title = re.sub("\xe2\x80\x94", "-", title)

    # Removes extra brackets etc from titles
    split_title = title.split('-')

    split_title[0] = clean_title(split_title[0])
    split_title[1] = clean_title(split_title[1])

    # return in order based on reverse of not.
    if(download_settings['reverse_title']):
        return split_title[1], split_title[0]
    else:
        return split_title[0], split_title[1]

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def find_video_ids(path):
    files = os.listdir(path)
    found_ids = []

    for fileN in files:
        if(".info.json" in fileN):
            found_ids.append(fileN.split('.')[0])
    
    return found_ids

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Fucking really man? How drunk was i?
def export_song(video, start, duration, path, img_path, track_num, file_name, artist, title, album, album_artist):
    # Load video into audiosegment
    video_split = AudioSegment.from_file(video.video_path, 'wav')

    # While video splitting is always necessary we can add meta-data and convert to MP3
    video_split[start:][:duration].export("{}{}.{}".format(download_settings['path'] ,file_name, "mp3"), 
        format="mp3", 
        tags={'artist': artist, 'title': title, 'album': album, 'track': track_num, 'album_artist': album_artist},
        cover=video.img_path
    )

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def format_playlist(video_list):
    sys.stdout.write('\tDetected plyalist, formating videos\n')
    sys.stdout.flush()

    # artist, album = split_title(video_list[i].json_contents['playlist_title'])

    for i in range(0, len(video_list)):
        # Splits title into artist and title.
        artist, title = split_title(video_list[i].json_contents['fulltitle'])

        # Check for forced arguments
        artist, album, title, album_artist = forced_arguments(artist, "", title, "")
        
        # sets safe name for saving file to Disk
        if(download_settings['artist_def'] is not None):
            file_name = title
        else:
            file_name = "{}_{}".format(artist, title)

        file_name = clean_filename(file_name)

        print "%d: %s - %s\n\t...currently being formatted." % (i+1, artist, title)

        # Export video as MP3 with meta-data
        export_song(video_list[i], 0, video_list[i].json_contents['duration'] * 1000, 
                    download_settings['path'], video_list[i].img_path, i+1,
                    file_name, artist, title, album, album_artist)

    print ("Finished downloading and formating %s\nStored within %s" 
            % (video_list[i].json_contents['fulltitle'], download_settings['path']))

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def format_single(video):
    sys.stdout.write('\tVideo detected as single song.\n')
    sys.stdout.flush()

    # Splits title into artist and title.
    artist, title = split_title(video.json_contents['fulltitle'])

    # Check for forced arguments
    artist, album, title, album_artist = forced_arguments(artist, "", title, "")
    
    # sets safe name for saving file to Disk
    file_name = "{}_{}".format(artist, title)
    file_name = clean_filename(file_name)

    # Export video as MP3 with meta-data
    export_song(video, 0, video.json_contents['duration'] * 1000, 
                download_settings['path'], video.img_path, 0,
                file_name, artist, title, album, album_artist)

    print "Finished downloading and formating %s\nStored within %s" % (video.json_contents['fulltitle'], download_settings['path'])

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def format_album(video):
    sys.stdout.write('Video is an album of the same artist.\n\tIf this is wrong, then well fuck.\n')
    sys.stdout.flush()

    artist, album = split_title(video.json_contents['fulltitle'])

     # Check for forced arguments
    artist, album, title, album_artist = forced_arguments(artist, album, "", "")
    
    for i in range(0, len(video.json_contents['chapters'])):

        title = clean_song(video.json_contents['chapters'][i]['title'])

        # Check everything for each song is fairly redundant
        artist, album, title, album_artist = forced_arguments(artist, album, title, album_artist)

        # get start and duration of songs in milliseconds
        start = video.json_contents['chapters'][i]['start_time'] * 1000
        duration = (video.json_contents['chapters'][i]['end_time'] * 1000) - start

        print "%d: %s - %s\n\t...currently being split." % (i+1, artist, title)

        # Export video as MP3 with meta-data
        export_song(video, start, duration, download_settings['path'],
                    video.img_path, i+1, clean_filename(title), 
                    artist, title, album, album_artist)
    print "Finished downloading and splitting %s\nStored within %s" % (video.json_contents['fulltitle'], download_settings['path'])

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def format_compilation(video):
    sys.stdout.write('Video is an compilation album.\n\tIf this is wrong, then well fuck.\n')
    sys.stdout.flush()

    album_artist = ""
    album = video.json_contents['fulltitle'].encode('utf-8')
    album = clean_title(album)
 
    for i in range(0, len(video.json_contents['chapters'])):

        artist, title = split_title(video.json_contents['chapters'][i]['title'])

        artist, album, title, album_artist = forced_arguments(artist, album, title, album_artist)

        # get start and duration of songs in milliseconds
        start = video.json_contents['chapters'][i]['start_time'] * 1000
        duration = (video.json_contents['chapters'][i]['end_time'] * 1000) - start

        print "%d: %s - %s\n\t...currently being split." % (i+1, artist, title)

        # sets safe name for saving file to Disk
        file_name = "{}_{}".format(artist, title)
        file_name = clean_filename(file_name)

        export_song(video, start, duration, download_settings['path'],
                    video.img_path, i+1, file_name, 
                    artist, title, album, album_artist)

    print "Finished downloading and splitting %s\nStored within %s" % (video.json_contents['fulltitle'], download_settings['path'])

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == "__main__":
    
    # Arguments
    parser = argparse.ArgumentParser(
            description='Using youtube_dl to download songs and albums and accurately add meta-data'
    )

    parser.add_argument(
            'link', 
            action='store', 
            nargs=1,
            help='Youtube Link'
    )

    parser.add_argument(
            '-d', dest='direc', 
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
            '-f', dest='videe_type', 
            action='store', 
            nargs=1,
            choices=VIDEO_TYPES,
            help="Force video type: (s)ingle, (a)lbum, (c)ompilation, (p)laylist"
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

    args = parser.parse_args()          # Arguments
    dl_videos = []                      # Each video downloaded
    video = yt_downloader(args.link[0]) # YT Downloader class

    # Checks on argument
    store_arguments(args)

    # creates destination folder
    # THIS NEEDS RE-WORK LOOK INTO USING /TMP
    if (not os.path.exists(download_settings['path'])):
        os.makedirs(download_settings['path'])

    # Sets template dir for Youtube-dl settings
    video.output_dir(download_settings['path'])

    # Downloads video using settings and given URL.
    video.download_video()

    # For each video downloaded create a class(struct) to hold information.
    for video in find_video_ids(args.direc):
        dl_videos.append(video_data(video, download_settings['path']))
    
    # This is so Damn nasty.
    if( len(dl_videos) > 1 or download_settings['video_type'] == 'p'):
        # If mutiple videos downloaded its a playlist
        print "PLAYLISTS ARE WORK IN PROGRESS, PLEASE FORCE ALBUM AND ARTIST"
        format_playlist(dl_videos)

    elif( dl_videos[0].json_contents['chapters'] is None or download_settings['video_type'] == 's'):
        # If no chapters in single video, its a single
        format_single(dl_videos[0])

    elif( "-" in clean_title(dl_videos[0].json_contents['fulltitle']) or download_settings['video_type'] == 'a'):
        # A little junky, if video title uses dash such as <artist - title>
        format_album(dl_videos[0])

    elif( "-" not in clean_title(dl_videos[0].json_contents['fulltitle']) or download_settings['video_type'] == 'c'):
        format_compilation(dl_videos[0])

    else:
        print "could not detect video type"
        
