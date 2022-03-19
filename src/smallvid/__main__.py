import sys
from pathlib import Path

from smallvid.gui import CV_GUI
from smallvid.main import Compress
from smallvid import utils


def main():

    if not utils.check_ffmpeg():
        print("ffmpeg and/or ffprobe were not found; Program cannot continue.")
        sys.exit(1)

    # Launch CLI
    if len(sys.argv) in (3, 4):

        infile = Path(sys.argv[2])
        # Get size of input file and exit if it does not exist
        try:
            infile_size = infile.stat().st_size / 1024 * 8
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
            filesize = utils.parse_filesize(sys.argv[1])
            if not filesize or filesize >= infile_size:
                print("Invalid filesize")
                sys.exit(1)

        try:
            outfile = Path(sys.argv[3])
            if outfile.exists():
                while True:
                    ans = input(f"Output file {outfile} exists. Replace? (Y/N)\n")
                    if ans.upper in ("Y", "YES"):
                        break
                    else:
                        sys.exit(0)
        except IndexError:
            outfile = None

        # Start
        ffcmd = Compress(infile, filesize, outfile)
        ffcmd.x264()

    else:
        # Launch GUI
        print("Launching GUI")
        gui = CV_GUI()
        gui.mainloop()


if __name__ == "__main__":
    main()
