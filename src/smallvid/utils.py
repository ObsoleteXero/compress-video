import os
import re
import sys
from pathlib import Path

devnull = os.devnull
temp = (
    os.path.expandvars("%TEMP%/ffmpeg2pass")
    if sys.platform == "win32"
    else "/tmp/ffmpeg2pass"
)


def clean_logs():
    """Clean up log files used by first pass"""
    for file in Path(temp).parent.glob("ffmpeg2pass-*.log*"):
        os.remove(file)


def parse_filesize(filesize: str):
    """Convert target filesize to kibibits"""
    units = {"B": 8, "K": 1, "M": 1024, "G": 1048576, "None": 0.001}
    size_input = re.search(r"^(\d+\.?\d*) ?([KMiG]*)(b)$", filesize, re.IGNORECASE)
    if not size_input:
        return False
    kb = float(size_input.group(1))
    kb *= units[size_input.group(2).upper() or "None"]
    kb *= units[size_input.group(3).upper()]
    return kb
