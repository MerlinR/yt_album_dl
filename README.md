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
    - Save location
        -d <DESTINATION>
    - Reverse title
        -r
    - No spaces in filename
        -p
    - Force detection
        -f <c|p|a|s>
    - Force title
        -t <TITLE>
    - Force Artist
        -a <ARTIST>
    - Force Album
        -A <ALBUM>
    - Force Album Artist
        -y <ALBUM_ARTIST>

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

## Bugs
    - Album or compilation detected as single song
        This is either to the video not listed the songs within a large file or due to
        relying on youtube-dl json files to determine the contents of a video,
        which sometimes returns 'Null' for the chapters (songs) within a larger video.
        This cant be fixed by using force detection.
