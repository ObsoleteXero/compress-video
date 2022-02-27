import os
import re
import sys
from pathlib import Path

from gui import CV_GUI
from main import Compress

def main():
    
    # Launch GUI
    if len(sys.argv) == 1:
        print("Lauching GUI")
        gui = CV_GUI()
        gui.mainloop()
    
    # Launch CLI
    elif len(sys.argv) == 3:
        filename = sys.argv[1]
        filesize = parse_filesize(sys.argv[2])
        if not filesize:
            print("Invalid filesize")
            sys.exit(2)
        try:
            if os.path.getsize(filename) / 1024 * 8 < filesize:
                print("Invalid filesize")
                sys.exit(1)
        except OSError:
            print("File not found")
            sys.exit(1)

        try:
            outfile = Path(sys.argv[3]).with_suffix('.mkv')
        except IndexError:
            outfile = Path(filename).with_suffix('.mkv')

        ffcmd = Compress(filename, filesize, outfile)
        print(f"-- Compressing {filename} --")
        ffcmd.x264()

    else:
        print(f"Usage: {sys.argv[0]} filename filesize")
        sys.exit(2)

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




if __name__ == '__main__':
    main()