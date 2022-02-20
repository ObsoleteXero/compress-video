import subprocess
import sys
import re


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} input target_filesize(MB)")
        return

    # TODO: Check inputs
    # TODO: Filesize formats
    # TODO: Check OS
    filename = sys.argv[1]
    filesize = int(sys.argv[2])

    ffcmd = Compress(filename, filesize)
    ffcmd.x264()


class Compress:

    null = 'NUL' if sys.platform == 'win32' else '/dev/null'
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
        t_br = self.target_size * 1024 * 8 / self.length
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
                self.null
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
                "compressed_" + self.filename
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
