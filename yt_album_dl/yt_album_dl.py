#!/usr/bin/python
#===============================================================================================
# Title           :yt_album_dl.py
# Description     :
__author__  = "Merlin Roe"
# Date            :19/09/2017
__version__ = "1.8"
# Usage           :python yt_album_dl.py
# Notes           :
# Python_version  :2.7.13
#===============================================================================================
# Imports
#===============================================================================================
import sys
import os
import re
import argparse
from pydub import AudioSegment
from video_dl import yt_downloader
from vid_control import video_data

#===============================================================================================
# Globals
#===============================================================================================

VIDEO_TYPES = {'p', 's', 'a', 'c'}

downloadSettings = {
    'path': None,               # Path songs are extracted into
    'video_type': None,         # Type of video downloading (single,album,compilation,playlist)
    'title_def': None,          # Forced Title
    'artist_def': None,         # Forced Artist
    'album_def': None,          # Forced Album
    'album_artist_def': None,   # Forced album artist (useful for complitation)
    'reverse_title': None,      # Reverse the order of title, either in video or songs/artists.
    'no_spaces': None           # Toggle spaces witihn the saved file name
}

# Holds MP3 Metadata tags
mp3Data = {
    'title':            "",     
    'album':            "",
    'artist':           "",
    'album_artist':     "",
    'type':             "", # Not tag but used to clarify.
}

#===============================================================================================

def error_catch(errorMessage, error=None):
    sys.stdout.write('ERROR: %s\n' % errorMessage)

    if error is not None:
        sys.stdout.write('\t%s\n' % error)

    sys.stdout.flush()
    exit()

#===============================================================================================

def updateArguments(args):
    if args.artist is not None:
        downloadSettings['artist_def'] = args.artist[0]
    if args.album is not None:
        downloadSettings['album_def'] = args.album[0]
    if args.title is not None:
        downloadSettings['title_def'] = args.title[0]
    if args.album_artist is not None:
        downloadSettings['album_artist_def'] = args.album_artist[0]
    if args.video_type is not None:
        downloadSettings['video_type'] = args.video_type[0]

    downloadSettings['path'] = args.direc[0] + '/'
    downloadSettings['link'] = args.link[0]
    downloadSettings['reverse_title'] = args.reverse
    downloadSettings['no_spaces'] = args.no_spaces

#===============================================================================================

def argumentOverrides(mp3Data):

    if downloadSettings['artist_def'] is not None:
        mp3Data['artist'] = downloadSettings['artist_def']
    if downloadSettings['album_def'] is not None:
        mp3Data['album'] = downloadSettings['album_def']
    if downloadSettings['title_def'] is not None:
        mp3Data['title'] = downloadSettings['title_def']
    if downloadSettings['album_artist_def'] is not None:
        mp3Data['album_artist'] = downloadSettings['album_artist_def']
    
    return mp3Data

#===============================================================================================

# Using in place of ".title()" in order to not lowercase intentional names or symbols
#   E.G With .title()
#       ("JJ Doom", "TW@T", "Master's Dog") -> ("Jj Doom", "Tw@T", "Master'S Dog")
def capitaliseTitle(string):
    newString=""

    for i, letter in enumerate(string):
        if i == 0:
            newString+=letter.upper()
        elif string[i-1] == ' ':
            newString+=letter.upper()
        else:
            newString+=letter

    return newString

#===============================================================================================

def cleanFilename(filename):
    # Removes all brackets and its contents and any whitespace surrounding it
    filename = re.sub(r'\s*[\<\(\[\{].*[\}\]\)\>]\s*',"",filename)

    # Removes chars that could cause issues as file name.
    filename = re.sub(r'[^a-zA-Z0-9\-\_\ ]',"",filename)

    #Remove duplicate spaces from removing symbols
    filename = re.sub(" +"," ",filename).strip()

    if (downloadSettings['no_spaces']):
        return re.sub(" ","_",filename).strip()
    else:
        return filename

#===============================================================================================

def cleanMp3DataTitles(mp3Data):
    # Removes all brackets and its contents and any whitespace surrounding it
    regexRemoveBracketsStart=re.compile("\s*[\<\(\[\{].*[\}\]\)\>]\s*")

    # Removes all brackets and its contents and everything after
    regexRemoveBracketsEnd=re.compile("\s*[\<\(\[\{].*[\}\]\)\>].*")

    # Removes any junk symbols at the start which are not part of the name
    regexRemoveTimeStampClutter=re.compile("^\d*[^\w]*\s*")

    # Remove junk globlaly (any type)
    regexRemoveJunk=re.compile("\"")

    if 'artist' in mp3Data:
        # Remove set of brackets and contents
        mp3Data['artist'] = re.sub(regexRemoveBracketsStart, "", mp3Data['artist'])

        # Remove junk
        mp3Data['artist'] = re.sub(regexRemoveJunk, "", mp3Data['artist'])

        # remove any numbering used from Timestamp E.G (00:00 :~ Artist -> Artist)
        mp3Data['artist'] = re.sub(regexRemoveTimeStampClutter, "", mp3Data['artist'])
        mp3Data['artist'].strip()

    if 'album' in mp3Data:
        # Remove set of brackets and contents
        mp3Data['album'] = re.sub(regexRemoveBracketsEnd, "", mp3Data['album'])

        # Remove junk
        mp3Data['album'] = re.sub(regexRemoveJunk, "", mp3Data['album'])

        mp3Data['album'].strip()

    if 'title' in mp3Data and ('type' in mp3Data and mp3Data['type'] == 'single'):
        # Remove set of brackets and contents E.G ("Title (Audio)" -> "Title")
        mp3Data['title'] = re.sub(regexRemoveBracketsEnd, "", mp3Data['title'])

        # Remove junk
        mp3Data['title'] = re.sub(regexRemoveJunk, "", mp3Data['title'])
        
        mp3Data['title'].strip()

    elif 'title' in mp3Data and ('type' not in mp3Data or mp3Data['type'] != 'single'):
        # remove any numbering used from Timestamp E.G ("00:00 :~ Artist" -> "Artist")
        mp3Data['title'] = re.sub(regexRemoveTimeStampClutter, "", mp3Data['title'])

        # Remove junk
        mp3Data['title'] = re.sub(regexRemoveJunk, "", mp3Data['title'])

        #Doesnt attempt to remove Brackets when song is listed in description
        mp3Data['title'].strip()

    return mp3Data

#===============================================================================================

def splitTitleByDelimiter(title):
    # Removes "en dash" (weird HTML based dashes) not ASCII into dash
    #title = title.encode("utf-8")
    title = re.sub("\xe2\x80\x93", "-", title)
    title = re.sub("\xe2\x80\x94", "-", title)

    title = capitaliseTitle(title)

    # Removes extra brackets etc from titles
    # or returns False to indicate it cannot be split
    if "-" in title:
        splitTitle = title.split('-')
    elif "~" in title:
        splitTitle = title.split('~')
    else:
        return False

    splitTitle[0] = splitTitle[0].strip()
    splitTitle[1] = splitTitle[1].strip()

    # return in order based on reverse or not.
    if(downloadSettings['reverse_title']):
        return splitTitle[1], splitTitle[0]
    else:
        return splitTitle[0], splitTitle[1]

#===============================================================================================

def searchForVideosByID(path):
    files = os.listdir(path)
    found_ids = []

    for fileN in files:
        if(".info.json" in fileN):
            found_ids.append(fileN.split('.')[0])
    
    return found_ids

#===============================================================================================

# Fucking really man? How drunk was i?
# Kinda better now
def exportSong(video, songStartTime, songDuration, trackNumber, fileName, mp3Data):
    # Load video into audiosegment
    exportVideo = AudioSegment.from_file(video.video_path, 'mp3')

    # While video splitting is always necessary we can add meta-data and convert to MP3
    exportVideo[songStartTime:][:songDuration].export("{}{}.{}".format(downloadSettings['path'] ,fileName, "mp3"), 
        format="mp3", 
        tags={'artist': mp3Data['artist'], 'title': mp3Data['title'], 'album': mp3Data['album'], 
              'track': trackNumber, 'album_artist': mp3Data['album_artist'] },
        cover=video.img_path
    )

#===============================================================================================

def format_single(video):
    sys.stdout.write('\tVideo being processed as a Single.\n')
    sys.stdout.flush()

    # Using mp3Data Global (As C struct)
    global mp3Data

    mp3Data['type'] = 'single'

    # Splits title into artist and title.
    # Needs improvement, Really dislike using Catch for this.
    try:
        mp3Data['artist'], mp3Data['title'] = splitTitleByDelimiter(video.jsonVideoData['fulltitle'])
    except Exception as e:
        error_catch("Could not split video title")

    # Clean up Title, Artist and album.
    mp3Data = cleanMp3DataTitles(mp3Data)

    # Check for overriding arguments
    mp3Data = argumentOverrides(mp3Data)
    
    # sets safe name for saving file to Disk
    file_name = cleanFilename("{}-{}".format(mp3Data['artist'], mp3Data['title']))

    # Export video as MP3 with meta-data
    exportSong(video, 0, video.jsonVideoData['duration'] * 1000, 0, file_name, mp3Data)

    print "Finished downloading and formating %s\nStored within %s" % (video.jsonVideoData['fulltitle'], downloadSettings['path'])

#===============================================================================================

def format_album(video):
    sys.stdout.write('Video is an album of the same artist.\n\tIf this is wrong, then well fuck.\n')
    sys.stdout.flush()

    global mp3Data

    try:
        mp3Data['artist'], mp3Data['album'] = splitTitleByDelimiter(video.jsonVideoData['fulltitle'])
    except Exception as e:
        error_catch("Could not split video title")

    # Check for overriding arguments
    mp3Data = argumentOverrides(mp3Data)
    
    for i in range(0, len(video.jsonVideoData['chapters'])):

        # Find title for specific song
        mp3Data['title'] = video.jsonVideoData['chapters'][i]['title']

        # Clean up Title, Artist and album.
        mp3Data = cleanMp3DataTitles(mp3Data)

        # Calculate start and duration of songs in milliseconds
        songStartingTime = video.jsonVideoData['chapters'][i]['start_time'] * 1000
        songDuration = (video.jsonVideoData['chapters'][i]['end_time'] * 1000) - songStartingTime

        print "%d: %s - %s\n\t...currently being split." % (i+1, mp3Data['artist'], mp3Data['title'])

        # Export video as MP3 with meta-data
        exportSong(video, songStartingTime, songDuration, i+1, cleanFilename(mp3Data['title']), mp3Data)


    print "Finished downloading and splitting \"%s\"\nStored within %s" % (video.jsonVideoData['fulltitle'], downloadSettings['path'])

#===============================================================================================

def format_compilation(video):
    sys.stdout.write('Video is an compilation album.\n\tIf this is wrong, then well fuck.\n')
    sys.stdout.flush()

    global mp3Data

    mp3Data['album'] = video.jsonVideoData['fulltitle']
    mp3Data['album_artist'] = "Various Artists"
 
    for i in range(0, len(video.jsonVideoData['chapters'])):

        try:
            mp3Data['artist'], mp3Data['title']  = splitTitleByDelimiter(video.jsonVideoData['chapters'][i]['title'])
        except Exception as e:
            error_catch("Could not split video title")

        mp3Data = argumentOverrides(mp3Data)

        # Clean up Title, Artist and album.
        mp3Data = cleanMp3DataTitles(mp3Data)

        # get start and duration of songs in milliseconds
        songStartingTime = video.jsonVideoData['chapters'][i]['start_time'] * 1000
        songDuration = (video.jsonVideoData['chapters'][i]['end_time'] * 1000) - songStartingTime

        print "%d: %s - %s\n\t...currently being split." % (i+1, mp3Data['artist'], mp3Data['title'])

        # sets safe name for saving file to Disk
        fileName = cleanFilename("{}_{}".format(mp3Data['artist'], mp3Data['title']))

        # Export video as MP3 with meta-data
        exportSong(video, songStartingTime, songDuration, i+1, fileName, mp3Data)

    print "Finished downloading and splitting \"%s\"\nStored within %s" % (video.jsonVideoData['fulltitle'], downloadSettings['path'])

#===============================================================================================

def format_playlist(video_list):
    sys.stdout.write('\tDetected plyalist, formating videos\n')
    sys.stdout.flush()

    # Using mp3Data Global (As C struct)
    global mp3Data

    #Name of playlist can be used to find artist and album, but cant distinguish between compilations and albums.
    try:
        mp3Data['artist'], mp3Data['album'] = splitTitleByDelimiter(video_list[0].jsonVideoData['playlist'])
    except Exception as e:
        mp3Data['album'] = video_list[0].jsonVideoData['playlist']

    for i in range(0, len(video_list)):
        # Splits title into artist and title.
        try:
            mp3Data['artist'], mp3Data['title'] = splitTitleByDelimiter(video_list[i].jsonVideoData['fulltitle'])
        except Exception as e:
            mp3Data['title'] = video_list[i].jsonVideoData['fulltitle']

        # Check for overriding arguments
        mp3Data = argumentOverrides(mp3Data)
        
        # sets safe name for saving file to Disk
        file_name = "{}-{}".format(mp3Data['artist'], mp3Data['title'])

        file_name = cleanFilename(file_name)

        print "%d: %s - %s\n\t...currently being formatted." % (i+1, mp3Data['artist'], mp3Data['title'])

        # Export video as MP3 with meta-data
        exportSong(video_list[i], 0, video_list[i].jsonVideoData['duration'] * 1000, i+1, file_name, mp3Data)

    print ("Finished downloading and formating \"%s\"\nStored within %s" 
            % (video_list[i].jsonVideoData['fulltitle'], downloadSettings['path']))


#===============================================================================================
# Main
#===============================================================================================
if __name__ == "__main__":
    
    # Arguments
    parser = argparse.ArgumentParser(
            description='Using youtube_dl to download songs and albums and accurately add meta-data'
    )

    parser.add_argument(
            'link',
            nargs=1,
            help='Youtube Link'
    )

    parser.add_argument(
            '-d', dest='direc', 
            nargs=1, 
            default='.',
            help="Directory to save MP3, creates folder if it doesn't exist."
    )
    
    parser.add_argument(
            '-r', dest='reverse', 
            action='store_true', 
            help="If video uses reversed naming convention title (Song - Artist)/(Album - Artist), use -r tag to correctly create tags."
    )

    parser.add_argument(
            '-p', dest='no_spaces', 
            action='store_true', 
            help="User underscores instead of spaces for Filename."
    )

    parser.add_argument(
            '-f', dest='video_type', 
            nargs=1,
            choices=VIDEO_TYPES,
            help="Force video type: (s)ingle, (a)lbum, (c)ompilation, (p)laylist"
    )

    parser.add_argument(
            '-t', dest='title', 
            nargs=1,
            help="song(s) title."
    )

    parser.add_argument(
            '-a', dest='artist', 
            nargs=1,
            help="Artist to add to meta-data of the MP3"
    )

    parser.add_argument(
            '-A', dest='album', 
            nargs=1,
            help="Album to add to meta-data of the MP3."
    )

    parser.add_argument(
            '-y', dest='album_artist', 
            nargs=1,
            help="Album artist to add to meta-data of the MP3."
    )

    # Arguments
    args = parser.parse_args()
    updateArguments(args)

    # YT Downloader class
    video = yt_downloader(downloadSettings['link'])

    # creates destination folder
    # THIS NEEDS RE-WORK LOOK INTO USING /TMP
    if (not os.path.exists(downloadSettings['path'])):
        os.makedirs(downloadSettings['path'])

    # Sets Download dir for Youtube-dl settings
    video.setDownloadPath(downloadSettings['path'])

    # Downloads video using settings and given URL.
    video.downloadVideo()

    # List of downloaded videos
    dl_videos = []

    # For each video downloaded create a class(struct) to hold information.
    for videoID in searchForVideosByID(downloadSettings['path']):
        dl_videos.append(video_data(videoID, downloadSettings['path']))
    
    # This is so Damn nasty.
    # This shit still here, Fuck man
    if (not downloadSettings['video_type']):
        if( len(dl_videos) > 1 or downloadSettings['video_type'] == 'p'):
            # If multiple videos downloaded its a playlist
            print "PLAYLISTS ARE WORK IN PROGRESS, PLEASE FORCE ALBUM AND ARTIST IF DOESNT WORK CORRECTLY"
            format_playlist(dl_videos)

        elif( dl_videos[0].jsonVideoData['chapters'] is None or downloadSettings['video_type'] == 's'):
            # If no chapters in single video, its a single
            format_single(dl_videos[0])

        elif( splitTitleByDelimiter(dl_videos[0].jsonVideoData['fulltitle']) or downloadSettings['video_type'] == 'a'):
            # A little junky, if video title uses dash such as <artist - title>
            format_album(dl_videos[0])

        elif( splitTitleByDelimiter(dl_videos[0].jsonVideoData['fulltitle']) is False or downloadSettings['video_type'] == 'c'):
            format_compilation(dl_videos[0])

        else:
            error_catch("could not detect video type")
        
    else:
        if (downloadSettings['video_type'] == 'p'):
            # If multiple videos downloaded its a playlist
            print "PLAYLISTS ARE WORK IN PROGRESS, PLEASE FORCE ALBUM AND ARTIST IF DOESNT WORK CORRECTLY"
            format_playlist(dl_videos)

        elif (downloadSettings['video_type'] == 's'):
            format_single(dl_videos[0])

        elif (downloadSettings['video_type'] == 'a'):
            format_album(dl_videos[0])

        elif (downloadSettings['video_type'] == 'c'):
            format_compilation(dl_videos[0])

        else:
            error_catch("could not detect video type")