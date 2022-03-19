import re
import subprocess
from pathlib import Path

from smallvid import utils


class Compress:
    def __init__(self, filename: Path, target_size, outfile: Path = None) -> None:
        self.filename = filename
        self.target_size = target_size
        self.progress = ""
        if outfile:
            self.outfile = outfile.with_suffix(".mkv")
        else:
            self.outfile = filename.with_name(f"compressed_{filename.stem}.mkv")

    def get_info(self) -> None:
        """Get input file length and number of frames"""
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
        """Calculate target bitrate and store as valid ffmpeg argument"""
        t_br = self.target_size / self.length
        v_br = round(t_br * 0.75)
        a_br = round(t_br * 0.25)
        self.vbr = str(v_br) + "k"
        self.abr = str(a_br) + "k"

    def x264(self) -> None:

        self.get_info()
        self.calculate_bitrate()

        print(f"-- Compressing {self.filename.stem} --")

        pass_one = subprocess.Popen(
            [
                "ffmpeg",
                "-y",
                "-i",
                self.filename,
                "-c:v",
                "libx264",
                "-passlogfile",
                utils.temp,
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
                utils.devnull,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        while True:
            line = pass_one.stdout.readline().decode("utf8", errors="replace").strip()
            if line == "":
                self.progress = "First Pass: Complete"
                print(self.progress)
                break
            if line.startswith("frame="):
                progress = round(int(line.lstrip("frame=")) / self.frames * 100, 2)
                self.progress = f"First Pass: {progress:.2f}%"
                print(self.progress, end="\r")

        pass_two = subprocess.Popen(
            [
                "ffmpeg",
                "-y",
                "-i",
                self.filename,
                "-c:v",
                "libx264",
                "-passlogfile",
                utils.temp,
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
                self.outfile,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        while True:
            line = pass_two.stdout.readline().decode("utf8", errors="replace").strip()
            if line == "":
                self.progress = "Second Pass: Complete"
                print(self.progress)
                break
            if line.startswith("frame="):
                progress = round(int(line.lstrip("frame=")) / self.frames * 100, 2)
                self.progress = f"Second Pass: {progress:.2f}%"
                print(self.progress, end="\r")

        utils.clean_logs()
