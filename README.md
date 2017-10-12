#Youtube Album splitter
Python script offering easy way to download and convert Youtube music videos into MP3's, while splitting those large videos into individual songs; with all the correct tags. 
Allowing you to instantly place it within your music library, and correctly be displayed. 

##Core Features
This script will differentiate, download and split:
    - Singles
    - Albums
    - Compilations
    - Playlists (kinda)

##Install guide
    1.Install requirements
        - pip install -r requirements.txt
    2. Run!
        - python yt_album_splitter.py <URL> -d <DESTINATION>

##Options
    - Save location
        -d <DESTINATION>
    - Reverse title
        -r
    - Forced detection
        -f <c|p|a|s>
    - Force title
        -t <TITLE>
    - Force Artist
        -a <ARTIST>
    - Force Album
        -A <ALBUM>
    - Force Album Artist
        -y <ALBUM_ARTIST>
 
##Req
(just install the requirement.txt file)
youtube-dl
pydub

##To-Do
    - Allow other formats (look into tags for other formats)
    - Store temp files in tmp dir instead of output dir (less clutter and no residue)
    - Implemented ability to download Playlists (kinda works?)
    - REALLY CLEAN THE NASTY ASS CODE UP

##Bugs
    - Album or compilation detected as single song
        This is either to the video not listed the songs within a large file or due to
        relying on youtube-dl json files to determine the contents of a video,
        which sometimes returns 'Null' for the chapters (songs) within a larger video.
        This cant be fixed by using force detection.
