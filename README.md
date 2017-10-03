#Youtube Downloader and Album splitter
Python script that downloads youtube videos and splits albums based on description.
Editing the metadata to use artist name and song title
uses youtube-dl

##Req
youtube-dl
pydub

##Core Features
Script that heavy relies on youtube-dl to automaticly download youtube albums and split the album into indivual songs with correct metadata
works for Albums, compilation and singles

##Options
    - Save location
        -d <PATH>
    - Reverse title
        -r
    - Force title
        -t <TITLE>
    - Force Artist
        -a <ARTIST>
    - Force Album
        -A <ALBUM>
    - Force Album Artist
        -y <ALBUM_ARTIST>
 

##To-Do
    - Fix folder tag, automaticly create folder with album name for MP3s
    - Allow other formats (look into tags for other formats)
    - Store temp files in tmp dir instead of output dir
    - Implemented ability to download Playlists

##Extras
