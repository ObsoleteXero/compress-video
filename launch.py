import os
import re
import sys
from pathlib import Path

from gui import CV_GUI
from main import Compress


def main():

    # Launch CLI
    if len(sys.argv) in (3, 4):

        infile = Path(sys.argv[2])
        # Get size of input file and exit if it does not exist
        try:
            infile_size = os.path.getsize(infile) / 1024 * 8
        except OSError:
            print("File not found.")
            sys.exit(1)

        try:
            # Determine target filesize if given as a factor
            filesize = float(sys.argv[1])
            if 0 < filesize < 1:
                filesize *= infile_size
            else:
                raise ValueError
        except ValueError:
            # Determine target filesize if given directly
            filesize = parse_filesize(sys.argv[1])
            if not filesize or filesize >= infile_size:
                print("Invalid filesize")
                sys.exit(1)

        # Set output filename to default if not given
        try:
            outfile = Path(sys.argv[3]).with_suffix(".mkv")
        except IndexError:
            outfile = infile.with_name(f"compressed_{infile.name}").with_suffix(".mkv")

        # Start
        ffcmd = Compress(infile, filesize, outfile)
        print(f"-- Compressing {infile.name} --")
        ffcmd.x264()

    else:
        # Launch GUI
        print("Launching GUI")
        gui = CV_GUI()
        gui.mainloop()


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


if __name__ == "__main__":
    main()
