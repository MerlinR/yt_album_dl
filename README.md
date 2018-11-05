# Youtube Album splitter
Python script offering easy way to download and convert Youtube music videos into MP3's, while splitting those large videos into individual songs; with all the correct tags. 
Allowing you to instantly place it within your music library, and correctly be displayed. 

## Core Features
This script will differentiate, download and split:
    - Singles
    - Albums
    - Compilations
    - Playlists (kinda)

## Install guide
    1.Install requirements
        - Install ffmpeg
        - pip install -r requirements.txt
    2. Run!
        - python yt_album_dl.py <URL> -d <DESTINATION>

## Options
    -d <DESTINATION>
        - Save location
    -r
        - Reverse title
    -p
        - No spaces in filename
    -f <c|p|a|s>
        - Force detection
    -t <TITLE>
        - Force title
    -a <ARTIST>
        - Force Artist
    -A <ALBUM>
        - Force Album
    -y <ALBUM_ARTIST>
        - Force Album Artist

## Req
ffmpeg

(just install the requirement.txt file)
youtube-dl
pydub

## Tests

Im an idiot so tests need to be ran from the main dir.

## To-Do
    - Allow other formats (look into tags for other formats)
    - Store temp files in tmp dir instead of output dir (less clutter and no residue)
    - Playlists expect songs to be singles.
    - Better detection for video type. Its fucking abysmal, Bloody bellend
    - If no Delimiter check for forced values
    - Check DB to auto select artist

## Bugs
    - Album or compilation detected as single songThis is either to the video not listed the songs within a large file or due to relying on youtube-dl json files to determine the contents of a video, which sometimes returns 'Null' for the chapters (songs) within a larger video. This cant be fixed by using force detection.
