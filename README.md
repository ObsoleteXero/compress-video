# Compress Video
Python script that transcodes video to target file size using ffmpeg.  
Video track is encoded using libx264 and audio with aac, with the total bitrate distributed in a 3:1 ratio.

## Installation
```
py -m pip install --upgrade https://github.com/ObsoleteXero/compress-video/tarball/package
```
## Usage
### Command Line
```
py -m smallvid filesize input [output]
```
Filesize should be a number followed by units (e.g.: `20MB`) or the ratio between the output and input file sizes (e.g.: `0.5` for half the size)  
If output is not provided, defaults to `compressed_[input].mkv`

### GUI
Any other arrangement of arguments (or no arguments) will open the GUI.

## Requirements
- Python 3.6+
- ffmpeg