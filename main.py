import subprocess
import sys


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
    def __init__(self, filename, target_size) -> None:
        self.filename = filename
        self.target_size = target_size

    def get_info(self) -> None:
        print("Gathering information...", end="\r")
        result = subprocess.run(
            [
                "ffprobe",
                "-count_frames",
                "-select_streams",
                "v:0",
                "-v",
                "error",
                "-show_entries",
                "stream=nb_read_frames : format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                self.filename,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        print("Gathering information... Complete")
        frames, length = result.stdout.strip().splitlines()
        self.frames = int(frames)
        self.length = float(length)

    def calculate_bitrate(self) -> None:
        v_br = round(self.target_size * 1024 * 8 / self.length - 128)
        self.br = str(v_br) + "k"

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
                self.br,
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
                "NUL",
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
                self.br,
                "-pass",
                "2",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                "-progress",
                "-",
                "-nostats",
                "-loglevel",
                "error",
                "compressed_" + self.filename,
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
