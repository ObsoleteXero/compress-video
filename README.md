# Compress Video
Python script that transcodes video to target file size using ffmpeg.  
Video track is encoded using libx264 and audio with aac, with the total bitrate distributed in a 3:1 ratio.

## Usage
```
python3 main.py filename filesize
```
Filesize should be a number followed by units (eg: `20MB`)

## Requirements
- Python 3.7+
- ffmpeg