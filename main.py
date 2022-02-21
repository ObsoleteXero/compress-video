import os
import re
import sys
import subprocess


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} input_file target_filesize")
        sys.exit(2)

    # Check Inputs
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

    ffcmd = Compress(filename, filesize)
    ffcmd.x264()


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


class Compress:

    null = "NUL" if sys.platform == "win32" else "/dev/null"

    def __init__(self, filename, target_size) -> None:
        self.filename = filename
        self.target_size = target_size

    def get_info(self) -> None:
        result = subprocess.run(
            [
                "ffprobe",
                "-select_streams",
                "v:0",
                "-v",
                "error",
                "-show_entries",
                "stream=r_frame_rate : format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                self.filename,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        # Process output from ffprobe to get video length and approximate no. of frames
        fps_1, fps_2, self.length = (
            float(i) for i in re.split(r"[\n/]", result.stdout.strip())
        )
        self.frames = (fps_1 // fps_2 + (fps_1 % fps_2 > 0)) * self.length

    def calculate_bitrate(self) -> None:
        t_br = self.target_size / self.length
        v_br = round(t_br * 0.75)
        a_br = round(t_br * 0.25)
        self.vbr = str(v_br) + "k"
        self.abr = str(a_br) + "k"

    def x264(self) -> None:

        self.get_info()
        self.calculate_bitrate()

        pass_one = subprocess.Popen(
            [
                "ffmpeg",
                "-y",
                "-i",
                self.filename,
                "-c:v",
                "libx264",
                "-b:v",
                self.vbr,
                "-pass",
                "1",
                "-an",
                "-f",
                "null",
                "-progress",
                "-",
                "-nostats",
                "-loglevel",
                "error",
                self.null,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        while True:
            line = pass_one.stdout.readline().decode("utf8", errors="replace").strip()
            if line == "":
                print("First Pass: Complete")
                break
            if line.startswith("frame="):
                progress = round(int(line.lstrip("frame=")) / self.frames * 100, 2)
                print(f"First Pass: {progress:.2f}%", end="\r")

        pass_two = subprocess.Popen(
            [
                "ffmpeg",
                "-y",
                "-i",
                self.filename,
                "-c:v",
                "libx264",
                "-b:v",
                self.vbr,
                "-pass",
                "2",
                "-c:a",
                "aac",
                "-b:a",
                self.abr,
                "-progress",
                "-",
                "-nostats",
                "-loglevel",
                "error",
                "compressed_" + os.path.splitext(self.filename)[0] + ".mkv",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        while True:
            line = pass_two.stdout.readline().decode("utf8", errors="replace").strip()
            if line == "":
                print("Second Pass: Complete")
                break
            if line.startswith("frame="):
                progress = round(int(line.lstrip("frame=")) / self.frames * 100, 2)
                print(f"Second Pass: {progress:.2f}%", end="\r")

    def x265():
        # TODO: x265
        return


if __name__ == "__main__":
    main()
